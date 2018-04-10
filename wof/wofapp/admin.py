from __future__ import unicode_literals

from django.contrib import admin
from wofapp.models import *
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

class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ['email']
    list_filter = ['email']
    search_fields = ['email',]
    save_on_top = True


admin.site.register(Linguagem,LinguagemAdmin)
admin.site.register(Framework,FrameworkmAdmin)
admin.site.register(Perfil,PerfilAdmin)
admin.site.register(Usuario,UsuarioAdmin)