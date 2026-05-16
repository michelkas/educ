"""
Modèles pour la gestion des comptes utilisateurs (profils, etc.).
Chaque classe et méthode est documentée selon les standards Pylint.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.html import format_html

class Profiles(models.Model):
    """
    Modèle représentant le profil utilisateur étendu.
    Contient les informations supplémentaires liées à l'utilisateur.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True, max_length= 120)
    avatar = models.ImageField(upload_to='avatar/', default='avatar/default_bcIt09K.jpg', blank=True)
    
    class Meta:
        db_table = 'profiles'
        verbose_name='profile'
        
    def save(self, *args, **kwargs):
        """
        Sauvegarde le profil après avoir redimensionné l'avatar si nécessaire.
        """
        #redimensionner la photo avant de sauvegarder
        if self.avatar:
            #ouvrir l'image
            img = Image.open(self.avatar)
            
            #redimensionner si necessaire 
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                
                #sauvegarde l'image redimensionné
                buffer = BytesIO()
                img.save(buffer, format = img.format if img.format else 'JPEG')
                self.avatar.save(
                    self.avatar.name,
                    ContentFile(buffer.getvalue()),
                    save=False
                )
        super().save(*args, **kwargs)
        
    def __str__(self):
        """
        Retourne la représentation textuelle du profil.
        Returns:
            str: Nom d'affichage du profil.
        """
        return f"{self.user.username}'s profile"

    def formatted_created_at(self):
        """
        Retourne la date de création formatée.
        Returns:
            str: Date formatée.
        """
        return self.user.date_joined.strftime("%d %B %Y")

    def formatted_updated_at(self):
        """
        Retourne la date de mise à jour formatée.
        Returns:
            str: Date formatée.
        """
        return self.user.last_login.strftime("%d %B %Y") if self.user.last_login else "Jamais"