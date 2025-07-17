from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.inventory.models import Inventory


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