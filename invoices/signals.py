# Prevent crashes if Profile is missing (IMPORTANT)

# If a user exists without a Profile, user.profile... will crash.

# auto-create Profile using signals
# invoices/signals.py


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(profile_user_id=instance, profile_role="Admin")
