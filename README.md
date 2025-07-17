# 🍱 Catering Automatizado – Backend Django

## Stack
- Python 3.11
- Django 5.0 + Django REST Framework (DRF)
- Swagger-UI (drf-spectacular)

## Instalación rápida

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-org/catering-backend.git
cd catering-backend
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Aplicar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Iniciar servidor de desarrollo:
```bash
python manage.py runserver
```

## Estructura de carpetas
```
catering_api/
├── config/               # Configuración principal
├── apps/
│   ├── clients/         # CRUD Clientes
│   ├── orders/          # CRUD Pedidos
│   ├── menus/           # CRUD Menús
│   ├── inventory/       # Gestión de inventario
│   └── analytics/       # Métricas y análisis
├── docs/                # Documentación
└── tests/              # Pruebas automatizadas
```

## API Documentation

La documentación interactiva de la API está disponible en:
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/

## Ejecución de pruebas

```bash
pytest
```

## Despliegue

El proyecto incluye configuración para Docker. Para desplegar:

```bash
docker-compose up --build
```

## Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## Contacto

Tu Nombre - [@tuusuario](https://twitter.com/tuusuario) - email@ejemplo.com

Enlace del proyecto: [https://github.com/tuusuario/catering-backend](https://github.com/tuusuario/catering-backend)
