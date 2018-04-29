from django.urls import path
from . import views

app_name='wofapp'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registrar_usuario/', views.registrar_usuario_view, name="registrar"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('comentario/<int:id>', views.comentario_view, name="comentario"),
    path('frameworks/<int:lg_id>', views.frameworks_view, name='frameworks'),
]