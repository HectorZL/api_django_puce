from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from .models import Menu, Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import PermissionRequiredMixin

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'menus/order_form.html'
    context_object_name = 'order'
    
    def test_func(self):
        order = self.get_object()
        # Only allow editing if order is pending and belongs to the user
        return order.estado == 'PENDIENTE' and order.cliente.usuario == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['orderitem_formset'] = OrderItemFormSet(self.request.POST, instance=self.object, prefix='orderitem')
        else:
            context['orderitem_formset'] = OrderItemFormSet(instance=self.object, prefix='orderitem')
        
        # Add menu choices to the context for the template
        context['menus'] = Menu.objects.filter(activo=True)
        context['editing'] = True
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        orderitem_formset = context['orderitem_formset']
        
        if orderitem_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.fecha_actualizacion = timezone.now()
            self.object.save()
            
            # Save the formset
            order_items = orderitem_formset.save(commit=False)
            
            # Delete any removed items
            for obj in orderitem_formset.deleted_objects:
                if obj.pk:
                    obj.delete()
            
            # Save or update order items
            for item in order_items:
                item.pedido = self.object
                item.save()
            
            # Update order totals
            self.object.actualizar_totales()
            
            messages.success(
                self.request, 
                _('Pedido actualizado exitosamente.')
            )
            
            # Send notification email
            try:
                send_order_status_notification(
                    self.request, 
                    self.object, 
                    status_changed=False
                )
            except Exception as e:
                logger.error(f"Error sending order update email: {e}")
            
            return redirect('menus:order_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

@login_required
def menu_list(request):
    """Vista para listar los menús disponibles"""
    print("\n=== MENU LIST VIEW DEBUG ===")
    print(f"User: {request.user}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    print(f"Is staff: {request.user.is_staff}")
    
    menus = Menu.objects.filter(activo=True).select_related()
    print(f"Found {len(menus)} active menus")
    
    context = {
        'menus': menus,
        'title': _('Menús Disponibles'),
        'user': request.user,
        'debug': {
            'user': str(request.user),
            'is_authenticated': request.user.is_authenticated,
            'is_staff': request.user.is_staff,
            'menu_count': len(menus)
        }
    }
    
    return render(request, 'menus/menu_list.html', context)


@login_required
def create_order(request):
    """Vista para crear un nuevo pedido"""
    # Asumimos que el cliente está relacionado con el usuario actual
    cliente = request.user.cliente
    
    if request.method == 'POST':
        form = OrderForm(request.POST, cliente=cliente)
        formset = OrderItemFormSet(request.POST, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.cliente = cliente
                order.save()
                
                # Guardar los ítems del pedido
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.pedido = order
                    instance.precio_unitario = instance.menu.precio
                    instance.save()
                
                # Eliminar ítems marcados para borrar
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Actualizar el total del pedido
                order.total = sum(item.subtotal() for item in order.items.all())
                order.save()
                
                messages.success(request, _('¡Pedido creado exitosamente!'))
                return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm(cliente=cliente, initial={
            'fecha_entrega': timezone.now() + timezone.timedelta(days=1)
        })
        formset = OrderItemFormSet(prefix='items')
    
    return render(request, 'menus/order_form.html', {
        'form': form,
        'formset': formset,
        'title': _('Nuevo Pedido')
    })


@login_required
def order_detail(request, pk):
    """
    Display order details and tracking information
    """
    order = get_object_or_404(Order.objects.select_related('cliente__usuario'), pk=pk)
    
    # Check if user has permission to view this order
    if not request.user.is_staff and order.cliente.usuario != request.user:
        messages.error(request, _('No tienes permiso para ver este pedido.'))
        return redirect('menus:order_list')
    
    order_items = order.items.select_related('menu')
    
    # Get the estimated delivery time (if applicable)
    estimated_delivery = None
    if order.estado in ['CONFIRMADO', 'EN_PROCESO', 'EN_CAMINO']:
        # Add 1 hour for preparation time
        estimated_delivery = order.fecha_entrega
    
    # Get delivery status information
    delivery_status = {
        'is_delivered': order.estado == 'ENTREGADO',
        'is_cancelled': order.estado == 'CANCELADO',
        'is_in_transit': order.estado == 'EN_CAMINO',
        'is_being_prepared': order.estado in ['CONFIRMADO', 'EN_PROCESO'],
        'is_pending': order.estado == 'PENDIENTE',
    }
    
    # Get status timeline
    status_timeline = order.history_entries.all().order_by('created_at')
    
    context = {
        'order': order,
        'order_items': order_items,
        'estimated_delivery': estimated_delivery,
        'delivery_status': delivery_status,
        'status_timeline': status_timeline,
        'title': _('Detalles del Pedido #{}').format(order.id)
    }
    
    return render(request, 'menus/order_detail.html', context)


@login_required
def order_list(request):
    """Vista para listar los pedidos del usuario actual"""
    if request.user.is_staff:
        # Admin can see all orders
        orders = Order.objects.all().select_related('cliente__usuario')
    else:
        # Regular users can only see their own orders
        orders = Order.objects.filter(
            cliente__usuario=request.user
        ).select_related('cliente__usuario')
    
    return render(request, 'menus/order_list.html', {
        'orders': orders,
        'title': _('Mis Pedidos') if not request.user.is_staff else _('Todos los Pedidos')
    })


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """Vista para cancelar un pedido"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if user has permission to cancel this order
    if not request.user.is_staff and order.cliente.usuario != request.user:
        messages.error(request, _('No tienes permiso para cancelar este pedido.'))
        return redirect('menus:order_list')
    
    # Only allow cancelling pending or confirmed orders
    if order.estado not in ['PENDIENTE', 'CONFIRMADO']:
        messages.error(
            request, 
            _('Solo se pueden cancelar pedidos que estén pendientes o confirmados.')
        )
        return redirect('menus:order_detail', pk=order.id)
    
    if request.method == 'POST':
        order.estado = 'CANCELADO'
        order.fecha_cancelacion = timezone.now()
        order.save()
        
        messages.success(request, _('Pedido cancelado exitosamente.'))
        return redirect('menus:order_list')
    
    return render(request, 'menus/order_confirm_cancel.html', {
        'order': order,
        'title': _('Confirmar Cancelación')
    })

@login_required
def order_edit(request, pk):
    """Edit an existing order"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check if user has permission to edit this order
    if not request.user.is_staff and order.cliente.usuario != request.user:
        messages.error(request, _('No tienes permiso para editar este pedido.'))
        return redirect('menus:order_list')
    
    # Only allow editing pending orders
    if order.estado != 'PENDIENTE':
        messages.error(
            request, 
            _('Solo se pueden editar pedidos que estén en estado pendiente.')
        )
        return redirect('menus:order_detail', pk=order.id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.fecha_actualizacion = timezone.now()
                order.save()
                formset.save()
                
                # Update order totals
                order.actualizar_totales()
                
                messages.success(request, _('Pedido actualizado exitosamente.'))
                return redirect('menus:order_detail', pk=order.id)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    
    return render(request, 'menus/order_form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': _('Editar Pedido')
    })

def get_menu_details(request, menu_id):
    """Endpoint para obtener detalles de un menú (usado con AJAX)"""
    menu = get_object_or_404(Menu, id=menu_id, activo=True)
    return JsonResponse({
        'id': menu.id,
        'nombre': menu.nombre,
        'descripcion': menu.descripcion,
        'precio': str(menu.precio),
        'tipo_menu': menu.get_tipo_menu_display(),
    })
