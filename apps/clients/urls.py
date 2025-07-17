from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuración del router para las vistas de la API
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'pedidos', views.HistorialPedidoViewSet, basename='pedido')

app_name = 'clients'

# Las URLs de la API estarán disponibles en /api/v1/clientes/ y /api/v1/pedidos/
urlpatterns = [
    path('', include(router.urls)),
]
