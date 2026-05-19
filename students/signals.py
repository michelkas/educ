
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Students
from django.utils import timezone  

@receiver(post_save, sender=Students)    
def create_user_and_matricule(sender, instance, created, **kwargs):
   if created:
    #sauvegarde automatique du matricule et creation
        if not instance.matricule:
            id_stf = str(instance.id)
            tmz = timezone.now()
            
            instance.matricule =  f"{timezone.now().year}{instance.option.code if instance.option else '000'}{id_stf.zfill(3)}" #ex : 2024001001
            instance.save(update_fields=["matricule"]) 
            
        if not instance.user:
            username = instance.matricule
            tmz = timezone.now()
            password = instance.name.upper() + instance.date_birthday.strftime("%Y") if instance.date_birthday else tmz.strftime("%Y") #ex : DOE2000 ou DOE2024 si date_birthday est null
            user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=instance.first_name,
                    last_name=instance.name,
                    is_staff=False
            )
            instance.user = user
            instance.save()
        
     