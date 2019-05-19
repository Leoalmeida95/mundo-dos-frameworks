from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import format_html, format_html_join
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.template.loader import render_to_string

from .tokens import account_activation_token
from .models import *
from .util import CpfValido

CHOICES=[(True,'Sim'),
         (False,'Não')]

# Formulários para Usuário       
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='password1',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label='password2',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password2'}))
    primeiro_nome = forms.CharField(label='primeiro_nome',required=True, 
        widget=forms.TextInput(attrs={'id': 'primeiro_nome'}))
    ultimo_nome = forms.CharField(label='ultimo_nome',required=True, 
        widget=forms.TextInput(attrs={'id': 'ultimo_nome'}))
    cpf = forms.CharField(label='cpf',required=True,
     widget=forms.TextInput(attrs={'id': 'cpf'}))
    conta_publica = forms.ChoiceField(choices=CHOICES,
     widget=forms.RadioSelect, initial = True)
    formacao = forms.CharField(label='formacao',required=False, 
        widget=forms.TextInput(attrs={'id': 'formacao'}))
    profissao = forms.CharField(label='profissao',required=False, 
        widget=forms.TextInput(attrs={'id': 'profissao'}))
    email = forms.CharField(label='email',required=True,
     widget=forms.TextInput(attrs={'id': 'email'}))
    class Meta:
        model = Usuario
        fields = ['primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao', 'email','password1','password2']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não são iguais.')
        return password2
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('primeiro_nome')
 
        if email and Usuario.verifica_email_valido(email,username):
            raise forms.ValidationError('Este email já está em uso, por favor escolha outro.')
        return email
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        username = self.cleaned_data.get('primeiro_nome')

        if cpf and Usuario.verifica_cpf_valido(cpf,username):
            raise forms.ValidationError('Este CPF já está em uso, por favor verifique se foi digitado corretamente.')
        # elif CpfValido().validate(cpf):
        #     raise forms.ValidationError('Número de CPF inválido.')
        return cpf

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CustomUserCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def enviar_email(self, user, request = None,use_https=False):
        current_site = get_current_site(request)
        message = render_to_string('ativar_conta_email.html', {
            'user': user,
            'domain': current_site.domain,
            'site_name': current_site.name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
            'protocol': 'https' if use_https else 'http',
        })
        user.email_user('Ative sua conta no WOF System',message,from_email = 'wofsystem@gmail.com')

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(label='password')
    primeiro_nome = forms.CharField(label='primeiro_nome',required=True, 
        widget=forms.TextInput(attrs={'id': 'primeiro_nome'}))
    ultimo_nome = forms.CharField(label='ultimo_nome',required=True, 
        widget=forms.TextInput(attrs={'id': 'ultimo_nome'}))
    cpf = forms.CharField(label='cpf',required=True,
     widget=forms.TextInput(attrs={'id': 'cpf'}))
    conta_publica = forms.ChoiceField(choices=CHOICES,
     widget=forms.RadioSelect)
    formacao = forms.CharField(label='formacao',required=False, 
        widget=forms.TextInput(attrs={'id': 'formacao'}))
    profissao = forms.CharField(label='profissao',required=False, 
        widget=forms.TextInput(attrs={'id': 'profissao'}))
    email = forms.CharField(label='email',required=True,
     widget=forms.TextInput(attrs={'id': 'email'}))
    class Meta:
        model = Usuario
        fields = ['primeiro_nome','ultimo_nome','cpf','conta_publica','formacao','profissao', 'email','password']

    def clean_password(self):
        return self.initial["password"]

