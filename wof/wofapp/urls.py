from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    #inicio
    path('', views.chart_view, name="home"),
    #paths usuario
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('reset_senha_confirmacao/<slug:uidb64>/<slug:token>', views.reset_senha_confirmacao_view, name="reset_senha_confirmacao"),
    path('trocar_senha/', views.trocar_senha_view, name="trocar_senha"),
    path('ativar_conta/<slug:uidb64>/<slug:token>', views.ativar_conta_view, name="ativar_conta"),
    path('reset_senha/', views.reset_senha_view, name="reset_senha"),
    path('faq/', views.faq_view, name="faq"),
    #frameworks
    path('buscar_framework/', views.buscar_framework_view, name="buscar_framework"),
    path('favoritos/', views.favoritos_view, name="favoritos"),
    path('frameworks/<int:id>', views.frameworks_view, name="frameworks"),
    path('trocar_versao/<int:vs_id>', views.trocar_versao_view, name="trocar_versao"),
    path('comentario/<int:fm_id>', views.comentario_view, name="comentario"),
    path('resposta/<int:fm_id>/<int:cm_id>', views.resposta_view, name="resposta"),
    path('helloworld/<int:fm_id>/<int:vs_id>', views.helloworld_view, name="helloworld"),
    path('versao/<int:fm_id>', views.versao_view, name="versao"),
    path('editar_versao/<int:vs_id>/<int:fm_id>', views.editar_versao_view, name="editar_versao"),
    path('nova_linguagem/', views.nova_linguagem_view, name="nova_linguagem"),
    path('novo_framework/<int:lg_id>', views.novo_framework_view, name="novo_framework"),
    path('define_linguagem_adcframework/<int:lg_id>', views.define_linguagem_adcframework_view, name="define_linguagem_adcframework"),
    path('opiniao/<int:fm_id>/<int:vs_id>', views.opiniao_view, name="opiniao"),
    path('favoritar_framework/<int:fm_id>', views.favoritar_framework_view, name="favoritar_framework"),
    path('desfavoritar_framework/<int:fm_id>', views.desfavoritar_framework_view, name="desfavoritar_framework"),
]