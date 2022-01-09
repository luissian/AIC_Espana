import statistics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import *
from .message_text import *
from .utils.generic_functions import *

def index(request):
    return render(request,'aicespana/index.html')

#@login_required
def alta_actividad(request):
    return render(request,'aicespana/altaActividad.html',{'new_actividad_data':new_actividad_data})


@login_required
def alta_delegacion(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
    delegaciones = []
    for delegacion_obj in delegacion_objs:
        delegaciones.append(delegacion_obj.get_delegacion_name())
    if request.method == 'POST' and request.POST['action'] == 'altaDelegacion':
        if Delegacion.objects.filter(nombreDelegacion__iexact = request.POST['nombre']).exists():
            error = [ERROR_DELEGACION_EXIST, request.POST['nombre']]
            return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones, 'ERROR':error})
        new_delegacion_obj = Delegacion.objects.create(nombreDelegacion = request.POST['nombre'])
        return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones,'confirmation_data': request.POST['nombre']})
    return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones})

#@login_required
def alta_diocesis(request):
    return render(request,'aicespana/altadiocesis.html',{'new_diocesis_data':new_diocesis_data})

#@login_required
def alta_grupo(request):
    return render(request,'aicespana/altaGrupo.html',{'new_grupo_data':new_grupo_data})

#@login_required
def alta_personal_iglesia(request):
    if request.method == 'POST' and request.POST['action'] == 'altaPersonal':
        confirmation_data = ''
        info_to_fetch = ['nombre', 'apellido','nif', 'email', 'fijo', 'movil']
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field]
        PersonalExterno_obj = PersonalIglesia.objects.create_new_personel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellido'] = request.POST['apellido']
        return render(request,'aicespana/altaPersonalIglesia.html',{'confirmation_data': confirmation_data})
    new_personel_data =''
    return render(request,'aicespana/altaPersonalIglesia.html',{'new_personel_data':new_personel_data})

#@login_required
def alta_proyecto(request):
    return render(request,'aicespana/altaProyecto.html',{'new_proyecto_data':new_proyecto_data})

#@login_required
def alta_voluntario(request):
    if request.method == 'POST' and request.POST['action'] == 'altaVoluntario':
        confirmation_data = ''
        info_to_fetch = ['nombre', 'apellidos','nif','nacimiento','calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil', 'tipoColaboracion']
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field]
        PersonalExterno_obj = PersonalExterno.objects.create_new_external_personel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellidos'] = request.POST['apellidos']

        return render(request,'aicespana/altaVoluntario.html',{'confirmation_data': confirmation_data})
    new_volunteer_data = {'types':get_volunteer_types() ,'provincias':get_provincias()}
    return render(request,'aicespana/altaVoluntario.html',{'new_volunteer_data':new_volunteer_data})



@login_required
def listado_voluntarios(request):

    return render(request,'listadoVoluntarios.html')

@login_required
def busqueda_personal(request):
    return render(request,'resultadoBusqueda.html')

def cargos_personal_iglesia(request):
    if request.method == 'POST' and request.POST['action'] == 'busquedaPersonal':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellido'] == '':
            return render(request, 'aicespana/cargosPersonalIglesia.html')
        if request.POST['nif'] != '':
            if PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/cargosPersonalIglesia.html',{'ERROR':error})
                return render(request, 'aicespana/cargosVoluntarios.html', {'personal_available_settings':personal_available_settings})
            error = [ERROR_NOT_FIND_PERSONAL_NIF, request.POST['nif']]
            return render(request, 'aicespana/cargosPersonalIglesia.html',{'ERROR':error})
        personal_objs = PersonalIglesia.objects.all()
        if request.POST['apellido'] != '':
            personal_objs = personal_objs.filter(apellido__iexact = request.POST['apellido'])
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
        if len(personal_objs) == 0:
            error = [ERROR_NOT_FIND_PERSONAl_CRITERIA, str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
            return render(request, 'aicespana/cargosPersonalIglesia.html',{'ERROR':error})
        if len(personal_objs) >1 :
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])
            return render(request, 'aicespana/cargosPersonalIglesia.html', {'personal_list':personal_list})
        personal_available_settings = get_responsablity_data_for_personel(personal_objs[0])
        personal_available_settings.update(get_personal_responsability(personal_objs[0]))

        personal_available_settings['user_id'] = personal_objs[0].get_personal_id()
        return render(request, 'aicespana/cargosPersonalIglesia.html', {'personal_available_settings':personal_available_settings})

    if request.method == 'POST' and request.POST['action'] == 'asignarCargos':
        user_obj = get_personel_obj_from_id(request.POST['user_id'])

        data = {}
        data['cargo'] = request.POST['cargo']
        data['delegacion'] = request.POST['delegacion']
        data['grupo'] = request.POST['grupo']
        user_obj.update_information(data)
        updated_data = get_personal_responsability(user_obj)
        import pdb; pdb.set_trace()
        return render(request, 'aicespana/cargosPersonalIglesia.html', {'updated_data':updated_data})
    return render(request, 'aicespana/cargosPersonalIglesia.html')



