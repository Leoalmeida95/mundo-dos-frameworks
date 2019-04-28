# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone

class EmailUserManager(BaseUserManager):
    def create_user(self, email, password=None, primeiro_nome=None, ultimo_nome=None, cpf = None, **kwargs):
        
        if not email:
            raise ValueError('Email é obrigatório.')

        if not primeiro_nome:
            raise ValueError('Primeiro Nome é obrigatório.')

        if not ultimo_nome:
            raise ValueError('Ultimo Nome é obrigatório.')

        if not cpf:
            raise ValueError('CPF é obrigatório.')

        email = self.normalize_email(email)
        user = self.model(email=email, primeiro_nome=primeiro_nome, ultimo_nome=ultimo_nome, cpf = cpf, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, primeiro_nome, ultimo_nome, cpf):
        user = self.create_user(email, password=password, primeiro_nome=primeiro_nome, ultimo_nome=ultimo_nome, cpf=cpf)
        user.administrador = True
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
    primeiro_nome = models.CharField(
        verbose_name=_('Nome'),
        max_length=50,
        blank=False,
        help_text=_('O campo Nome é obrigatório.'),)
    ultimo_nome = models.CharField(
        verbose_name=_('Sobrenome'),
        max_length=50,
        blank=False,
        help_text=_('O campo Sobrenome é obrigatório.'),)
    ativo = models.BooleanField(default=True)
    administrador = models.BooleanField(default=False)
    conta_publica = models.BooleanField(default=False)
    formacao = models.CharField(max_length=80,null = True)
    profissao = models.CharField(max_length=80,null = True)
    data_cadastro = models.DateTimeField(default=timezone.now)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['primeiro_nome','ultimo_nome','cpf']

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.primeiro_nome +" "+ self.ultimo_nome

    def get_profissao(self):
        if not self.profissao:
            return ""
        else:
            return self.profissao        

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
        return self.administrador

    @property
    def is_superuser(self):
        return self.administrador

    @property
    def is_active(self):
        return self.ativo

class Linguagem(models.Model):
    nome = models.CharField(max_length=30)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    
    def __str__(self):
        return self.nome

class Framework(models.Model):
    nome = models.CharField(max_length=30)
    linguagem = models.ForeignKey(Linguagem, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    favoritado_por = models.ManyToManyField(Usuario, blank=True, related_name="favoritado_por")

    def __str__(self):
        return self.nome

class Versao(models.Model):
    numero = models.DecimalField(default=0, max_digits=10, decimal_places=3)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return str(self.numero)

class Funcionalidade(models.Model):
    descricao = models.CharField(max_length=5000)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Helloworld(models.Model):
    codigo_exemplo = models.CharField(max_length=50000)
    descricao = models.CharField(max_length=50000)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.OneToOneField(Versao, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Opiniao(models.Model):
    texto = models.CharField(max_length=1000)
    eh_favoravel = models.BooleanField(default=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.nome    

class Link(models.Model):
    caminho = models.CharField(max_length=800)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.path

class Comentario(models.Model):
    texto = models.CharField(max_length=1000)
    data = models.DateTimeField(default=timezone.now)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    respostas = models.ManyToManyField("self",symmetrical=False)

    def __str__(self):
        return self.texto

class Voto(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null = False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)

class Denuncia(models.Model):
    data = models.DateTimeField(default=timezone.now)
    motivo = models.CharField(max_length=500)
    quem_denunciou = models.ForeignKey(Usuario, on_delete=models.CASCADE, null = False)
    linguagem = models.ForeignKey(Linguagem, on_delete=models.CASCADE, blank=True, null=True)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, blank=True, null=True)
    versao = models.ForeignKey(Versao, on_delete=models.CASCADE, blank=True, null=True)
    helloworld = models.ForeignKey(Helloworld, on_delete=models.CASCADE, blank=True, null=True)
    funcionalidade = models.ForeignKey(Funcionalidade, on_delete=models.CASCADE, blank=True, null=True)
    opiniao = models.ForeignKey(Opiniao, on_delete=models.CASCADE, blank=True, null=True)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, blank=True, null=True)
    Comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.motivo
