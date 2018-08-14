from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    path('', views.chart_view, name="home"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('reset_senha_confirmacao/<slug:uidb64>/<slug:token>', views.reset_senha_confirmacao_view, name="reset_senha_confirmacao"),
    path('trocar_senha/', views.trocar_senha_view, name="trocar_senha"),
    path('ativar_conta/<slug:uidb64>/<slug:token>', views.ativar_conta_view, name="ativar_conta"),
    path('reset_senha/', views.reset_senha_view, name="reset_senha"),
    path('faq/', views.faq_view, name="faq"),

    path('frameworks/<int:id>', views.frameworks_view, name="frameworks"),
    path('comentario/<int:id>', views.comentario_view, name="comentario"),
    path('resposta/<int:fm_id>/<int:cm_id>', views.resposta_view, name="resposta"),
    path('helloworld/<int:fm_id>/<int:vs_id>', views.helloworld_view, name="helloworld"),
    path('versao/<int:id>', views.versao_view, name="versao"),
]