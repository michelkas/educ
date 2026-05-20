
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Staff
from django.utils import timezone  

@receiver(post_save, sender=Staff)    
def create_user_and_matricule(sender, instance, created, **kwargs):
   if created:
    #sauvegarde automatique du matricule et creation
        if not instance.matricule:
            id_stf = str(instance.id) #obtenir l'ID
            db_stf = instance.date_birthday.strftime("%y") if instance.date_birthday else "00" #obtenir les deux dernier chiffre de l'année de naissance
            nm = instance.name[:1].upper() if instance.name else 'X' #obtenir la premier lettre du nom
            tmz = timezone.now()
            
            instance.matricule = f"{tmz.strftime("%Y")}{id_stf.zfill(4)}{db_stf}{nm}"  #le matricule est composez de l'année actuelle ex: 2024, suivi de l'ID de l'employé avec des zéros pour le compléter à 4 chiffres, les deux derniers chiffres de l'année de naissance et la première lettre du nom en majuscule
            instance.save(update_fields=["matricule"])  #ex: 2024000100X pour un employé né en 2000 et dont le nom commence par X
            
        if not instance.user:
            username = instance.matricule
            password = f"{instance.name.lower()}{instance.date_birthday.strftime("%Y") if instance.date_birthday else '0000'}"  #le mot de passe est composez du nom en minuscule suivi de l'année de naissance ex: x2000 pour un employé nommé X et né en 2000
            user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=instance.firstname,
                    last_name=instance.name,
                    email= instance.email,
                    is_staff=False
            )
            instance.user = user
            instance.save()
        
     