from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.urls import reverse_lazy, reverse

from .forms import CustomUserCreationForm

def home(request):
    return render(request,'home.html')


def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('web:home'))

    kwargs['extra_context'] = {'next': reverse('web:home')}
    kwargs['template_name'] = 'web/login.html'
    return login(request, *args, **kwargs)


def logout_view(request, *args, **kwargs):
    kwargs['next_page'] = reverse('web:home')
    return logout(request, *args, **kwargs)


class RegistrationView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('web:login')
    template_name = "web/register.html"
