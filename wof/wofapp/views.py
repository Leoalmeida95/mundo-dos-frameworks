from django.shortcuts import render
from django.template import loader
from django.views.generic import CreateView, ListView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm,AuthenticationForm
from .models import Linguagem, Framework

def home(request):
    linguagens = Linguagem.objects.all().order_by('nome')
    return render(request,'web/home.html',{'linguagens':linguagens})

def get_frameworks(request,lg_id):
    linguagem = Linguagem.objects.get(id=lg_id)
    frameworks = Framework.objects.all().filter(linguagem_id=lg_id)
    linguagens = Linguagem.objects.all().order_by('nome')
    return render(request,'web/frameworks.html',{'frameworks':frameworks,'linguagem':linguagem,'linguagens':linguagens})

def login_view(request, *args, **kwargs):
    args = {}
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('web:home'))
    else:
        form = AuthenticationForm()

    args['form'] = form
    return render(request,'web/home.html',args)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('web:home'))

def register(request):
    args = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Parabéns, registro concluído com sucesso.')
            return HttpResponseRedirect(reverse('web:home'))
    else:
        form = CustomUserCreationForm()

    args['form'] = form
    linguagens = Linguagem.objects.all().order_by('nome')
    return render(request,'web/register.html',args)

@login_required
def altera_usuario_view(request):
    return render(request,'atualizar_dados.html',{'linguagens':linguagens})

@login_required
def atualiza_usuario(request):
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario actualizado exitosamente.', extra_tags='html_dante')
            return HttpResponseRedirect(reverse('home:listar_usuarios'))
    else:
        form = UserChangeForm(instance=user)
        
    context = {
        'form': form,
    }
    return render(request, 'atualizar_dados.html', context)