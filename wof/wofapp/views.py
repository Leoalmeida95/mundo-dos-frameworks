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
from  collections import OrderedDict
from .tokens import account_activation_token
from .forms import *
from .models import *

def chart_view(request):
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    top_linguagens = Linguagem.obter_numero_frameworks()
    top_frameworks = Framework.obter_top10_constribuicoes()
    
    dataSource1 = OrderedDict()
    dataSource2 = OrderedDict()
    chartConfig1 = OrderedDict()
    chartConfig2 = OrderedDict()

    chartConfig1["caption"] = "Top 10 Linguagens com mais Frameworks"
    chartConfig1["xAxisName"] = "Linguagens"
    chartConfig1["yAxisName"] = "Frameworks"
    chartConfig1["showBorder"] = "1"
    chartConfig1["palettecolors"] = "8B008B,98FB98,FF0000,FF7F50,00BFFF,FF69B4,00FF7F,DAA520,FF4500,E0FFFF"

    chartConfig1["toolTipBorderColor"] = "#666666"
    chartConfig1["toolTipBgColor"] = "#efefef"
    chartConfig1["toolTipBgAlpha"] = "80"
    chartConfig1["showToolTipShadow"] = "1"
    chartConfig1["outCnvBaseFont"] = "Arial"
    chartConfig1["placeValuesInside"] = "1"
    chartConfig1["outCnvBaseFontSize"] = "13"
    chartConfig1["outCnvBaseFontColor"] = "#343a40"
    chartConfig1["showBorder"] = "1"
    chartConfig1["canvasbgColor"] = "#ffffff"
    chartConfig1["canvasbgAlpha"] = "10"
    chartConfig1["showCanvasBase"] = "0"
    chartConfig1["canvasBorderThickness"] = "1"
    chartConfig1["showAlternateHGridColor"] = "0"

    chartConfig2["caption"] = "Top 10 Frameworks com mais conteudo"
    chartConfig2["xAxisName"] = "Frameworks"
    chartConfig2["yAxisName"] = "Dados"
    chartConfig2["palettecolors"] = "00FF00,FFD700,D2691E,9932CC,B22222,D8BFD8,FA8072,483D8B,0000FF,DC143C"

    chartConfig2["toolTipBorderColor"] = "#666666"
    chartConfig2["toolTipBgColor"] = "#efefef"
    chartConfig2["toolTipBgAlpha"] = "80"
    chartConfig2["showToolTipShadow"] = "1"
    chartConfig2["outCnvBaseFont"] = "Arial"
    chartConfig2["placeValuesInside"] = "1"
    chartConfig2["outCnvBaseFontSize"] = "13"
    chartConfig2["outCnvBaseFontColor"] = "#343a40"
    chartConfig2["showBorder"] = "1"
    chartConfig2["canvasbgColor"] = "#ffffff"
    chartConfig2["canvasbgAlpha"] = "10"
    chartConfig2["showCanvasBase"] = "0"
    chartConfig2["canvasBorderThickness"] = "1"
    chartConfig2["showAlternateHGridColor"] = "0"

    dataSource1["chart"] = chartConfig1
    dataSource1["data"] = []
    dataSource2["chart"] = chartConfig2
    dataSource2["data"] = []

    for l in top_linguagens:
        data1 = {}
        data1["label"] = l.nome
        data1["value"] = l.total_fram
        dataSource1["data"].append(data1)

    for f in top_frameworks:
        data2 = {}
        data2["label"] = f.nome
        data2["value"] = f.total_contribuicoes
        dataSource2["data"].append(data2)

    column3D_1 = FusionCharts("column3d", "ex1" , "100%", "300", "chart-1", "json", dataSource1)
    column3D_2 = FusionCharts("column3d", "ex2" , "100%", "300", "chart-2", "json", dataSource2)

    return  render(request, 'home.html', {'output1' : column3D_1.render(),'output2' : column3D_2.render(),'linguagens_combo':linguagens_combo})

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
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    linguagens = Linguagem.obter_linguagens()
    return render(request,'faq.html',{'linguagens_combo':linguagens_combo,'linguagens':linguagens})

def registrar_usuario_view(request):
    args = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        publica = request.POST.get("conta_publica","")
        args['form'] = form
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.ativo = False
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
    args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    return render(request,'usuario.html',args)

