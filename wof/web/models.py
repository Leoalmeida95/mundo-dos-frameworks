# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
import datetime

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

class Helloworld(models.Model):
    codigo_exemplo = models.CharField(max_length=1000)
    descricao = models.CharField(max_length=5000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.descricao

class Comentario(models.Model):
    texto = models.CharField(max_length=1000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.texto

class Link(models.Model):
    path = models.CharField(max_length=500)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.path

class Versao(models.Model):
    Numero = models.DecimalField(..., max_digits=10, decimal_places=5)
    descricao = models.CharField(max_length=4000)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, null = False)

    def __str__(self):
        return self.Numero

class Perfil(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome

class Denuncia(models.Model):
    data = models.DateField(auto_now=True)
    motivo_denuncia = models.CharField(max_length=500)

class Voto(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, null = False)
