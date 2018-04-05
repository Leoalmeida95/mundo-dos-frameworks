# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
import datetime

class Linguagem(models.Model):
    nome = models.CharField(max_length=30)
    
    def __str__(self):
        return self.nome

class Framework(models.Model):
    nome = models.CharField(max_length=30)
    linguagem = models.ForeignKey(Linguagem, on_delete=models.CASCADE, null = True)

    def __str__(self):
        return self.nome
