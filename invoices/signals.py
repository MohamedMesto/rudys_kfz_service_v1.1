# invoices/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.create(
        profile_user_id=instance,
        profile_role="Mechanic",
    )
