from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Inventory
from .serializers import InventorySerializer, InventoryUpdateSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows inventory items to be viewed or edited.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio', 'cantidad_disponible']
    ordering = ['categoria', 'nombre']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action in ['update', 'partial_update']:
            return InventoryUpdateSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """
        Custom action to update inventory stock
        """
        inventory = self.get_object()
        amount = request.data.get('amount', 0)
        action_type = request.data.get('action', 'add')  # 'add' or 'subtract'
        
        try:
            amount = float(amount)
            if action_type == 'add':
                inventory.cantidad_disponible += amount
            elif action_type == 'subtract':
                if inventory.cantidad_disponible < amount:
                    return Response(
                        {'error': 'Insufficient stock'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                inventory.cantidad_disponible -= amount
            inventory.save()
            return Response(InventorySerializer(inventory).data)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
