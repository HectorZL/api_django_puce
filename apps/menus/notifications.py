from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site


def send_order_status_notification(request, order, status_changed=False):
    """
    Send notification to the client about their order status
    
    Args:
        request: HttpRequest object
        order: Order instance
        status_changed: Boolean indicating if this is a status change notification
    """
    if not order.cliente or not order.cliente.usuario.email:
        return False
    
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    order_url = f"{protocol}://{domain}{reverse('menus:order_detail', args=[order.id])}"
    
    # Email subject based on order status
    subject = _('Actualización de tu pedido #{order_id}').format(order_id=order.id)
    
    # Context for the email template
    context = {
        'order': order,
        'status_changed': status_changed,
        'order_url': order_url,
        'site_name': site_name,
        'domain': domain,
        'protocol': protocol,
    }
    
    # Render email content
    text_content = render_to_string('emails/order_status_update.txt', context)
    html_content = render_to_string('emails/order_status_update.html', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.cliente.usuario.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending order notification email: {e}")
        return False


def send_order_created_notification(request, order):
    """Send notification when a new order is created"""
    return send_order_status_notification(request, order, status_changed=True)


def send_order_status_changed_notification(request, order, old_status):
    """Send notification when order status changes"""
    return send_order_status_notification(request, order, status_changed=True)


def send_order_cancellation_notification(request, order, reason):
    """Send notification when an order is cancelled"""
    if not order.cliente or not order.cliente.usuario.email:
        return False
    
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    order_url = f"{protocol}://{domain}{reverse('menus:order_detail', args=[order.id])}"
    
    subject = _('Tu pedido #{order_id} ha sido cancelado').format(order_id=order.id)
    
    context = {
        'order': order,
        'order_url': order_url,
        'site_name': site_name,
        'domain': domain,
        'protocol': protocol,
        'cancellation_reason': reason,
    }
    
    # Render email content
    text_content = render_to_string('emails/order_cancelled.txt', context)
    html_content = render_to_string('emails/order_cancelled.html', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.cliente.usuario.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending order cancellation email: {e}")
        return False
