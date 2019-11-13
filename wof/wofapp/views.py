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
    top_linguagens = Linguagem.obter_top10_mais_frameworks()
    top_frameworks = Framework.obter_top10_constribuicoes()
    
    dataSource1 = OrderedDict()
    dataSource2 = OrderedDict()
    chartConfig1 = OrderedDict()
    chartConfig2 = OrderedDict()

    chartConfig1["caption"] = "Top 10 Linguagens com mais Frameworks"
    chartConfig1["xAxisName"] = "Linguagens"
    chartConfig1["yAxisName"] = "Quantidade de Frameworks"
    chartConfig1["showBorder"] = "1"
    chartConfig1["palettecolors"] = "8B008B,00FF7F,FF0000,FF7F50,FF4500,FF69B4,98FB98,DAA520,B22222,E0FFFF"

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

    chartConfig2["caption"] = "Top 10 Frameworks com mais dados inseridos"
    chartConfig2["xAxisName"] = "Frameworks"
    chartConfig2["yAxisName"] = "Quantidade de Dados"
    chartConfig2["palettecolors"] = "00FF00,00BFFF,DC143C,9932CC,FFD700,0000FF,FA8072,483D8B,D8BFD8,D2691E"

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

    path = request.POST.get('next', '/')
    next = path if path != '/buscar_framework/' else '/'
    return HttpResponseRedirect(next)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def faq_view(request):
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    linguagens = Linguagem.obter_linguagens()
    return render(request,'faq.html',{'linguagens_combo':linguagens_combo,'linguagens':linguagens})

def favoritos_view(request):
    linguagens_combo = Linguagem.obter_linguagens_minimo_um_framework()
    favoritos = request.user.favoritado_por.all().order_by('nome')
    return render(request,'favoritos.html',{'linguagens_combo':linguagens_combo,'favoritos':favoritos})

