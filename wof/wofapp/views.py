from django.shortcuts import render
from django.template import loader
from django.views.generic import CreateView, ListView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.urls import reverse_lazy, reverse

from .forms import CustomUserCreationForm
from .models import Linguagem, Framework

def home(request):
    linguagens = Linguagem.objects.all().order_by('nome')
    return render(request,'web/home.html',{'linguagens':linguagens})

def get_frameworks(request,lg_id):
    linguagem = Linguagem.objects.get(id=lg_id)
    frameworks = Framework.objects.all().filter(linguagem_id=lg_id)
    return render(request,'web/frameworks.html',{'frameworks':frameworks,'linguagem':linguagem})

def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('web:home'))

    kwargs['extra_context'] = {'next': reverse('web:home')}
    kwargs['template_name'] = 'web:login.html'
    return login(request, *args, **kwargs)

def logout_view(request, *args, **kwargs):
    kwargs['next_page'] = reverse('web:home')
    return logout(request, *args, **kwargs)

class RegistrationView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('web:login')
    template_name = "web/register.html"
