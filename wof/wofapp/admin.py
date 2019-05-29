from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from wofapp.models import *
from wofapp.forms import *

admin.site.site_title = 'Mundo dos Frameworks'
admin.site.site_header = 'Administração - Mundo dos Frameworks'
admin.site.index_title = 'Ambiente de Administração do site'

class LinguagemAdmin(admin.ModelAdmin):
    model = Linguagem
    list_display = ['nome']
    search_fields = ['nome',]
    fieldsets = (
        ('Dados da Linguagem', {'fields': ('nome','usuario')}),
    )
    save_on_top = True

class FrameworkAdmin(admin.ModelAdmin):
    model = Framework
    list_display = ['nome']
    search_fields = ['nome',]
    fieldsets = (
        ('Dados da Framework', {'fields': ('nome','linguagem')}),
    )
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
        ('Dados de Login', {'fields': ('email', 'password')}),
        ('Informação Pessoal', {'fields': ('primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao',)}),
        ('Permissão', {'fields': ('administrador','ativo')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao', 'password1', 'password2')}
        ),
    )
    readonly_fields = ['email','primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao']
    ordering = ('email',)
    filter_horizontal = ()

class DenunciaAdmin(admin.ModelAdmin):
    model = Denuncia
    list_filter = ['resolvida']
    search_fields = ['motivo',]
    list_display=['resolvida','motivo']
    fieldsets = (
        ('Motivo denúncia', {'fields': ('resolvida','motivo','data','quem_denunciou',)}),
        ('Conteúdo denúncia', {'fields': ('Comentario','opiniao','framework','linguagem',)}),
    )
    readonly_fields = ['motivo','data','quem_denunciou','Comentario','opiniao','framework','linguagem']
    save_on_top = True

class ComentarioAdmin(admin.ModelAdmin):
    model = Comentario
    search_fields = ['texto','usuario']
    list_display=['texto','usuario']
    readonly_fields = ['texto','usuario','data','framework',]
    exclude=['respostas']
    save_on_top = True

class OpiniaoAdmin(admin.ModelAdmin):
    model = Opiniao
    search_fields = ['texto','usuario']
    list_display=['texto','usuario']
    readonly_fields = ['texto','usuario','versao','eh_favoravel']
    save_on_top = True

admin.site.register(Denuncia,DenunciaAdmin)
admin.site.register(Opiniao,OpiniaoAdmin)
admin.site.register(Comentario,ComentarioAdmin)
admin.site.register(Linguagem,LinguagemAdmin)
admin.site.register(Framework,FrameworkAdmin)
admin.site.register(Usuario,UsuarioAdmin)

admin.site.unregister(Group)