from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importar vistas de autenticación
from apps.clients.views import RegisterView

# Importaciones condicionales para desarrollo
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # URLs de la aplicación UI (incluye autenticación en /auth/)
    path('', include(('apps.ui.urls', 'ui'), namespace='ui')),
    
    # URLs de la aplicación de menús y pedidos
    path('menus/', include(('apps.menus.urls', 'menus'), namespace='menus')),
    
    # API URLs
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/clients/', include('apps.clients.urls')),
]

# Añadir URLs de drf_spectacular si está disponible
if SPECTACULAR_AVAILABLE:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]

# Debug Toolbar - Solo en desarrollo
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass

# Servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
