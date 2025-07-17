from django.urls import path
from . import views

app_name = 'ui'

urlpatterns = [
    # Authentication pages
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Profile
    path('perfil/', views.profile_view, name='profile'),
    
    # Client CRUD
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
    path('clientes/buscar/', views.clientes_search, name='clientes_search'),
]