def ativar_conta_view(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Usuario.obter_usuario_por_id(uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.ativo = True
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

    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    return render(request,'nova_senha.html',{'form':form,'linguagens_combo':linguagens_combo})

def reset_senha_confirmacao_view(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Usuario.obter_usuario_por_id(uid)
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
    
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    return render(request, 'reset_senha_confirmacao.html', {'form':form,'authorized':authorized,'linguagens_combo':linguagens_combo})

@login_required
def atualizar_usuario_view(request):
    user = request.user
    user.profissao = "" if user.profissao is None else user.profissao
    user.formacao = "" if user.formacao  is None else user.formacao 
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

    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    return render(request, 'usuario.html', {'linguagens_combo':linguagens_combo,'form':form, 'publica':user.conta_publica})

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
    
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    return render(request, 'reset_senha_confirmacao.html', {'authorized':True,'form':form, 'linguagens_combo':linguagens_combo})

def montar_framework(framework,versao):
    args = {}
    args['framework'] = framework
    args['versao_selecionada'] = versao
    args['ultimo_helloworld'] = versao.helloworld_set.last() if versao is not None else None
    args['lista_frameworks'] = Linguagem.obter_frameworks_linguagem(framework.linguagem_id)
    args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    args['comentarios'] = Comentario.obter_somente_comentarios(framework.id)
 
    return args

def frameworks_view(request,id):
    framework = Framework.obter_framework_por_id(id)
    versao = framework.versao_set.last()
    args = montar_framework(framework,versao)
    
    return render(request,'frameworks.html', args)

def trocar_versao(request,vs_id):
    versao = Versao.obter_versao_por_id(vs_id)
    framework = versao.framework
    args = {}
    args = montar_framework(framework,versao)
    
    return render(request,'frameworks.html', args)

@login_required
def comentario_view(request,fm_id):
    user = request.user
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                coment = Comentario(
                    texto=request.POST['texto'],
                    framework_id =fm_id,
                    usuario_id = user.id
                )
                coment.save()
                messages.info(request, 'Seu comentário foi enviado com sucesso.')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao criar comentário.")
                messages.error(request, 'Erro ao realizar comentário. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def resposta_view(request,fm_id,cm_id):
    user = request.user
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                coment = Comentario.obter_comentario_por_id(cm_id)
                coment.respostas.create(
                    texto=request.POST['texto'],
                    framework_id= fm_id,
                    usuario_id=user.id
                )
                messages.info(request, 'Sua resposta foi enviada com sucesso.')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao criar resposta.")
                messages.error(request, 'Erro ao realizar resposta. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def helloworld_view(request,fm_id,vs_id):
    user = request.user
    if request.method == 'POST':
        form = HelloWorldForm(request.POST)
        if form.is_valid():
            try:
                hello = Helloworld(
                    descricao=request.POST['descricao'],
                    codigo_exemplo=request.POST['codigo_exemplo'],
                    usuario_id=user.id,
                    versao_id =vs_id
                ) 
                hello.save()
                messages.info(request, 'Hello World editaco com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar Hello World.")
                messages.error(request, 'Erro ao atualizar hello world. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def versao_view(request,fm_id):
    user = request.user
    if request.method == 'POST':
        form = VersaoForm(request.POST)
        if form.is_valid():
            try:
                versao = Versao(
                    numero=request.POST['numero_versao'],
                    framework_id=fm_id,
                    usuario_id=user.id,
                ) 
                versao.save()
                messages.info(request, 'Versão editada com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao editar Versão.")
                messages.error(request, 'Erro ao editar Versão. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def nova_linguagem_view(request):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = LinguagemForm(request.POST)
        args['form'] = form
        if form.is_valid():
            try:
                linguagem = Linguagem(
                    nome=request.POST['nome'],
                    usuario_id=user.id,
                ) 
                linguagem.save()
                messages.info(request, 'Linguagem registrada com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao editar Versão.")
                messages.error(request, 'Erro ao adicionar a Linguagem. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    args['linguagens'] = Linguagem.obter_linguagens()
    return render(request,'faq.html',args)

@login_required
def novo_framework_view(request,lg_id):
    args = {}
    user = request.user
    if request.method == 'POST':
        form = FrameworkForm(lg_id, request.POST)
        args['form'] = form
        if form.is_valid():
            try:
                fram = Framework(
                    nome=request.POST['nome'],
                    linguagem_id = lg_id,
                    usuario_id=user.id,
                ) 
                fram.save()
                messages.info(request, 'Framwork registrado com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao editar Versão.")
                messages.error(request, 'Erro ao adicionar a Linguagem. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    linguagens = Linguagem.obter_linguagens()
    return render(request,'faq.html',{'linguagens_combo':linguagens_combo,'linguagens':linguagens})

@login_required
def define_linguagem_adcframework_view(request,lg_id):
    args={}
    args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    args['linguagens'] = Linguagem.obter_linguagens()
    args['lg_escolhida'] = Linguagem.obter_linguagem_por_id(lg_id)
    args['exibe_modal_fram'] = "show"

    return render(request,'faq.html', args)