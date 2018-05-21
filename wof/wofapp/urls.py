from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    path('', views.home_view, name="home"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('reset_senha/', views.reset_senha_view, name="reset_senha"),
    path('comentario/<int:id>', views.comentario_view, name="comentario"),
    path('helloworld/<int:id>', views.helloworld_view, name="helloworld"),
    path('frameworks/<int:lg_id>', views.frameworks_view, name="frameworks"),
    path('reset_senha_confirmacao/<slug:uidb64>/<slug:token>', views.reset_senha_confirmacao_view, name="reset_senha_confirmacao"),
    path('trocar_senha/', views.trocar_senha_view, name="trocar_senha"),
    path('ativar_conta/<slug:uidb64>/<slug:token>', views.ativar_conta_view, name="ativar_conta")
]