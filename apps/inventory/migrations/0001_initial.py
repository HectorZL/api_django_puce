# Generated by Django 5.2.4 on 2025-07-17 20:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del artículo')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('categoria', models.CharField(choices=[('ENTRADA', 'Entrada'), ('PLATO_FUERTE', 'Plato Fuerte'), ('POSTRE', 'Postre'), ('BEBIDA', 'Bebida'), ('ACOMPANAMIENTO', 'Acompañamiento')], max_length=20, verbose_name='Categoría')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precio unitario')),
                ('cantidad_disponible', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Cantidad disponible')),
                ('unidad_medida', models.CharField(choices=[('UNIDAD', 'Unidad'), ('KG', 'Kilogramo'), ('GR', 'Gramo'), ('LT', 'Litro'), ('ML', 'Mililitro')], default='UNIDAD', max_length=10, verbose_name='Unidad de medida')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
            ],
            options={
                'verbose_name': 'Artículo de inventario',
                'verbose_name_plural': 'Artículos de inventario',
                'ordering': ['categoria', 'nombre'],
            },
        ),
    ]
