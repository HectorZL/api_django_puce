from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.inventory.models import Inventory
from apps.clients.models import Cliente


class Menu(models.Model):
    """
    Modelo para gestionar los menús del servicio de catering.
    Un menú puede contener múltiples artículos del inventario.
    """
    TIPO_MENU = [
        ('DESAYUNO', 'Desayuno'),
        ('ALMUERZO', 'Almuerzo'),
        ('MERIENDA', 'Merienda'),
        ('CENA', 'Cena'),
        ('ESPECIAL', 'Menú Especial'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre del menú'))
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    tipo_menu = models.CharField(
        max_length=20,
        choices=TIPO_MENU,
        verbose_name=_('Tipo de menú')
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Precio'),
        validators=[MinValueValidator(0)]
    )
    items = models.ManyToManyField(
        Inventory,
        through='MenuItem',
        through_fields=('menu', 'inventory_item'),
        verbose_name=_('Artículos del menú'),
        related_name='menus'
    )
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última actualización'))
    
    class Meta:
        verbose_name = _('Menú')
        verbose_name_plural = _('Menús')
        ordering = ['tipo_menu', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_menu_display()}) - ${self.precio}"


class MenuItem(models.Model):
    """
    Modelo intermedio para la relación muchos a muchos entre Menu e Inventory.
    Permite almacenar información adicional sobre cada artículo en el menú,
    como la cantidad necesaria.
    """
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        verbose_name=_('Menú')
    )
    inventory_item = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        verbose_name=_('Artículo de inventario')
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Cantidad requerida'),
        validators=[MinValueValidator(0.01)]
    )
    notas = models.TextField(verbose_name=_('Notas adicionales'), blank=True)
    
    class Meta:
        verbose_name = _('Artículo del menú')
        verbose_name_plural = _('Artículos del menú')
        unique_together = ('menu', 'inventory_item')
    
    def __str__(self):
        return f"{self.inventory_item.nombre} ({self.cantidad} {self.inventory_item.get_unidad_medida_display()}) - {self.menu.nombre}"


class Order(models.Model):
    """
    Modelo para gestionar los pedidos de catering.
    Un pedido puede contener múltiples ítems del menú con sus respectivas cantidades.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('EN_PROCESO', 'En Proceso'),
        ('EN_CAMINO', 'En Camino'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name=_('Cliente')
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de creación'))
    fecha_entrega = models.DateTimeField(verbose_name=_('Fecha de entrega'))
    direccion_entrega = models.TextField(verbose_name=_('Dirección de entrega'))
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE',
        verbose_name=_('Estado del pedido')
    )
    notas = models.TextField(verbose_name=_('Notas adicionales'), blank=True)
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total del pedido')
    )
    
    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.nombres} - {self.get_estado_display()}'
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los subtotales de los ítems"""
        return sum(item.subtotal() for item in self.items.all())
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo si es un nuevo pedido
            self.total = self.calcular_total()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Modelo para los ítems individuales dentro de un pedido.
    Relaciona un menú con una cantidad específica en un pedido.
    """
    pedido = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Pedido')
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name=_('Menú')
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Cantidad')
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Precio unitario')
    )
    notas = models.TextField(verbose_name=_('Notas'), blank=True)
    
    class Meta:
        verbose_name = _('Ítem de pedido')
        verbose_name_plural = _('Ítems de pedido')
    
    def __str__(self):
        return f'{self.cantidad}x {self.menu.nombre} - ${self.precio_unitario} c/u'
    
    def subtotal(self):
        """Calcula el subtotal de este ítem"""
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        # Al guardar, actualizamos el precio unitario con el precio actual del menú
        if not self.precio_unitario:
            self.precio_unitario = self.menu.precio
        super().save(*args, **kwargs)
        # Actualizamos el total del pedido
        self.pedido.total = self.pedido.calcular_total()
        self.pedido.save(update_fields=['total'])


class OrderHistory(models.Model):
    """
    Tracks changes to order status and important updates
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='history_entries',
        verbose_name=_('pedido')
    )
    
    STATUS_CHOICES = Order.ESTADOS
    
    old_status = models.CharField(
        _('estado anterior'),
        max_length=20,
        choices=STATUS_CHOICES,
        blank=True,
        null=True
    )
    
    new_status = models.CharField(
        _('nuevo estado'),
        max_length=20,
        choices=STATUS_CHOICES
    )
    
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('cambiado por')
    )
    
    notes = models.TextField(
        _('notas'),
        blank=True,
        help_text=_('Información adicional sobre este cambio de estado')
    )
    
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('historial de pedido')
        verbose_name_plural = _('historial de pedidos')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order} - {self.old_status} → {self.new_status} - {self.created_at}"