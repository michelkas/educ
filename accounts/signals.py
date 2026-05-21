from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profiles

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profiles.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, update_fields=None, **kwargs):
    if created or update_fields == {"last_login"} or update_fields == ["last_login"]:
        return

    if hasattr(instance, 'profiles'):
        instance.profiles.save()
