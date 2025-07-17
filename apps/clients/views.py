from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cliente, HistorialPedido
from .serializers import ClienteSerializer, HistorialPedidoSerializer, ClienteDetailSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite gestionar clientes.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombres', 'apellidos', 'identificacion', 'email']
    filterset_fields = ['tipo_identificacion', 'activo']
    ordering_fields = ['nombres', 'apellidos', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_serializer_class(self):
        
        if self.action == 'retrieve':
            return ClienteDetailSerializer
        return ClienteSerializer

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        
        cliente = self.get_object()
        historial = cliente.historial_pedidos.all().order_by('-fecha_pedido')
        page = self.paginate_queryset(historial)
        
        if page is not None:
            serializer = HistorialPedidoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = HistorialPedidoSerializer(historial, many=True)
        return Response(serializer.data)


class HistorialPedidoViewSet(viewsets.ModelViewSet):
    
    queryset = HistorialPedido.objects.all()
    serializer_class = HistorialPedidoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['cliente', 'estado']
    ordering_fields = ['fecha_pedido', 'monto_total']
    ordering = ['-fecha_pedido']

    def perform_create(self, serializer):
        
        if hasattr(self.request.user, 'id'):
            serializer.save(creado_por=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo "estado" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el estado sea válido
        estados_validos = dict(HistorialPedido.ESTADO_CHOICES).keys()
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.estado = nuevo_estado
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)
