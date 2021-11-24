import statistics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import *
from .utils.generic_functions import *

def index(request):
    return render(request,'aicespana/index.html')

@login_required
def listado_voluntarios(request):

    return render(request,'listadoVoluntarios.html')

@login_required
def busqueda_personal(request):
    return render(request,'resultadoBusqueda.html')

def cargos_personal_iglesia(request):
    if request.method == 'POST' and request.POST['action'] == 'altaVoluntario':
        return render(request, 'aicespana/cargosPersonalIglesia.html')
    return render(request, 'aicespana/cargosPersonalIglesia.html')

def cargos_voluntarios(request):
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellidos'] == '':
            return render(request, 'aicespana/cargosVoluntarios.html')
        if request.POST['nif'] != '':
            if PersonalExterno.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalExterno.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
                personal_available_settings = get_responsablity_data_for_voluntary(personal_objs[0])
                personal_available_settings.update(get_external_personal_responsability(personal_objs[0]))
                import pdb; pdb.set_trace()
                return render(request, 'aicespana/cargosVoluntarios.html', {'personal_available_settings':personal_available_settings})

            error = ['No hay nigún voluntario que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
        personal_objs = PersonalExterno.objects.all()
        if request.POST['apellidos'] != '':
            personal_objs = personal_objs.filter(apellidos__iexact = request.POST['apelidos'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el apellido', request.POST['apellidos']]
                return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el nombre', request.POST['nombre']]
                return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
        if len(personal_objs) >1 :
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])
            return render(request, 'aicespana/cargosVoluntarios.html', {'personal_list':personal_list})
        personal_available_settings = get_responsablity_data_for_voluntary(personal_objs[0])
        personal_available_settings.update(get_external_personal_responsability(personal_objs[0]))
        personal_available_settings['user_id'] = personal_objs[0].get_personal_id()
        return render(request, 'aicespana/cargosVoluntarios.html', {'personal_available_settings':personal_available_settings})
    if request.method == 'POST' and request.POST['action'] == 'asignarCargos':
        user_obj = get_user_obj_from_id(request.POST['user_id'])
        data = {}
        data['cargo'] = request.POST['cargo']
        data['actividad'] = request.POST['actividad']
        data['grupo'] = request.POST['grupo']
        data['proyecto'] = request.POST['proyecto']
        data['colaboracion'] = request.POST['colaboracion']
        user_obj.update_information(data)
        updated_data = get_external_personal_responsability(user_obj)

        return render(request, 'aicespana/cargosVoluntarios.html', {'updated_data':updated_data})
    return render(request, 'aicespana/cargosVoluntarios.html')

def listado_delegaciones(request):
    delegaciones = []
    if Delegacion.objects.all().exists():
        delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegacion_obj in delegacion_objs:
            delegaciones.append([delegacion_obj.get_delegation_id(), delegacion_obj.get_delegacion_name()])
    if request.method == 'POST' and request.POST['action'] == 'informacionDelegacion':
        delegacion_data = get_delegation_data(request.POST['delegacion'])
        return render(request,'aicespana/listadoDelegaciones.html', {'delegacion_data':delegacion_data})
    return render(request,'aicespana/listadoDelegaciones.html', {'delegaciones': delegaciones})

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

        return render(request,'aicespana/nuevoVoluntario.html',{'confirmation_data': confirmation_data})
    return render(request,'aicespana/nuevoVoluntario.html')
