from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importaciones condicionales para desarrollo
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # URLs de la aplicación UI
    path('', include('apps.ui.urls')),
    
    # API URLs - Aquí incluiremos las URLs de las aplicaciones
    # path('api/', include('tu_app.urls')),
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
