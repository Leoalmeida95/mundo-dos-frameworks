from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import authenticate, get_user_model
from django.utils.text import capfirst

from .models import Usuario,Comentario,Framework

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='password',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label='password_confirm',required=True, 
        widget=forms.PasswordInput(attrs={'id': 'password2'}))
    first_name = forms.CharField(label='first_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'first_name'}))
    last_name = forms.CharField(label='last_name',required=True, 
        widget=forms.TextInput(attrs={'id': 'last_name'}))
    cpf = forms.CharField(label='cpf',required=True, widget=forms.TextInput(attrs={'id': 'cpf'}))
    conta_publica = forms.BooleanField(label='conta_publica',initial=True, required=True)
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
    class Meta:
        model = Usuario
        fields = ['first_name','last_name','cpf','conta_publica','formacao','profissao', 'email',]

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        password = ReadOnlyPasswordHashField(label='password')
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
        if not user.is_active:
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
