from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .models import Linguagem, Framework

def home_view(request):
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    return render(request,'home.html',{'linguagens':linguagens_navbar})

def frameworks_view(request,lg_id):
    args = {}
    linguagem_selecionada = Linguagem.objects.get(id=lg_id)
    frameworks = Framework.objects.all().filter(linguagem_id=lg_id)
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    args['frameworks'] = frameworks
    args['linguagem'] = linguagem_selecionada
    args['linguagens'] = linguagens_navbar
    return render(request,'frameworks.html',args)

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
                return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = AuthenticationForm()

    args['form'] = form
    return render(request,'home.html',args)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('wofapp:home'))

def registrar_usuario_view(request):
    args = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        publica = request.POST.get("conta_publica","")
        args['form'] = form
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Parabéns, registro concluído com sucesso.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = CustomUserCreationForm()
        publica = 'True'

    args['publica'] = True if publica is 'True' else False 
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    args['linguagens'] =linguagens_navbar
    return render(request,'usuario.html',args)

@login_required
def comentario_view(request,id):
    args = {}
    user = request.user
    if request.method == 'POST':
        framework = Framework.objects.all().get(id=id)
        form = ComentarioForm(request.POST)
        args['form'] = form
        if framework is not None and form.is_valid():
            x = request.POST['texto']

    #retornar para o framework de origem do post
    return render(request,'frameworks.html',args)

@login_required
def atualizar_usuario_view(request):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = UserChangeForm(instance=user)
        
    args['publica'] = user.conta_publica
    args['form'] = form
    return render(request, 'usuario.html', args)