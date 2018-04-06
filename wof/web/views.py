from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render('web/home.html')

def index(request):
    return HttpResponse('Heloo')