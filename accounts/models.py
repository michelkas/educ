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
    DEFAULT_AVATAR = 'avatar/default_bcIt09K.jpg'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True, max_length= 120)
    avatar = models.ImageField(upload_to='avatar/', default=DEFAULT_AVATAR, blank=True)
    
    class Meta:
        db_table = 'profiles'
        verbose_name='profile'
        
    def save(self, *args, **kwargs):
        """
        Sauvegarde le profil après avoir redimensionné l'avatar si nécessaire.
        """
        if not self.avatar or not self.avatar.name:
            self.avatar = self.DEFAULT_AVATAR
        elif not self.avatar.storage.exists(self.avatar.name):
            self.avatar = self.DEFAULT_AVATAR

        if self.avatar and self.avatar.name != self.DEFAULT_AVATAR:
            try:
                img = Image.open(self.avatar)
            except (FileNotFoundError, OSError, ValueError):
                self.avatar = self.DEFAULT_AVATAR
            else:
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    buffer = BytesIO()
                    img.save(buffer, format=img.format if img.format else 'JPEG')
                    self.avatar.save(
                        os.path.basename(self.avatar.name),
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
