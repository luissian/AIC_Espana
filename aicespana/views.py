import statistics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import *

def index(request):
    return render(request,'aicespana/index.html')

@login_required
def listado_voluntarios(request):

    return render(request,'listadoVoluntarios.html')

@login_required
def busqueda_personal(request):
    return render(request,'resultadoBusqueda.html')

#@login_required
def nuevo_voluntario(request):
    if request.method == 'POST' and request.POST['action'] == 'altaVoluntario':
        confirmation_data = ''
        info_to_fetch = ['nombre', 'apellidos','nif','nacimiento','calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil']
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field]
        PersonalExterno_obj = PersonalExterno.objects.create_new_external_pesonel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellidos'] = request.POST['apellidos']
        import pdb; pdb.set_trace()
        return render(request,'aicespana/nuevoVoluntario.html',{'confirmation_data': confirmation_data})
    return render(request,'aicespana/nuevoVoluntario.html')
