

# Esta línea es importante para que Django reconozca esta carpeta como un paquete de Python
# y pueda encontrar los modelos, vistas, etc.

def get_version():
    """
    Retorna la versión actual del módulo de clientes.
    """
    return "1.0.0"

__version__ = get_version()
