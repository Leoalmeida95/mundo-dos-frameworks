from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .tokens import account_activation_token
from .forms import *
from .models import Linguagem, Framework,Versao,Helloworld,Opiniao,Link,Comentario

def home_view(request):
    linguagens_navbar = Linguagem.objects.all().order_by('nome')
    return render(request,'home.html',{'linguagens':linguagens_navbar})

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
            user = form.save(commit=False)
            user.is_activeUser = False
            user.save()
            form.enviar_email(user,request=request)
            messages.info(request, 'Muito bem! Agora para concluir seu registro, por favor confirme sua conta no email que enviamos pra você.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = CustomUserCreationForm()
        publica = 'True'

    args['publica'] = True if publica == 'True' else False 
    args['linguagens'] =Linguagem.objects.all().order_by('nome')
    return render(request,'usuario.html',args)

def ativar_conta_view(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_activeUser = True
        user.save()
        login(request, user)
        messages.info(request, 'Parabéns, registro concluído com sucesso.')
        return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        return HttpResponse('Link de ativação da conta inválido.')

def reset_senha_view(request):
    args = {}
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.info(request, 'As instruções para troca de senha foram enviadas para seu email.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = PasswordResetForm()

    args['form'] = form
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
    return render(request,'reset_senha.html',args)

def reset_senha_confirmacao_view(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    args = {}
    if user is not None and account_activation_token.check_token(user, token):
        authorized = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.info(request, 'Senha alterada com sucesso!')
                return HttpResponseRedirect(reverse('wofapp:home'))
        else:
            form = SetPasswordForm(user)
    else:
        authorized = False
        form = None
    
    args['form'] = form
    args['authorized'] = authorized
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
    return render(request, 'reset_senha_confirmacao.html', args)

@login_required
def atualizar_usuario_view(request):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.info(request, 'Seus dados foram atualizados com sucesso!')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = UserChangeForm(instance=user)
        
    args['publica'] = user.conta_publica
    args['form'] = form
    return render(request, 'usuario.html', args)

@login_required
def trocar_senha_view(request):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Senha alterada com sucesso! Por favor, faça o login novamente.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = SetPasswordForm(user)
    
    args['authorized'] = True
    args['form'] = form
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
    return render(request, 'reset_senha_confirmacao.html', args)

def frameworks_view(request,lg_id):
    args = {}
    frameworks = Framework.objects.all().filter(linguagem_id=lg_id)
    framework = frameworks.first()

    # from django.db import connection
    # for comentario in framework.comentarios.all():
    #     print (comentario.texto)
    
    # print (len(connection.queries)) # realiza 3 queries

    testes = Framework.objects.prefetch_related('comentarios').all()
    teste = testes.filter(linguagem_id=lg_id)
    t = teste.first()
    from django.db import connection
    for comentario in t.comentarios.all():
        print (comentario.texto)
    
    print (len(connection.queries))

    args['versoes'] = Framework.objects.prefetch_related('versoes').filter(framework_id=framework.id)
    args['opinioes'] = Framework.objects.prefetch_related('opinioes').filter(framework_id=framework.id)
    args['links'] = Framework.objects.prefetch_related('links').filter(framework_id=framework.id)
    args['helloword'] = Framework.objects.prefetch_related('helloworlds').filter(framework_id=framework.id).first()

    args['lista_frameworks'] = frameworks
    args['framework'] = framework
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
    return render(request,'frameworks.html',args)

@login_required
def comentario_view(request,id):
    args = {}
    user = request.user
    if request.method == 'POST':
        framework = Framework.objects.get(id=id)
        form = ComentarioForm(request.POST)
        args['form'] = form
        if framework is not None and form.is_valid():
            x = request.POST['texto']

    #retornar para o framework de origem do post
    return render(request,'frameworks.html',args)

@login_required
def helloworld_view(request,id):
    args = {}
    user = request.user
    if request.method == 'POST':
        hello = Helloworld.objects.all().get(framework_id=id).first()
        # args['framework'] = framework
        form = HelloWorldForm(request.POST)
        args['form'] = form
        if form.is_valid():
            if hello is None:
                hello = Helloworld() 
            hello.descricao = request.POST['descricao']
            hello.codigo_exemplo =codigo_exemplo=request.POST['codigo_exemplo']
            hello.framework_id = id
            user = request.user
            hello.usuario_id = user.id
            hello.save()
            args['helloword'] = hello

    #retornar para o framework de origem do post
    return render(request,'frameworks.html',args)