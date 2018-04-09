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
            raise ValueError(_('Email é obrigatório.'))

        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Perfil(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome

class Usuario(PermissionsMixin, AbstractBaseUser):
    nome = models.CharField(max_length=30)
    cpf = models.CharField(max_length=30)
    ativo = models.BooleanField(default = False)
    email = models.EmailField(
        verbose_name=_('Email'),
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('Nome'),
        max_length=50,
        blank=False,
        help_text=_('Informe seu nome'),
    )
    last_name = models.CharField(
        verbose_name=_('Sobrenome'),
        max_length=50,
        blank=False,
        help_text=_('Informe seu sobrenome'),
    )
    USERNAME_FIELD = 'email'
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null = False)
    objects = EmailUserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.nome
        
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