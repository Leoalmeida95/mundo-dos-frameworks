from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    #inicio
    path('', views.chart_view, name="home"),
    # usuario
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('reset_senha_confirmacao/<slug:uidb64>/<slug:token>', views.reset_senha_confirmacao_view, name="reset_senha_confirmacao"),
    path('trocar_senha/', views.trocar_senha_view, name="trocar_senha"),
    path('ativar_conta/<slug:uidb64>/<slug:token>', views.ativar_conta_view, name="ativar_conta"),
    path('reset_senha/', views.reset_senha_view, name="reset_senha"),
    #linguagem
    path('nova_linguagem/', views.nova_linguagem_view, name="nova_linguagem"),
    path('define_linguagem_adcframework/<int:lg_id>', views.define_linguagem_adcframework_view, name="define_linguagem_adcframework"),
    #frameworks
    path('faq/', views.faq_view, name="faq"),
    path('novo_framework/<int:lg_id>', views.novo_framework_view, name="novo_framework"),
    path('buscar_framework/', views.buscar_framework_view, name="buscar_framework"),
    path('favoritos/', views.favoritos_view, name="favoritos"),
    path('frameworks/<int:id>', views.frameworks_view, name="frameworks"),
    path('favoritar_framework/<int:fm_id>', views.favoritar_framework_view, name="favoritar_framework"),
    path('desfavoritar_framework/<int:fm_id>', views.desfavoritar_framework_view, name="desfavoritar_framework"),
    #versao
    path('trocar_versao/<int:vs_id>', views.trocar_versao_view, name="trocar_versao"),
    path('versao/<int:fm_id>', views.versao_view, name="versao"),
    path('editar_versao/<int:vs_id>/<int:fm_id>', views.editar_versao_view, name="editar_versao"),
    #comentario
    path('comentario/<int:fm_id>', views.comentario_view, name="comentario"),
    path('resposta/<int:fm_id>/<int:cm_id>', views.resposta_view, name="resposta"),
    path('excluir_comentario/<int:rs_id>/<int:fm_id>', views.excluir_comentario_view, name="excluir_comentario"),
    #helloworld
    path('helloworld/<int:fm_id>/<int:vs_id>', views.helloworld_view, name="helloworld"),
    #opiniao
    path('opiniao/<int:fm_id>/<int:vs_id>', views.opiniao_view, name="opiniao"),
    path('editar_opiniao/<int:op_id>/<int:fm_id>', views.editar_opiniao_view, name="editar_opiniao"),
    #funcionalidade
    path('funcionalidade/<int:fm_id>/<int:vs_id>', views.funcionalidade_view, name="funcionalidade"),
    path('editar_funcionalidade/<int:fun_id>/<int:fm_id>', views.editar_funcionalidade_view, name="editar_funcionalidade"),
    #links
    path('link/<int:fm_id>', views.link_view, name="link"),
    path('editar_link/<int:li_id>/<int:fm_id>', views.editar_link_view, name="editar_link"),
    #voto
    path('votar_link/<int:li_id>/<int:fm_id>', views.votar_link_view, name="votar_link"),
    #denuncia
    path('denuncia_comentario/<int:cm_id>', views.denuncia_comentario_view, name="denuncia_comentario"),
    path('denuncia_opiniao/<int:op_id>', views.denuncia_opiniao_view, name="denuncia_opiniao"),
]