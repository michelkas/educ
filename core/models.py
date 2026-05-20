from django.db import models

"""
field :
    nom officiel, numero d'agrement, code d'identification, province, statut juridique, promo
"""

class Core(models.Model):
    official_name = models.CharField("Nom officiel de l'école", max_length= 255, null=False, blank=False)
    number = models.CharField("Numero d'agrément", max_length= 255, blank=True)
    code = models.CharField("code d'identification de l'école", max_length= 255, blank=True)
    province = models.CharField("Province Educationnelle", max_length= 255, blank=True)
    statut = models.TextField("Statut juridique", blank=True)
    promo = models.CharField("Promoteur de l'école", max_length= 255, blank=True)
    logo = models.ImageField("Logo de l'école", upload_to='logo/', blank=True, null=True)
    date_created = models.DateField('Date de création', null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'core'

    def __str__(self):
        return self.official_name



