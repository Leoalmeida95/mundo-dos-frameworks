from django.urls import path
from . import views

app_name='web'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register_view, name="register"),
    path('atualizar_usuario/', views.atualizar_usuario_view, name="atualizar"),
    path('comentario', views.comentario_view, name="comentar"),
    path('frameworks/<int:lg_id>', views.frameworks_view, name='frameworks'),
]