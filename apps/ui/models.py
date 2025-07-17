from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Modelo para almacenar información adicional del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Foto de Perfil')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f'Perfil de {self.user.username}'

# Señal para crear automáticamente el perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Señal para guardar el perfil cuando se guarda el usuario
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
