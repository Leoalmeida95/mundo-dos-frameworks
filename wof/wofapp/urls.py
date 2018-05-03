from django.urls import path
from django.contrib.auth import views as auth_views
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
    path('confirmacao_reset_senha/<slug:uidb64>/<slug:token>)/',auth_views.password_reset_confirm, name='confirmacao_reset_senha'),
]