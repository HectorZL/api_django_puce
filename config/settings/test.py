from .base import *

# Configuración específica para pruebas

# Usar SQLite para pruebas
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Usar base de datos en memoria para pruebas
    }
}

# Configuración para acelerar las pruebas
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar autenticación para las pruebas
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = []

# Desactivar logs durante las pruebas
import logging
logging.disable(logging.CRITICAL)
