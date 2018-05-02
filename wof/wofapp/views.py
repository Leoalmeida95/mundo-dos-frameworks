from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from .forms import *
from .models import Linguagem, Framework

def home_view(request):
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    return render(request,'home.html',{'linguagens':linguagens_navbar})

def senha_reset_view(request):
    args = {}
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(from_email = 'admin@thedomain.com', email_template_name= 'corpo_email.html', 
            use_https = False, token_generator = default_token_generator, request=request, html_email_template_name=None)
    else:
        form = PasswordResetForm()

    args['form'] = form
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
    return render(request,'senha_reset.html',args)

def login_view(request, *args, **kwargs):
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
            erroMsg = form.errors['__all__'].data[0].message
            messages.error(request, erroMsg)

    return render(request,'home.html')

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
            messages.info(request, 'Parabéns, registro concluído com sucesso.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = CustomUserCreationForm()
        publica = 'True'

    args['publica'] = True if publica == 'True' else False 
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    args['linguagens'] =linguagens_navbar
    return render(request,'usuario.html',args)

@login_required
def atualizar_usuario_view(request):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.info(request, 'Usuário atualizado com sucesso!')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = UserChangeForm(instance=user)
        
    args['publica'] = user.conta_publica
    args['form'] = form
    return render(request, 'usuario.html', args)

def frameworks_view(request,lg_id):
    args = {}
    linguagem_selecionada = Linguagem.objects.get(id=lg_id)
    frameworks = Framework.objects.all().filter(linguagem_id=lg_id)
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    args['frameworks'] = frameworks
    args['linguagem'] = linguagem_selecionada
    args['linguagens'] = linguagens_navbar
    return render(request,'frameworks.html',args)

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