
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Staff
from django.utils import timezone  

@receiver(post_save, sender=Staff)
def create_user_and_matricule(sender, instance, created, **kwargs):
    if not instance.user and instance.matricule:
        username = instance.matricule
        tmz = timezone.now()
        password = (
            f"{instance.name.lower()}{instance.date_birthday.strftime('%Y')}"
            if instance.date_birthday else tmz.strftime('%Y')
        )
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=instance.firstname,
            last_name=instance.name,
            email=instance.email,
            is_staff=False
        )
        instance.user = user
        instance.save(update_fields=['user'])
        
     