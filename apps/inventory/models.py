from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

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
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre del artículo')
    descripcion = models.TextField(verbose_name='Descripción', blank=True)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría')
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario',
        validators=[MinValueValidator(0)]
    )
    cantidad_disponible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad disponible',
        validators=[MinValueValidator(0)]
    )
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA,
        default='UNIDAD',
        verbose_name='Unidad de medida'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Artículo de inventario'
        verbose_name_plural = 'Artículos de inventario'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()}) - {self.cantidad_disponible} {self.get_unidad_medida_display()}"