from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Order, OrderHistory

User = get_user_model()

@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """
    Track changes to order status and create history entries
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.estado != instance.estado:
                # Status has changed, create a history entry
                OrderHistory.objects.create(
                    order=instance,
                    old_status=old_instance.estado,
                    new_status=instance.estado,
                    changed_by=instance._changed_by if hasattr(instance, '_changed_by') else None,
                    notes=getattr(instance, '_status_change_notes', '')
                )
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def create_initial_history(sender, instance, created, **kwargs):
    """
    Create initial history entry when an order is first created
    """
    if created:
        OrderHistory.objects.create(
            order=instance,
            new_status=instance.estado,
            changed_by=instance._changed_by if hasattr(instance, '_changed_by') else None,
            notes=_('Pedido creado')
        )

@receiver(post_save, sender=Order)
def update_order_timestamps(sender, instance, created, **kwargs):
    """
    Update relevant timestamps when order status changes
    """
    if not created and instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.estado != instance.estado:
                # Status has changed, update relevant timestamps
                now = timezone.now()
                updates = {}
                
                if instance.estado == 'CANCELADO':
                    updates['fecha_cancelacion'] = now
                elif instance.estado == 'ENTREGADO':
                    updates['fecha_entrega_real'] = now
                
                if updates:
                    Order.objects.filter(pk=instance.pk).update(**updates)
        except Order.DoesNotExist:
            pass
