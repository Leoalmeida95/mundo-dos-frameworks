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
import logging

from .fusioncharts import FusionCharts
from .tokens import account_activation_token
from .forms import *
from .models import *

def chart_view(request):
    linguagens = Linguagem.objects.all().order_by('nome')
    top_linguagens = linguagens[:5]
    frameworks = Framework.objects.all().order_by('nome')[:10]

    chart1 = """{ 
                "chart": {
                "caption": "Top 5 linguagens mais acessadas",
                "subcaption": "Mensal",
                "startingangle": "120",
                "showlabels": "1",
                "showlegend": "1",
                "enablemultislicing": "1",
                "slicingdistance": "15",
                "showpercentvalues": "1",
                "showpercentintooltip": "1",
                "plottooltext": "Linguagem: $label, Acessos : $datavalue",
                "theme": "zune"
                },
                "data": ["""
    
    i = 1
    for linguagem in top_linguagens:
        chart1 = chart1 + """ {"label": " """ + linguagem.nome +  """", "value":" """   +  str(i*100) + """"},"""
        i = i+1
    chart1 = chart1[:-1]    
    chart1 = chart1 + """         ]
        }"""


    chart2 = """{ 
                "chart": {
                "caption": "Top 10 Frameworks com mais contribuintes",
                "subcaption": "Total",
                "startingangle": "120",
                "showlabels": "1",
                "showlegend": "1",
                "enablemultislicing": "1",
                "slicingdistance": "15",
                "showpercentvalues": "1",
                "showpercentintooltip": "1",
                "plottooltext": "Framework: $label, Contribuintes : $datavalue",
                "theme": "carbon"
                },
                "data": ["""
    
    for framework in frameworks:
        chart2 = chart2 + """ {"label": " """ + framework.nome +  """", "value":" """   +  str(i*100) + """"},"""
        i = i+1
    chart2 = chart2[:-1]    
    chart2 = chart2 + """         ]
        }"""

    p1 = FusionCharts("pie3d", "ex1" , "100%", "400", "chart-1", "json", chart1)
    p2 = FusionCharts("pie3d", "ex2" , "100%", "430", "chart-2", "json", chart2)

    return  render(request, 'home.html', {'output1' : p1.render(),'output2' : p2.render(),'linguagens':linguagens})

def login_view(request, *args, **kwargs):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = authenticate(request, username=username, password=password)
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro de autenticação no login.")
                user = None

            if user is not None:
                login(request, user)
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.error(request, erroMsg)
     
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def logout_view(request):
    logout(request)
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def faq_view(request):
    return render(request,'faq.html',{'linguagens':Linguagem.objects.all().order_by('nome')})

def registrar_usuario_view(request):
    args = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        publica = request.POST.get("conta_publica","")
        args['form'] = form
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_activeUser = False
                user.save()
                form.enviar_email(user,request=request)
                messages.info(request, 'Muito bem! Agora para concluir seu registro, por favor confirme sua conta no email que enviamos pra você.')
                return HttpResponseRedirect(reverse('wofapp:home'))
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro no registro de usuário.")
                messages.error(request, 'Erro ao registrar usuário. Tente novamente mais tarde.')
    else:
        form = CustomUserCreationForm()
        publica = 'True'

    args['publica'] = True if publica == 'True' else False 
    args['linguagens'] = Linguagem.objects.all().order_by('nome')
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
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.info(request, 'As instruções para troca de senha foram enviadas para seu email.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = PasswordResetForm()

    return render(request,'nova_senha.html',{'form':form,'linguagens':Linguagem.objects.all().order_by('nome')})

def reset_senha_confirmacao_view(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

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
    

    return render(request, 'reset_senha_confirmacao.html', {'form':form,'authorized':authorized,
    'linguagens':Linguagem.objects.all().order_by('nome')})

@login_required
def atualizar_usuario_view(request):
    user = request.user
    if request.method == 'POST':
        POST = request.POST.copy()
        POST['cpf'] = user.cpf
        form = UserChangeForm(POST, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                messages.info(request, 'Seus dados foram atualizados com sucesso!')
                return HttpResponseRedirect(reverse('wofapp:home'))
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar usuário.")
                messages.error(request, 'Erro ao atualizar dados. Tente novamente mais tarde.')
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'usuario.html', {'linguagens':Linguagem.objects.all().order_by('nome'),'form':form,
    'publica':user.conta_publica})

@login_required
def trocar_senha_view(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Senha alterada com sucesso! Por favor, faça o login novamente.')
            return HttpResponseRedirect(reverse('wofapp:home'))
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'reset_senha_confirmacao.html', {'authorized':True,'form':form,
    'linguagens':Linguagem.objects.all().order_by('nome')})

def frameworks_view(request,id):
    framework = Framework.objects.get(id=id)
    respostas = Comentario.objects.raw('''SELECT to_comentario_id AS id FROM wofapp_comentario_respostas''')
    frameworks = framework.linguagem.frameworks.all()

    return render(request,'frameworks.html', {'lista_frameworks':frameworks,'framework':framework,
    'linguagens':Linguagem.objects.all().order_by('nome')})

@login_required
def comentario_view(request,id):
    user = request.user
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                coment = Comentario(
                    texto=request.POST['texto'],
                    framework_id =id,
                    usuario_id = user.id
                )
                coment.save()
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao criar comentário.")
                messages.error(request, 'Erro ao realizar comentário. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':id}))

@login_required
def resposta_view(request,fm_id,cm_id):
    user = request.user
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                coment = Comentario.objects.get(id=cm_id)
                coment.respostas.create(
                    texto=request.POST['texto'],
                    framework_id= fm_id,
                    usuario_id=user.id
                )
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao criar resposta.")
                messages.error(request, 'Erro ao realizar resposta. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))


@login_required
def helloworld_view(request,id):
    user = request.user
    if request.method == 'POST':
        form = HelloWorldForm(request.POST)
        if form.is_valid():
            try:
                hello = Helloworld(
                    descricao=request.POST['descricao'],
                    codigo_exemplo=request.POST['codigo_exemplo'],
                    framework_id=id,
                    usuario_id=user.id,
                    versao_id =request.POST['versao_id']
                ) 
                hello.save()
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar Hello World.")
                messages.error(request, 'Erro ao atualizar hello world. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)


    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':id}))