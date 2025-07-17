from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """Formulario para la información del perfil de usuario"""
    class Meta:
        model = UserProfile
        fields = ['telefono', 'direccion', 'fecha_nacimiento', 'avatar']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

class UserForm(UserChangeForm):
    """Formulario para la información básica del usuario"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo de contraseña del formulario
        self.fields.pop('password', None)
