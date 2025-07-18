from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from apps.clients.models import Cliente
from apps.clients.serializers import ClienteSerializer
from .models import UserProfile
from .forms import UserForm, UserProfileForm

def login_view(request):
    """Vista para el inicio de sesión"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Ensure the user has a profile
                from django.db import transaction
                with transaction.atomic():
                    profile, created = UserProfile.objects.get_or_create(user=user)
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('ui:dashboard')
        messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    return render(request, 'ui/login.html', {
        'form': form,
        'title': 'Iniciar Sesión'
    })

def register_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('ui:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'ui/register.html', {
        'form': form,
        'show_navbar': False
    })

@login_required
def dashboard_view(request):
    """Vista del panel de control principal"""
    return render(request, 'ui/dashboard.html')

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('ui:login')  # Usando el namespace 'ui:login' en lugar de solo 'login'

# Vistas CRUD para Clientes
@login_required
def clientes_list(request):
    """Vista para listar clientes"""
    clientes = Cliente.objects.all()
    return render(request, 'ui/clientes/list.html', {'clientes': clientes})

@login_required
def cliente_create(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        serializer = ClienteSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('clientes_list')
        messages.error(request, 'Error al crear el cliente')
    return render(request, 'ui/clientes/form.html', {'form': ClienteSerializer()})

@login_required
def cliente_update(request, pk):
    """Vista para actualizar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        serializer = ClienteSerializer(cliente, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('clientes_list')
        messages.error(request, 'Error al actualizar el cliente')
    return render(request, 'ui/clientes/form.html', {
        'form': ClienteSerializer(instance=cliente),
        'cliente': cliente
    })

@login_required
def cliente_delete(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente')
        return redirect('clientes_list')
    return render(request, 'ui/clientes/confirm_delete.html', {'cliente': cliente})

@login_required
def clientes_search(request):
    """API endpoint para buscar clientes"""
    query = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(identificacion__icontains=query) |
        Q(email__icontains=query)
    )
    serializer = ClienteSerializer(clientes, many=True)
    return JsonResponse(serializer.data, safe=False)

@login_required
def profile_view(request):
    """Vista para editar el perfil del usuario"""
    # Asegurarse de que el perfil exista
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('ui:profile')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'ui/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
