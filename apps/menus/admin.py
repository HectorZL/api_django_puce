from django.contrib import admin
from .models import Menu, MenuItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    raw_id_fields = ('inventory_item',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_menu', 'precio', 'activo')
    list_filter = ('tipo_menu', 'activo')
    search_fields = ('nombre', 'descripcion')
    inlines = [MenuItemInline]
    
    # Remove the items field from the form since we're using inline
    exclude = ('items',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('menu', 'inventory_item', 'cantidad')
    list_filter = ('menu',)
    search_fields = ('menu__nombre', 'inventory_item__nombre')from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import F, Sum

from .models import Menu, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('menu', 'cantidad', 'precio_unitario', 'notas', 'subtotal')
    autocomplete_fields = ('menu',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente_info', 'fecha_entrega', 'estado_badge', 
        'total_formatted', 'fecha_creacion', 'actions_column'
    )
    list_filter = ('estado', 'fecha_creacion', 'fecha_entrega')
    search_fields = (
        'id', 'cliente__usuario__first_name', 'cliente__usuario__last_name',
        'cliente__usuario__email', 'direccion_entrega', 'notas'
    )
    list_select_related = ('cliente__usuario',)
    readonly_fields = ('fecha_creacion', 'total')
    date_hierarchy = 'fecha_creacion'
    actions = ['marcar_como_confirmado', 'marcar_como_en_proceso', 'marcar_como_en_camino', 
               'marcar_como_entregado', 'cancelar_pedidos', 'generar_factura_pdf']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': (('cliente', 'estado'), 'fecha_entrega', 'direccion_entrega', 'notas')
        }),
        ('Totales', {
            'classes': ('collapse',),
            'fields': (('total',),)
        }),
        ('Auditoría', {
            'classes': ('collapse',),
            'fields': (('fecha_creacion',),)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_sum=Sum(F('items__cantidad') * F('items__precio_unitario'))
        )

    def estado_badge(self, obj):
        estado_classes = {
            'PENDIENTE': 'bg-warning',
            'CONFIRMADO': 'bg-primary',
            'EN_PROCESO': 'bg-info',
            'EN_CAMINO': 'bg-info',
            'ENTREGADO': 'bg-success',
            'CANCELADO': 'bg-danger',
        }
        return format_html(
            '<span class="badge {} text-white">{}</span>',
            estado_classes.get(obj.estado, 'bg-secondary'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'

    def cliente_info(self, obj):
        return f"{obj.cliente.nombre_completo} - {obj.cliente.telefono or 'Sin teléfono'}"
    cliente_info.short_description = 'Cliente'
    cliente_info.admin_order_field = 'cliente__usuario__first_name'

    def total_formatted(self, obj):
        return f"${obj.total:,.2f}" if obj.total else "$0.00"
    total_formatted.short_description = 'Total'
    total_formatted.admin_order_field = 'total_sum'

    def actions_column(self, obj):
        links = []
        if obj.estado in ['PENDIENTE', 'CONFIRMADO']:
            cancel_url = reverse('admin:menus_order_cancel', args=[obj.pk])
            links.append(f'<a href="{cancel_url}" class="button">Cancelar</a>')
        
        if obj.estado == 'PENDIENTE':
            confirm_url = reverse('admin:menus_order_confirm', args=[obj.pk])
            links.append(f'<a href="{confirm_url}" class="button">Confirmar</a>')
        
        if obj.estado == 'CONFIRMADO':
            process_url = reverse('admin:menus_order_process', args=[obj.pk])
            links.append(f'<a href="{process_url}" class="button">En Proceso</a>')
        
        if obj.estado == 'EN_PROCESO':
            ship_url = reverse('admin:menus_order_ship', args=[obj.pk])
            links.append(f'<a href="{ship_url}" class="button">Enviar</a>')
        
        if obj.estado == 'EN_CAMINO':
            deliver_url = reverse('admin:menus_order_deliver', args=[obj.pk])
            links.append(f'<a href="{deliver_url}" class="button">Entregado</a>')
        
        return format_html(' '.join(links))
    actions_column.short_description = 'Acciones'
    actions_column.allow_tags = True

    # Custom Actions
    @admin.action(description='Marcar como CONFIRMADO')
    def marcar_como_confirmado(self, request, queryset):
        updated = queryset.filter(estado='PENDIENTE').update(estado='CONFIRMADO', fecha_actualizacion=timezone.now())
        self.message_user(request, ngettext(
            '%d pedido fue marcado como confirmado.',
            '%d pedidos fueron marcados como confirmados.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Marcar como EN PROCESO')
    def marcar_como_en_proceso(self, request, queryset):
        updated = queryset.filter(estado='CONFIRMADO').update(estado='EN_PROCESO', fecha_actualizacion=timezone.now())
        self.message_user(request, ngettext(
            '%d pedido fue marcado como en proceso.',
            '%d pedidos fueron marcados como en proceso.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Marcar como EN CAMINO')
    def marcar_como_en_camino(self, request, queryset):
        updated = queryset.filter(estado='EN_PROCESO').update(estado='EN_CAMINO', fecha_actualizacion=timezone.now())
        self.message_user(request, ngettext(
            '%d pedido fue marcado como enviado.',
            '%d pedidos fueron marcados como enviados.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Marcar como ENTREGADO')
    def marcar_como_entregado(self, request, queryset):
        updated = queryset.filter(estado='EN_CAMINO').update(estado='ENTREGADO', fecha_actualizacion=timezone.now())
        self.message_user(request, ngettext(
            '%d pedido fue marcado como entregado.',
            '%d pedidos fueron marcados como entregados.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Cancelar pedidos seleccionados')
    def cancelar_pedidos(self, request, queryset):
        if 'apply' in request.POST:
            motivo = request.POST.get('motivo_cancelacion', 'Sin motivo especificado')
            updated = queryset.exclude(estado__in=['CANCELADO', 'ENTREGADO']).update(
                estado='CANCELADO',
                fecha_cancelacion=timezone.now(),
                motivo_cancelacion=motivo,
                fecha_actualizacion=timezone.now()
            )
            self.message_user(request, ngettext(
                '%d pedido fue cancelado.',
                '%d pedidos fueron cancelados.',
                updated,
            ) % updated, messages.SUCCESS)
            return None

        return self.message_user(
            request,
            '¿Está seguro de que desea cancelar los pedidos seleccionados?',
            extra_tags='confirmation',
            fail_silently=True,
        )

    # Custom URLs for order actions
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:order_id>/confirmar/',
                self.admin_site.admin_view(self.confirm_order),
                name='menus_order_confirm',
            ),
            path(
                '<int:order_id>/cancelar/',
                self.admin_site.admin_view(self.cancel_order),
                name='menus_order_cancel',
            ),
            path(
                '<int:order_id>/procesar/',
                self.admin_site.admin_view(self.process_order),
                name='menus_order_process',
            ),
            path(
                '<int:order_id>/enviar/',
                self.admin_site.admin_view(self.ship_order),
                name='menus_order_ship',
            ),
            path(
                '<int:order_id>/entregar/',
                self.admin_site.admin_view(self.deliver_order),
                name='menus_order_deliver',
            ),
        ]
        return custom_urls + urls

    def confirm_order(self, request, order_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        
        order = self.get_object(request, order_id)
        if order and order.estado == 'PENDIENTE':
            order.estado = 'CONFIRMADO'
            order.fecha_actualizacion = timezone.now()
            order.save()
            messages.success(request, _('El pedido ha sido confirmado.'))
        return redirect('admin:menus_order_changelist')

    def cancel_order(self, request, order_id):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        
        order = self.get_object(request, order_id)
        if request.method == 'POST':
            motivo = request.POST.get('motivo_cancelacion', 'Sin motivo especificado')
            order.estado = 'CANCELADO'
            order.fecha_cancelacion = timezone.now()
            order.motivo_cancelacion = motivo
            order.fecha_actualizacion = timezone.now()
            order.save()
            messages.success(request, _('El pedido ha sido cancelado.'))
            return redirect('admin:menus_order_changelist')
            
        return render(request, 'admin/orders/cancel_order.html', {
            'order': order,
            'title': _('Cancelar Pedido'),
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        })

    def process_order(self, request, order_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        
        order = self.get_object(request, order_id)
        if order and order.estado == 'CONFIRMADO':
            order.estado = 'EN_PROCESO'
            order.fecha_actualizacion = timezone.now()
            order.save()
            messages.success(request, _('El pedido está en proceso.'))
        return redirect('admin:menus_order_changelist')

    def ship_order(self, request, order_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        
        order = self.get_object(request, order_id)
        if order and order.estado == 'EN_PROCESO':
            order.estado = 'EN_CAMINO'
            order.fecha_actualizacion = timezone.now()
            order.save()
            messages.success(request, _('El pedido ha sido enviado.'))
        return redirect('admin:menus_order_changelist')

    def deliver_order(self, request, order_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.utils.translation import gettext as _
        
        order = self.get_object(request, order_id)
        if order and order.estado == 'EN_CAMINO':
            order.estado = 'ENTREGADO'
            order.fecha_actualizacion = timezone.now()
            order.save()
            messages.success(request, _('El pedido ha sido marcado como entregado.'))
        return redirect('admin:menus_order_changelist')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_menu', 'precio', 'activo', 'items_count')
    list_filter = ('tipo_menu', 'activo')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'tipo_menu', 'precio', 'activo')
        }),
        ('Auditoría', {
            'classes': ('collapse',),
            'fields': (('fecha_creacion', 'fecha_actualizacion'),)
        }),
    )
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'menu_nombre', 'cantidad', 'precio_unitario', 'subtotal')
    list_select_related = ('pedido', 'menu')
    search_fields = ('pedido__id', 'menu__nombre')
    autocomplete_fields = ('pedido', 'menu')
    readonly_fields = ('subtotal',)

    def pedido_link(self, obj):
        url = reverse('admin:menus_order_change', args=[obj.pedido.id])
        return format_html('<a href="{}">Pedido #{}</a>', url, obj.pedido.id)
    pedido_link.short_description = 'Pedido'
    pedido_link.admin_order_field = 'pedido__id'

    def menu_nombre(self, obj):
        return obj.menu.nombre
    menu_nombre.short_description = 'Menú'
    menu_nombre.admin_order_field = 'menu__nombre'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            subtotal_calc=F('cantidad') * F('precio_unitario')
        )

    def subtotal(self, obj):
        return f"${obj.subtotal_calc:,.2f}" if hasattr(obj, 'subtotal_calc') else "$0.00"
    subtotal.short_description = 'Subtotal'
    subtotal.admin_order_field = 'subtotal_calc'
