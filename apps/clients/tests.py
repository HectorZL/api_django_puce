import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.clients.models import Cliente, HistorialPedido

User = get_user_model()

class ClienteAPITestCase(APITestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Datos de prueba para un cliente
        self.cliente_data = {
            'tipo_identificacion': 'C',
            'identificacion': '1723456789',
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan.perez@example.com',
            'telefono': '+593987654321',
            'direccion': 'Av. Principal 123',
            'activo': True
        }
        # URL base para las pruebas
        self.list_url = reverse('cliente-list')

    def test_crear_cliente(self):
        """Test para crear un nuevo cliente"""
        response = self.client.post(self.list_url, self.cliente_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Cliente.objects.get().nombres, 'Juan')

    def test_listar_clientes(self):
        """Test para listar clientes"""
        # Crear un cliente de prueba
        Cliente.objects.create(**self.cliente_data)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombres'], 'Juan')

    def test_obtener_cliente_por_id(self):
        """Test para obtener un cliente por su ID"""
        cliente = Cliente.objects.create(**self.cliente_data)
        detail_url = reverse('cliente-detail', args=[cliente.id])
        
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombres'], 'Juan')

    def test_actualizar_cliente(self):
        """Test para actualizar un cliente existente"""
        cliente = Cliente.objects.create(**self.cliente_data)
        detail_url = reverse('cliente-detail', args=[cliente.id])
        
        datos_actualizados = self.cliente_data.copy()
        datos_actualizados['nombres'] = 'Juan Carlos'
        
        response = self.client.put(detail_url, datos_actualizados, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombres'], 'Juan Carlos')

    def test_eliminar_cliente(self):
        """Test para eliminar un cliente"""
        cliente = Cliente.objects.create(**self.cliente_data)
        detail_url = reverse('cliente-detail', args=[cliente.id])
        
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cliente.objects.count(), 0)
