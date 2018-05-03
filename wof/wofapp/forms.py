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
from .tokens import account_activation_token
from django.template import loader

from .models import Usuario,Comentario,Framework

CHOICES=[(True,'Sim'),
         (False,'Não')]

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='password1',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label='password2',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password2'}))
    first_name = forms.CharField(label='first_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'first_name'}))
    last_name = forms.CharField(label='last_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'last_name'}))
    cpf = forms.CharField(label='cpf',required=True, widget=forms.TextInput(attrs={'id': 'cpf'}))
    conta_publica = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, initial = True)
    formacao = forms.CharField(label='formacao',required=False, 
        widget=forms.TextInput(attrs={'id': 'formacao'}))
    profissao = forms.CharField(label='profissao',required=False, 
        widget=forms.TextInput(attrs={'id': 'profissao'}))
    email = forms.CharField(label='email',required=True, widget=forms.TextInput(attrs={'id': 'email'}))
    class Meta:
        model = Usuario
        fields = ['first_name','last_name','cpf','conta_publica','formacao','profissao', 'email','password1','password2']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não são iguais.")
        return password2
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('first_name')

        if email and Usuario.objects.filter(email=email).exclude(first_name=username).count():
            raise forms.ValidationError("Este email já está em uso, por favor escolha outro.")
        return email

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CustomUserCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label='password')
    first_name = forms.CharField(label='first_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'first_name'}))
    last_name = forms.CharField(label='last_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'last_name'}))
    cpf = forms.CharField(label='cpf',required=True, widget=forms.TextInput(attrs={'id': 'cpf'}))
    conta_publica = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    formacao = forms.CharField(label='formacao',required=False, 
        widget=forms.TextInput(attrs={'id': 'formacao'}))
    profissao = forms.CharField(label='profissao',required=False, 
        widget=forms.TextInput(attrs={'id': 'profissao'}))
    email = forms.CharField(label='email',required=True, widget=forms.TextInput(attrs={'id': 'email'}))
    class Meta:
        model = Usuario
        fields = ['first_name','last_name','cpf','conta_publica','formacao','profissao', 'email','password']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(required=True,
                widget=forms.TextInput(attrs={'id': 'username'}))
    password = forms.CharField(required=True,
                widget=forms.PasswordInput(attrs={'id': 'password'}))


    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Login ou senha incorretos. Por favor verifique seus dados.',
                    code='Essa conta está inativa.')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_activeUser:
            raise forms.ValidationError(
                self.error_messages['Essa conta está inativa.'],
                code='Essa conta está inativa.',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):

        return self.user_cache

class ComentarioForm(forms.ModelForm):

    class Meta:
        model = Comentario
        fields = ['texto']

    def clean(self):        
        texto = self.cleaned_data.get('texto')
        if texto is None:
            raise forms.ValidationError('Escreva alguma pergunta ou comentário.', code='texto')
        
        return self.cleaned_data

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='email', max_length=60)

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

    def get_users(self, email):

        active_users = get_user_model()._default_manager.filter(
            email=email, is_activeUser=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='WOF - nova senha',
             email_template_name='corpo_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):

        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': current_site.domain,
                'site_name': current_site.name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)