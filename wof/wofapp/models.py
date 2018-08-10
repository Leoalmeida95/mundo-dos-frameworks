# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone

class Linguagem(models.Model):
    nome = models.CharField(max_length=30)
    
    def __str__(self):
        return self.nome

class Framework(models.Model):
    nome = models.CharField(max_length=30)
    linguagem = models.ForeignKey(Linguagem, on_delete=models.CASCADE, null = False,related_name='frameworks')

    def __str__(self):
        return self.nome

class Perfil(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome

class EmailUserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        email = kwargs["email"]
        email = self.normalize_email(email)
        password = kwargs["password"]
        kwargs.pop("password")

        if not email:
            raise ValueError('Email é obrigatório.')

        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        user = self.create_user(**kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Usuario(PermissionsMixin, AbstractBaseUser):
    cpf = models.CharField(
        max_length=14,
        blank=False,
        help_text=_('O campo CPF é obriagatório.'),
        unique = True,)
    email = models.EmailField(
        verbose_name=_('Email'),
        max_length = 60,
        unique=True,
    help_text=_('O campo Email é obrigatório.'),)
    first_name = models.CharField(
        verbose_name=_('Nome'),
        max_length=50,
        blank=False,
        help_text=_('O campo Nome é obrigatório.'),)
    last_name = models.CharField(
        verbose_name=_('Sobrenome'),
        max_length=50,
        blank=False,
        help_text=_('O campo Sobrenome é obrigatório.'),)
    is_activeUser = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    conta_publica = models.BooleanField(default=False)
    formacao = models.CharField(max_length=80,null = True)
    profissao = models.CharField(max_length=80,null = True)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null = False,default = 1)
    data_cadastro = models.DateTimeField(default=timezone.now)
    favoritos = models.ManyToManyField(Framework, blank=True)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','cpf']

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.first_name +" "+ self.last_name

    def has_module_perms(self, app_label):
        "O usuário tem permissão para visualizar o app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def has_perm(self, perm, obj=None):
        "O usuário possui uma permissão específica?"
        # Simplest possible answer: Yes, always
        return True

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    @property
    def is_staff(self):
        "O usuário é um administrador?"
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_active(self):
        return self.is_activeUser

class Versao(models.Model):
    numero = models.DecimalField(default=0, max_digits=10, decimal_places=5)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False,related_name='versoes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.numero

class Funcionalidades(models.Model):
    descricao = models.CharField(max_length=5000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False,related_name='funcionalidades')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Helloworld(models.Model):
    codigo_exemplo = models.CharField(max_length=50000)
    descricao = models.CharField(max_length=50000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False,related_name='helloworlds')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Opiniao(models.Model):
    texto = models.CharField(max_length=1000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False, related_name='opinioes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)
    models.BooleanField(default=True)
    eh_favoravel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome    

class Link(models.Model):
    path = models.CharField(max_length=800)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False,related_name='links')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.path

class Comentario(models.Model):
    texto = models.CharField(max_length=1000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False,related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    data = models.DateTimeField(default=timezone.now)
    respostas = models.ManyToManyField("self",symmetrical=False)

    def __str__(self):
        return self.texto

class Voto(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

class Denuncia(models.Model):
    data = models.DateTimeField(default=timezone.now)
    motivo_denuncia = models.CharField(max_length=500)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, null = False)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null = False)
    helloworld = models.ForeignKey(Helloworld, on_delete=models.CASCADE, null = False)
    funcionalidades = models.ForeignKey(Funcionalidades, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)
    
    def __str__(self):
        return self.motivo_denuncia

    def __str__(self):
        return self.link