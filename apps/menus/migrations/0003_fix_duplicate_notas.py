from django.db import migrations, connection

def check_column_exists(table_name, column_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND COLUMN_NAME = %s
        """, [table_name, column_name])
        return cursor.fetchone()[0] > 0

def forwards_func(apps, schema_editor):
    # Check if the column already exists
    if not check_column_exists('menus_menuitem', 'notas'):
        # Only add the field if it doesn't exist
        schema_editor.add_field(
            'menus.MenuItem',
            'notas',
            models.TextField(blank=True, verbose_name='Notas adicionales'),
            preserve_default=True,
        )

def reverse_func(apps, schema_editor):
    # No need to do anything when unapplying
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('menus', '0002_alter_menuitem_options_remove_order_menus_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
