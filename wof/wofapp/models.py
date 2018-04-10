# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

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

class Perfil(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome

class Usuario(PermissionsMixin, AbstractBaseUser):
    cpf = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    conta_publica = models.BooleanField(default=False)
    formacao = models.CharField(max_length=80,null = True)
    profissao = models.CharField(max_length=80,null = True)
    email = models.EmailField(
        verbose_name=_('Email'),
        max_length = 100,
        unique=True,)
    first_name = models.CharField(
        verbose_name=_('Nome'),
        max_length=50,
        blank=False,
        help_text=_('Informe seu nome'),)
    last_name = models.CharField(
        verbose_name=_('Sobrenome'),
        max_length=50,
        blank=False,
        help_text=_('Informe seu sobrenome'),)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null = False,default = 1)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','cpf']

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

    @property
    def is_staff(self):
        "O usuário é um administrador?"
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_active(self):
        return self.is_active

class Linguagem(models.Model):
    nome = models.CharField(max_length=30)
    
    def __str__(self):
        return self.nome

class Framework(models.Model):
    nome = models.CharField(max_length=30)
    linguagem = models.ForeignKey(Linguagem, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.nome

class Opiniao(models.Model):
    pros = models.CharField(max_length=400)
    contras = models.CharField(max_length=400)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.nome    

class Helloworld(models.Model):
    codigo_exemplo = models.CharField(max_length=1000)
    descricao = models.CharField(max_length=5000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Comentario(models.Model):
    texto = models.CharField(max_length=1000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.texto

class Link(models.Model):
    path = models.CharField(max_length=500)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.path

class Versao(models.Model):
    numero = models.DecimalField(default=0, max_digits=10, decimal_places=5)
    descricao = models.CharField(max_length=4000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao


class Denuncia(models.Model):
    data = models.DateField(auto_now=True)
    motivo_denuncia = models.CharField(max_length=500)
    usuarios = models.ManyToManyField(Usuario)

    def __str__(self):
        return self.nome

class Voto(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.nome