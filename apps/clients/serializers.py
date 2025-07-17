from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Cliente, HistorialPedido

User = get_user_model()

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Cliente.
    """
    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_identificacion', 'identificacion',
            'nombres', 'apellidos',
            'telefono', 'email', 'direccion',
            'fecha_registro', 'activo'
        ]
        read_only_fields = ['fecha_registro']


class HistorialPedidoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo HistorialPedido.
    Incluye información básica del cliente relacionado.
    """
    cliente_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = HistorialPedido
        fields = [
            'id', 'cliente', 'cliente_info',
            'fecha_pedido', 'descripcion',
            'monto_total', 'estado', 'estado_display',
            'notas'
        ]
        read_only_fields = ['fecha_pedido']
    
    def get_cliente_info(self, obj):
        
        return {
            'nombre_completo': f"{obj.cliente.nombres} {obj.cliente.apellidos}",
            'identificacion': obj.cliente.identificacion,
            'email': obj.cliente.email
        }


class ClienteDetailSerializer(ClienteSerializer):
    
    pedidos = serializers.SerializerMethodField()
    
    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['pedidos']
    
    def get_pedidos(self, obj):
        
        pedidos = obj.historial_pedidos.all().order_by('-fecha_pedido')
        return HistorialPedidoSerializer(pedidos, many=True).data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        # Eliminamos password2 ya que no es un campo del modelo
        validated_data.pop('password2', None)
        
        # Creamos el usuario
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Establecemos la contraseña (se encripta automáticamente)
        user.set_password(validated_data['password'])
        user.save()
        
        return user
