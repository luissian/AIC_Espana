import statistics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,'aicespana/index.html')
