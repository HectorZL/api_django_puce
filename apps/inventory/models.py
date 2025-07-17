from django.db import models

from apps import inventory


class Menu(models.Model):
    """
    Modelo para almacenar la información sobre los menus del servicio de catering.
    """

    MenuItem = models.JSONField()
    amount = models.IntegerField(verbose_name="Cantidad", blank=False)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.MenuItem} ({self.amount})"


class Inventory(models.Model):
    """
    Modelo para gestionar los artículos del inventario que pueden incluirse en los menús.
    """
    CATEGORY_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('PLATO_FUERTE', 'Plato Fuerte'),
        ('POSTRE', 'Postre'),
        ('BEBIDA', 'Bebida'),
        ('ACOMPANAMIENTO', 'Acompañamiento'),
    ]
    
    UNIDAD_MEDIDA = [
        ('UNIDAD', 'Unidad'),
        ('KG', 'Kilogramo'),
        ('GR', 'Gramo'),
        ('LT', 'Litro'),
        ('ML', 'Mililitro'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre del artículo'))
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Categoría')
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Precio unitario'),
        validators=[MinValueValidator(0)]
    )
    cantidad_disponible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Cantidad disponible'),
        validators=[MinValueValidator(0)]
    )
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA,
        default='UNIDAD',
        verbose_name=_('Unidad de medida')
    )
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última actualización'))
    
    class Meta:
        verbose_name = _('Artículo de inventario')
        verbose_name_plural = _('Artículos de inventario')
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()}) - {self.cantidad_disponible} {self.get_unidad_medida_display()}"