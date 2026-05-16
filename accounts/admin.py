from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profiles

class ProfilesInline(admin.StackedInline):
    model = Profiles
    can_delete = False
    verbose_name_plural = 'Profil'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfilesInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "Panneau d'administration"
admin.site.site_title = "Admin"
admin.site.index_title = "Tableau de bord de l'administration"