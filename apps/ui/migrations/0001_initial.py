# Generated by Django 5.0 on 2025-07-17 19:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('direccion', models.TextField(blank=True, verbose_name='Dirección')),
                ('fecha_nacimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Foto de Perfil')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Usuario',
                'verbose_name_plural': 'Perfiles de Usuario',
            },
        ),
    ]