def cargos_voluntarios(request):
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellido'] == '':
            return render(request, 'aicespana/cargosVoluntarios.html')
        if request.POST['nif'] != '':
            if PersonalExterno.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalExterno.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
                personal_available_settings = get_responsablity_data_for_voluntary(personal_objs[0])
                personal_available_settings.update(get_external_personal_responsability(personal_objs[0]))
                return render(request, 'aicespana/cargosVoluntarios.html', {'personal_available_settings':personal_available_settings})
            error = ['No hay nigún voluntario que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/cargosVoluntarios.html',{'ERROR':error})
        personal_objs = PersonalExterno.objects.all()
        if request.POST['apellido'] != '':
            personal_objs = personal_objs.filter(apellido__iexact = request.POST['apellido'])
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
        if len(personal_objs) == 0 :
            error = ['No hay nigún voluntario que cumpla los criterios de busqueda', str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
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

def informacion_voluntario(request):
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellidos'] == '':
            return render(request, 'aicespana/informacionVoluntario.html')
        if request.POST['nif'] != '':
            if PersonalExterno.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalExterno.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
                info_voluntario = personal_objs[0].get_voluntario_data()
                return render(request, 'aicespana/informacionVoluntario.html',{'info_voluntario':info_voluntario})
            error = ['No hay nigún voluntario que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        personal_objs = PersonalExterno.objects.all()
        if request.POST['apellidos'] != '':
            personal_objs = personal_objs.filter(apellidos__iexact = request.POST['apelidos'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el apellido', request.POST['apellidos']]
                return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el nombre', request.POST['nombre']]
                return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        if len(personal_objs) >1 :
            error = ['Hay más de un voluntario que cumple los criterios de busqueda']
            return render(request, 'aicespana/informacionVoluntario.html', {'ERROR':error})
        info_voluntario = [personal_objs[0].get_voluntario_data()]
        return render(request,'aicespana/informacionVoluntario.html',{'info_voluntario':info_voluntario})
    return render(request,'aicespana/informacionVoluntario.html')

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


def listado_diocesis(request):
    diocesis = []
    if Diocesis.objects.all().exists():
        diocesis_objs = Diocesis.objects.all().order_by('nombreDiocesis')
        for diocesis_obj in diocesis_objs:
            diocesis.append([diocesis_obj.get_diocesis_id(),diocesis_obj.get_diocesis_name()])
    if request.method == 'POST' and request.POST['action'] == 'informacionDiocesis':
        diocesis_data = get_diocesis_data(request.POST['diocesis'])

        return render(request,'aicespana/listadoDiocesis.html', {'diocesis_data': diocesis_data})
    return render(request,'aicespana/listadoDiocesis.html', {'diocesis': diocesis})


def listado_voluntarios_grupo(request):
    grupos = []
    if Grupo.objects.all().exists():
        grupo_objs = Grupo.objects.all().order_by('nombreGrupo')
        for grupo_obj in grupo_objs:
            grupos.append([grupo_obj.get_group_id(), grupo_obj.get_group_name(),grupo_obj.get_parroquia_name() ])
    if request.method == 'POST' and request.POST['action'] == 'nombreGrupo':
        voluntarios_data = get_voluntarios_info_from_grupo(request.POST['grupo_id'])

        return render(request, 'aicespana/listadoVoluntariosGrupo.html', {'voluntarios_data': voluntarios_data})

    return render(request,'aicespana/listadoVoluntariosGrupo.html', {'grupos':grupos})
