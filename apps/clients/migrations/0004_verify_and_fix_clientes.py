from django.db import migrations

def verify_and_fix_clientes(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Cliente = apps.get_model('clients', 'Cliente')
    
    # Get all users without a Cliente
    users_without_cliente = User.objects.filter(cliente__isnull=True)
    print(f"Found {users_without_cliente.count()} users without a Cliente record")
    
    for user in users_without_cliente:
        print(f"Creating Cliente for user: {user.username} ({user.email})")
        Cliente.objects.create(
            usuario=user,
            tipo_identificacion='C',
            identificacion=user.username or f"temp_{user.id}",
            nombres=user.first_name or 'Usuario',
            apellidos=user.last_name or 'Sin Nombre',
            email=user.email or f"user{user.id}@example.com"
        )

def reverse_func(apps, schema_editor):
    # No need to do anything when unapplying
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0003_update_existing_usuarios'),
    ]

    operations = [
        migrations.RunPython(verify_and_fix_clientes, reverse_func),
    ]
