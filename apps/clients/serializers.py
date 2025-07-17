from rest_framework import serializers
from .models import Cliente, HistorialPedido

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
