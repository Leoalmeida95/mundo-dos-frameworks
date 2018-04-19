from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from wofapp.models import *
from wofapp.forms import *

admin.site.site_title = 'WOF'
admin.site.site_header = 'Administração - WOF'
admin.site.index_title = 'Ambiente de administração do site'

class LinguagemAdmin(admin.ModelAdmin):
    model = Linguagem
    list_display = ['nome']
    list_filter = ['nome']
    search_fields = ['nome',]
    save_on_top = True

class FrameworkmAdmin(admin.ModelAdmin):
    model = Framework
    list_display = ['nome']
    list_filter = ['nome']
    search_fields = ['nome',]
    save_on_top = True

class PerfilAdmin(admin.ModelAdmin):
    model = Perfil
    list_display = ['nome']
    list_filter = ['nome']
    search_fields = ['nome',]
    save_on_top = True

class UsuarioAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    model = Usuario
    list_display = ['email','last_name','is_admin']
    list_filter = ['email']
    search_fields = ['email','first_name']
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informação Pessoal', {'fields': ('first_name','last_name','cpf','conta_publica','formacao','profissao',)}),
        ('Permissão', {'fields': ('is_admin','is_activeUser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','first_name','last_name','cpf','conta_publica','formacao','profissao', 'password1', 'password2')}
        ),
    )
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Linguagem,LinguagemAdmin)
admin.site.register(Framework,FrameworkmAdmin)
admin.site.register(Perfil,PerfilAdmin)
admin.site.register(Usuario,UsuarioAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)