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
    search_fields = ('menu__nombre', 'inventory_item__nombre')