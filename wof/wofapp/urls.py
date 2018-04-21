from django.urls import path
from . import views

app_name='web'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name="register"),
    path('frameworks/<int:lg_id>', views.get_frameworks, name='frameworks'),
]