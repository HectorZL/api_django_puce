from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'menus'

urlpatterns = [
    # Lista de menús disponibles
    path('', views.menu_list, name='menu_list'),
    
    # Rutas para pedidos
    path('pedidos/crear/', views.create_order, name='create_order'),
    path('pedidos/<int:pk>/', views.order_detail, name='order_detail'),
    path('pedidos/<int:pk>/editar/', views.order_edit, name='order_edit'),  
    path('pedidos/', views.order_list, name='order_list'),
    path('pedidos/<int:pk>/cancelar/', views.cancel_order, name='cancel_order'),
    
    # API Endpoints
    path('api/menus/<int:menu_id>/', views.get_menu_details, name='menu_details'),
]