def registrar_usuario_view(request):
    args = {}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        publica = request.POST.get("conta_publica","")
        args['form'] = form
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.adicionar()
                form.enviar_email(user,request=request)
                messages.info(request, 'Muito bem! Agora para concluir seu registro, por favor confirme sua conta no email que enviamos pra você.')
                return HttpResponseRedirect(reverse('wofapp:home'))
            except Exception as e:
                erro = str(e)
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
        user = Usuario.obter_usuario(uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.ativar_conta()
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
        user = Usuario.obter_usuario(uid)
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

def montar_framework(framework,versao,u_id):
    args = {}
    args['framework'] = framework
    args['favorito'] = framework.favoritado_por.filter(id=u_id).first()
    args['versao_selecionada'] = versao
    args['ultimo_helloworld'] = versao.helloworld_set.last() if versao is not None else None
    args['vantagens'] = versao.opiniao_set.filter(eh_favoravel=True).all() if versao is not None else None
    args['desvantagens'] = versao.opiniao_set.filter(eh_favoravel=False).all() if versao is not None else None
    args['comentarios'] = framework.comentario_set.exclude(texto__exact='').exclude(respostas_id__isnull=False)
    args['links'] = framework.link_set.all().annotate(qtd_voto=Count('voto')).order_by('-qtd_voto')

    args['lista_frameworks'] = Linguagem.obter_frameworks_linguagem(framework.linguagem_id)
    args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
 
    return args

def frameworks_view(request,id):
    args = {}
    framework = Framework.obter_framework(id)
    args = montar_framework(framework,framework.versao_set.last(),request.user.id)
    
    return render(request,'frameworks.html', args)

def trocar_versao_view(request,vs_id):
    args = {}
    versao = Versao.obter_versao(vs_id)
    framework = versao.framework
    args = montar_framework(framework,versao,request.user.id)
    
    return render(request,'frameworks.html', args)

def buscar_framework_view(request):
    if request.method == 'POST':
        pesquisa = request.POST['pesquisa']
        framework = Framework.buscar_por_nome(pesquisa)
        args = {}
        if framework is None:
            messages.warning(request, 'Não existe nenhum Framework que contenha \''+pesquisa+'\'.')
            path = request.POST.get('next', '/')
            next = path if path != '/buscar_framework/' else '/'
            return HttpResponseRedirect(next)

        else:
            args = montar_framework(framework,framework.versao_set.last(),request.user.id)
            return render(request,'frameworks.html', args)

@login_required
def comentario_view(request,fm_id):
    user = request.user
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                Comentario.adicionar(request.POST['texto'],fm_id,user.id)
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
                Comentario.adicionar_resposta(cm_id,request.POST['texto'],fm_id,user.id)
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
                Helloworld.adicionar(request.POST['descricao'],request.POST['codigo_exemplo'],user.id,vs_id)
                messages.info(request, 'Hello World editado com sucesso!')
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
        form = VersaoForm(fm_id, request.POST)
        if form.is_valid():
            try:
                Versao.adicionar(request.POST['numero_versao'],fm_id,user.id)
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
def editar_versao_view(request,vs_id,fm_id):
    user = request.user
    if request.method == 'POST':
        form = VersaoForm(fm_id, request.POST)
        if form.is_valid():
            try:
                Versao.editar(request.POST['numero_versao'],vs_id,user.id)
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
                Linguagem.adicionar(request.POST['nome'],user.id)
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
                Framework.adicionar(request.POST['nome'],lg_id,user.id)
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
    args['lg_escolhida'] = Linguagem.obter_linguagem(lg_id)
    args['exibe_modal_fram'] = "show"

    return render(request,'faq.html', args)

@login_required
def opiniao_view(request,fm_id,vs_id):
    args={}
    user = request.user
    if request.method == 'POST':
        eh_favoravel = True if request.POST.get("opiniao","") == 'True' else False 
        form = OpiniaoForm(request.POST)
        if form.is_valid():
            try:
                Opiniao.adicionar(request.POST['texto'], eh_favoravel, user.id,vs_id)
                if eh_favoravel == True: 
                    messages.info(request, 'Vantagens editadas com sucesso!')
                else:
                    messages.info(request, 'Desvantagens editadas com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar vantagens e desvantagens.")
                messages.error(request, 'Erro ao atualizar vantagens e desvantagens. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)
    else:
        form = OpiniaoForm()

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def editar_opiniao_view(request,op_id,fm_id):
    user = request.user
    if request.method == 'POST':
        form = OpiniaoForm(request.POST)
        if form.is_valid():
            try:
                Opiniao.editar(request.POST['texto'],op_id,user.id)
                messages.info(request, 'Edição das Vantagens e Desvantagens realizada com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar vantagens e desvantagens.")
                messages.error(request, 'Erro ao atualizar vantagens e desvantagens. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))


@login_required
def funcionalidade_view(request,fm_id,vs_id):
    args={}
    user = request.user
    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST)
        if form.is_valid():
            try:
                Funcionalidade.adicionar(request.POST['descricao'],user.id,vs_id)
                messages.info(request, 'Funcionalidades editadas com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar as funcionalidades.")
                messages.error(request, 'Erro ao atualizar as funcionalidades. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)
    else:
        form = FuncionalidadeForm()

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def editar_funcionalidade_view(request,fun_id,fm_id):
    user = request.user
    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST)
        if form.is_valid():
            try:
                Funcionalidade.editar(request.POST['descricao'],fun_id,user.id)
                messages.info(request, 'Funcionalidade editada com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar funcionalidade.")
                messages.error(request, 'Erro ao atualizar funcionalidade. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def favoritar_framework_view(request,fm_id):
    try:
        Framework.adicionar_favorito(fm_id,request.user.id)
        messages.info(request, 'Framework adicionado aos favoritos!')
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao adicionar framework favorito.")
        messages.error(request, 'Erro ao adicionar framework favorito. Tente novamente mais tarde.')
                
    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def desfavoritar_framework_view(request,fm_id):
    try:
        Framework.excluir_favorito(fm_id,request.user.id)
        messages.info(request, 'Framework retirado dos favoritos!')
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao excluir framework favorito.")
        messages.error(request, 'Erro ao excluir framework favorito. Tente novamente mais tarde.')

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def excluir_comentario_view(request,rs_id,fm_id):
    try:
        Comentario.excluir(rs_id)
        messages.info(request, 'Comentário excluído com sucesso!')
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao excluir comentário.")
        messages.error(request, 'Erro ao excluir comentário. Tente novamente mais tarde.')

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def link_view(request,fm_id):
    args={}
    user = request.user
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            try:
                Link.adicionar(request.POST['caminho'],user.id,fm_id)
                messages.info(request, 'Links editados com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar os Links.")
                messages.error(request, 'Erro ao atualizar os links. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)
    else:
        form = LinkForm()

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def editar_link_view(request,li_id,fm_id):
    user = request.user
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            try:
                Link.editar(request.POST['caminho'],li_id,user.id)
                messages.info(request, 'Links editados com sucesso!')
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("Erro ao atualizar os Links.")
                messages.error(request, 'Erro ao atualizar os links. Tente novamente mais tarde.')
        else:
            erroMsg = form.errors['__all__'].data[0].message
            messages.warning(request, erroMsg)

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def votar_link_view(request,li_id,fm_id):
    try:
        if Voto.verifica_voto(li_id,request.user.id):
            messages.warning(request, 'Você já votou nesse link!')
        else:
            Voto.adicionar(li_id,request.user.id)
            messages.info(request, 'Voto computado com sucesso!')
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao excluir framework favorito.")
        messages.error(request, 'Erro ao excluir framework favorito. Tente novamente mais tarde.')

    return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':fm_id}))

@login_required
def denuncia_comentario_view(request,cm_id):
    user = request.user
    args={}
    try:
        if request.method == 'POST':
            form = DenunciaForm(request.POST)
            if form.is_valid():
                Denuncia.denunciar_comentario(request.POST['motivo'],cm_id,user.id)
                messages.info(request, 'O conteúdo foi denunciado com sucesso! Obrigado por sua contribuição. o memso será avaliado pelos administradores.')
                return HttpResponseRedirect('/')
            else:
                erroMsg = form.errors['__all__'].data[0].message
                messages.warning(request, erroMsg)
        else:
            denuncia = Denuncia.verifica_denuncia_comentario(cm_id,user.id)
            if denuncia:
                messages.warning(request, 'Você já denunciou esse conteúdo!')
                return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':denuncia.Comentario.framework_id}))
            else:
                args['denuncia'] = "Comentario"
                args['conteudo'] = Comentario.obter_texto_denunciado(cm_id)
                args['cm_id'] = cm_id
                args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao denunciar comentário.")
        messages.error(request, 'Erro ao denunciar comentário. Tente novamente mais tarde.')
        return HttpResponseRedirect('/')

    return  render(request, 'denuncia.html', args)


@login_required
def denuncia_opiniao_view(request,op_id):
    user = request.user
    args={}
    try:
        if request.method == 'POST':
            form = DenunciaForm(request.POST)
            if form.is_valid():
                Denuncia.denunciar_opiniao(request.POST['motivo'],op_id,user.id)
                messages.info(request, 'O conteúdo foi denunciado com sucesso! Obrigado por sua contribuição. o memso será avaliado pelos administradores.')
                return HttpResponseRedirect('/')
            else:
                erroMsg = form.errors['__all__'].data[0].message
                messages.warning(request, erroMsg)
        else:
            denuncia = Denuncia.verifica_denuncia_opiniao(op_id,user.id)
            if denuncia:
                messages.warning(request, 'Você já denunciou esse conteúdo!')
                return HttpResponseRedirect(reverse('wofapp:frameworks', kwargs={'id':denuncia.opiniao.versao.framework_id}))
            else:
                args['denuncia'] = "Opinião"
                args['conteudo'] = Opiniao.obter_texto_denunciado(op_id)
                args['op_id'] = op_id
                args['linguagens_combo'] = Linguagem.obter_linguagens_minimo_um_framework()
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Erro ao denunciar opinião.")
        messages.error(request, 'Erro ao denunciar opinião. Tente novamente mais tarde.')
        return HttpResponseRedirect('/')

    return  render(request, 'denuncia.html', args)