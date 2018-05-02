from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('senha_reset/', views.senha_reset_view, name="senha_reset"),
    path('comentario/<int:id>', views.comentario_view, name="comentario"),
    path('frameworks/<int:lg_id>', views.frameworks_view, name='frameworks'),
    path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.confirmacao_reset_senha, name='confirmacao_reset_senha')
]