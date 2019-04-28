from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from wofapp.models import *
from wofapp.forms import *

admin.site.site_title = 'Mundo dos Frameworks'
admin.site.site_header = 'Administração - Mundo dos Frameworks'
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

class UsuarioAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = CustomUserCreationForm

    model = Usuario
    list_display = ['email','primeiro_nome','ultimo_nome','administrador']
    list_filter = ['email']
    search_fields = ['email','primeiro_nome', 'cpf']
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informação Pessoal', {'fields': ('primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao',)}),
        ('Permissão', {'fields': ('administrador','ativo')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao', 'password1', 'password2')}
        ),
    )
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Linguagem,LinguagemAdmin)
admin.site.register(Framework,FrameworkmAdmin)
admin.site.register(Usuario,UsuarioAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)