class AuthenticationForm(forms.Form):
    
    username = forms.CharField(required=True,
                widget=forms.TextInput(attrs={'id': 'username'}))
    password = forms.CharField(required=True,
                widget=forms.PasswordInput(attrs={'id': 'password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(
                    'Login ou senha incorretos. Por favor verifique seus dados.')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.ativo:
            raise forms.ValidationError(
                'Sua conta não está ativa. Por favor, verifique seu email para completar seu registro.',
                code='Essa conta está inativa.') 

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='email', max_length=60)

    def clean(self):
        email = self.cleaned_data["email"]
        active_users = get_user_model()._default_manager.filter(
            email=email, ativo=True)

        if active_users:
            self.user_cache = active_users
        else:
            raise forms.ValidationError('Esse email não está registrado.')

        return self.cleaned_data

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        subject = subject_template_name
        # Email subject *must not* contain newlines
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self):
        return (u for u in self.user_cache if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='WOF - nova senha',
             email_template_name='reset_senha_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email = 'wofsystem@gmail.com', request=None, html_email_template_name=None):

        email = self.cleaned_data["email"]
        for user in self.get_users():
            if not domain_override:
                current_site = get_current_site(request)
            else:
                site_name = domain = domain_override

            context = {
                'user': user,
                'email': user.email,
                'domain': current_site.domain,
                'site_name': current_site.name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)

class SetPasswordForm(UserCreationForm):
    
    password1 = forms.CharField(label='password1',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label='password2',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password2'}))
    class Meta:
        model = Usuario
        fields = ['password1','password2']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não são iguais.')

        return self.cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['password1'])
        if commit:
            self.user.save()

        return self.user

# Formulários para Framework       
class ComentarioForm(forms.ModelForm):
    
    texto = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'texto'}))

    class Meta:
        model = Comentario
        fields = ['texto']

    def clean(self):        
        texto = self.cleaned_data.get('texto')
        if texto is None:
            raise forms.ValidationError('Escreva algo no seu comentário.', code='texto')
        
        return self.cleaned_data

class HelloWorldForm(forms.ModelForm):
    
    descricao = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'descricao'}))
    codigo_exemplo = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'codigo_exemplo'}))

    class Meta:
        model = Helloworld
        fields = ['descricao','codigo_exemplo']

    def clean(self):        
        descricao = self.cleaned_data.get('descricao')
        codigo_exemplo = self.cleaned_data.get('codigo_exemplo')

        if descricao is None or codigo_exemplo is None:
            raise forms.ValidationError('A descrição e o exemplo de código são obrigatórios.')
        return self.cleaned_data

class VersaoForm(forms.ModelForm):
    
    numero_versao = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'numero_versao'}))
    fram_id = forms.IntegerField(required=False, 
        widget=forms.TextInput())

    class Meta:
        model = Versao
        fields = ['numero_versao']

    def __init__(self, fram_id, *args, **kwargs):
        self.fram_id = fram_id
        super(VersaoForm, self).__init__(*args, **kwargs)

    def clean(self):        
        numero_versao = self.cleaned_data.get('numero_versao')
        fram_id = self.fram_id

        if numero_versao is None:
            raise forms.ValidationError('O Número da Versão é obrigatório.')
        elif Versao.verifica_numero(numero_versao,fram_id):
            raise forms.ValidationError('O framework já possui essa versão.')
        return self.cleaned_data

class LinguagemForm(forms.ModelForm):
    
    nome = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'nome'}))

    class Meta:
        model = Linguagem
        fields = ['nome']

    def clean(self):        
        nome = self.cleaned_data.get('nome')

        if nome is None:
            raise forms.ValidationError('O nome é obrigatório.')
        elif Linguagem.verifica_nome(nome):
            raise forms.ValidationError('Essa Linguagem já está registrada no sistema.')
        return self.cleaned_data


class FrameworkForm(forms.ModelForm):
    
    nome = forms.CharField(required=False, 
        widget=forms.TextInput(attrs={'name': 'nome'}))
    linguagem_id = forms.IntegerField(required=False, 
        widget=forms.TextInput())

    class Meta:
        model = Framework
        fields = ['nome','linguagem_id']

    def __init__(self, linguagem_id, *args, **kwargs):
        self.linguagem_id = linguagem_id
        super(FrameworkForm, self).__init__(*args, **kwargs)

    def clean(self):        
        nome = self.cleaned_data.get('nome')
        linguagem_id = self.linguagem_id

        if nome is None or nome is '' or linguagem_id is None:
            raise forms.ValidationError('Os campos são obrigatórios.')
        elif Framework.verifica_nome(nome):
            raise forms.ValidationError('Essa Framework já está registrada no sistema.')
        elif Linguagem.obter_linguagem_por_id(linguagem_id) is None:
            raise forms.ValidationError('Escolha uma Linguagem válida para o Framework.')
        return self.cleaned_data

class OpiniaoForm(forms.ModelForm):

    opiniao = forms.ChoiceField(choices=CHOICES,
     widget=forms.RadioSelect, initial = True) 
    texto = forms.CharField(required=True, 
        widget=forms.TextInput(attrs={'name': 'texto'}))

    class Meta:
        model = Opiniao
        fields = ['texto','eh_favoravel']

    def clean(self):        
        texto = self.cleaned_data.get('texto')
        if texto is None:
            raise forms.ValidationError('Escreva algo na opinião.', code='texto')
        
        return self.cleaned_data

