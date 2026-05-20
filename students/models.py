from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from education.models import Classes, Section, Options
from django.utils import timezone  
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

class Students(models.Model):
    """
    Modèle représentant un élève de l'établissement.
    Contient les informations personnelles, scolaires et de contact du tuteur.
    """
    """
    Modèles pour la gestion des élèves dans l'application scolaire.
    Chaque classe et méthode est documentée selon les standards Pylint.
    """
    """
    Modèle représentant un élève de l'établissement.
    Contient les informations personnelles, scolaires et de contact du tuteur.
    """
    SEXE_CHOICE = [
        ('masculin', 'Masculin'),
        ('feminin', 'Feminin')
    ]
    STATUT_CHOICE = [
        ('scolariser', 'Scolariser'),
        ('exempter', 'Exempter')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("Nom", max_length=60, null=False, blank=False)
    surname = models.CharField("Post Nom", max_length=60, null=False, blank=False)
    first_name = models.CharField("Prenom", max_length=60, null=False, blank=False)
    sexe = models.CharField(max_length=10, null=True, choices=SEXE_CHOICE, default="masculin")
    matricule = models.CharField(max_length=100, unique=True, blank=True)
    classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    option = models.ForeignKey(Options, on_delete=models.SET_NULL, null=True, blank=True)
    date_birthday = models.DateField("Date de naissance", null=True, blank=True)
    place_birthday = models.CharField("Lieu de naissance", max_length=60, null=True, blank=True)
    address = models.CharField("Adresse", max_length=255, null=True, blank=True)
    statut = models.CharField(max_length=10, null=True, choices=STATUT_CHOICE, default="scolariser")
    father_name = models.CharField("Père", max_length=150, null=True, blank=True)
    mother_name = models.CharField("Mère", max_length=150, null=True, blank=True)
    garduan = models.CharField("Tuteur", max_length=150, null=True, blank=True)
    contact_garduan = PhoneNumberField("Contact du tuteur", region='CD', null=True, blank=True, unique=False)
    address_garduan = models.CharField("Adresse du Tuteur", max_length=255, null=True, blank=True)
    created_at = models.DateTimeField("Date d'inscription", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Dossier Etudiant'
        verbose_name_plural = 'Dossiers Etudiants'
        ordering = ['name']

    def save(self, *args, **kwargs):
        """Sauvegarde l'élève et génère automatiquement le matricule lors de la première sauvegarde."""
        creating = self.pk is None
        if creating:
            initial_kwargs = kwargs.copy()
            initial_kwargs.pop('update_fields', None)
            super().save(*args, **initial_kwargs)
            if not self.matricule:
                self.matricule = self._generate_matricule()
                super().save(update_fields=['matricule'])
        else:
            super().save(*args, **kwargs)

    def _generate_matricule(self):
        option_code = str(self.option.code).zfill(3) if self.option and self.option.code is not None else '000'
        return f"{timezone.now().year}{option_code}{self.id:03d}"

    def __str__(self):
        return f" {self.name} {self.surname} {self.first_name} "

    def clean(self):
        """Valide l'attribution d'option et la cohérence section/classe."""
        section_name = self.section.name.strip().lower() if self.section else ''
        classe_name = self.classe.name.strip().lower() if self.classe else ''

        if self.option:
            if section_name in ['maternelle', 'primaire']:
                raise ValidationError(
                    "Les élèves en section primaire ou maternelle ne peuvent pas être attribués à une option."
                )
            if classe_name in ['7ème', '8ème', '7eme', '8eme']:
                raise ValidationError(
                    "Les élèves en classe 7ème ou 8ème ne peuvent pas être attribués à une option."
                )

        if classe_name in ['7ème', '8ème', '7eme', '8eme'] and section_name in ['maternelle', 'primaire']:
            raise ValidationError(
                "La classe 7ème ou 8ème ne peut pas appartenir à une section primaire ou maternelle."
            )

    def formatted_created_at(self):
        """Retourne la date de création formatée."""
        """
        Retourne la date de création formatée.
        Returns:
            str: Date formatée.
        """
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def formatted_updated_at(self):
        """Retourne la date de mise à jour formatée."""
        """
        Retourne la date de mise à jour formatée.
        Returns:
            str: Date formatée.
        """
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_students_for_payment(cls):
        """
        Retourne les élèves qui ne sont pas exemptés (statut différent de 'exempter').
        """
        """
        Retourne les élèves qui ne sont pas exemptés (statut différent de 'exempter').
        Returns:
            QuerySet: Élèves non exemptés.
        """
        return cls.objects.exclude(statut__iexact='exempter')
