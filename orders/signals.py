from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Order
from .emails import send_order_status_email_html


@receiver(pre_save, sender=Order)
def _capture_old_status(sender, instance: Order, **kwargs):
    if instance.pk:
        try:
            old = Order.objects.only("status").get(pk=instance.pk)
            instance._old_status = old.status  # raw code e.g. 'pending'
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def _notify_on_status_change(sender, instance: Order, created: bool, **kwargs):
    user = getattr(instance, "user", None)
    to_email = getattr(user, "email", None)
    if not to_email:
        return

    old_status = getattr(instance, "_old_status", None)

    if created:
        send_order_status_email_html(
            to_email, instance, old_status=None, is_created=True
        )
    else:
        if old_status is not None and old_status != instance.status:
            send_order_status_email_html(
                to_email, instance, old_status=old_status, is_created=False
            )
