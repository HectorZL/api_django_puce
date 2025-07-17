from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad_disponible', 'unidad_medida', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')
    ordering = ('categoria', 'nombre')