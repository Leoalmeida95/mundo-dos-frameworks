from django.urls import path
from . import views

app_name='web'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.RegistrationView.as_view(), name="register")
]