from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Cliente(models.Model):
    """
    Modelo para almacenar la información de los clientes del servicio de catering.
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente',
        verbose_name='Usuario',
        null=True,  # Make it nullable for migration
        blank=True  # Allow blank in forms
    )
    
    TIPO_IDENTIFICACION = [
        ('C', 'Cédula'),
        ('R', 'RUC'),
        ('P', 'Pasaporte')
    ]

    tipo_identificacion = models.CharField(
        max_length=1,
        choices=TIPO_IDENTIFICACION,
        default='C',
        verbose_name='Tipo de Identificación'
    )
    
    identificacion = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Identificación'
    )
    
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe tener el formato: '+593999999999'"
    )
    telefono = models.CharField(
        validators=[telefono_regex],
        max_length=17,
        verbose_name='Teléfono',
        blank=True
    )
    
    email = models.EmailField(verbose_name='Correo Electrónico', unique=True)
    direccion = models.TextField(verbose_name='Dirección', blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    activo = models.BooleanField(default=True, verbose_name='Cliente Activo')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create a Cliente for the given user."""
        try:
            return user.cliente
        except Cliente.DoesNotExist:
            # Create a new Cliente for the user
            return cls.objects.create(
                usuario=user,
                email=user.email,
                nombres=user.first_name or 'Cliente',
                apellidos=user.last_name or 'Nuevo',
                identificacion=f"USER-{user.id}",
                telefono='',
                direccion='',
            )


class HistorialPedido(models.Model):
    """
    Modelo para almacenar el historial de pedidos de los clientes.
    """
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('E', 'En Proceso'),
        ('C', 'Completado'),
        ('A', 'Anulado')
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='historial_pedidos',
        verbose_name='Cliente'
    )
    
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Pedido')
    descripcion = models.TextField(verbose_name='Descripción del Pedido')
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto Total',
        default=0.00
    )
    estado = models.CharField(
        max_length=1,
        choices=ESTADO_CHOICES,
        default='P',
        verbose_name='Estado del Pedido'
    )
    
    notas = models.TextField(verbose_name='Notas Adicionales', blank=True)
    
    class Meta:
        verbose_name = 'Historial de Pedido'
        verbose_name_plural = 'Historial de Pedidos'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} - {self.get_estado_display()}"
