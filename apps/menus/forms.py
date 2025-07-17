from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory

from .models import Menu, Order, OrderItem


class OrderItemForm(forms.ModelForm):
    """Formulario para los ítems del pedido"""
    menu = forms.ModelChoiceField(
        queryset=Menu.objects.filter(activo=True),
        label=_('Menú'),
        widget=forms.Select(attrs={
            'class': 'form-select menu-select',
            'data-live-search': 'true',
        })
    )
    
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label=_('Cantidad'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control cantidad',
            'min': '1',
        })
    )
    
    class Meta:
        model = OrderItem
        fields = ['menu', 'cantidad', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Especificaciones adicionales...')
            }),
        }


class OrderForm(forms.ModelForm):
    """Formulario principal para crear/editar un pedido"""
    class Meta:
        model = Order
        fields = ['fecha_entrega', 'direccion_entrega', 'notas']
        widgets = {
            'fecha_entrega': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'direccion_entrega': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Dirección completa de entrega')
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Instrucciones especiales o notas adicionales')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if self.cliente and not self.instance.pk:
            self.fields['direccion_entrega'].initial = self.cliente.direccion


# Creamos un formset para los ítems del pedido
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
