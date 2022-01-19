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
    delegaciones = delegation_name_list()
    if request.method == 'POST' and request.POST['action'] == 'altaDelegacion':
        if Delegacion.objects.filter(nombreDelegacion__iexact = request.POST['nombre']).exists():
            error = [ERROR_DELEGACION_EXIST, request.POST['nombre']]
            return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones, 'ERROR':error})
        new_delegacion_obj = Delegacion.objects.create(nombreDelegacion = request.POST['nombre'])
        return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones,'confirmation_data': request.POST['nombre']})
    return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones})

@login_required
def alta_diocesis(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    diocesis_data = {}
    diocesis_data['delegation_data'] = delegation_id_and_name_list()
    diocesis_data['diocesis_list'] = get_diocesis_name_and_delegation_name()

    if request.method == 'POST' and request.POST['action'] == 'altaDiocesis':
        if Diocesis.objects.filter(nombreDiocesis__iexact = request.POST['nombre']).exists():
            error = [ERROR_DIOCESIS_EXIST, request.POST['nombre']]
            return render(request,'aicespana/altaDiocesis.html',{'diocesis_data':diocesis_data, 'ERROR':error})
        data = {'name':request.POST['nombre'], 'delegation_id':request.POST['delegacion_id']}
        new_diocesis_obj =Diocesis.objects.create_new_diocesis(data)

        return render(request,'aicespana/altaDiocesis.html',{'diocesis_data':diocesis_data,'confirmation_data': request.POST['nombre']})
    return render(request,'aicespana/altaDiocesis.html',{'diocesis_data':diocesis_data})

@login_required
def alta_parroquia(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    parroquia_data = {}
    parroquia_data['parroquia_diocesis_name'] = get_id_parroquia_diocesis_delegacion_name()
    parroquia_data['diocesis_id_name_list'] = get_diocesis_id_name_list()
    parroquia_data['provincias'] = get_provincias()
    if request.method == 'POST' and request.POST['action'] == 'altaParroquia':
        if check_exists_parroquia(request.POST['nombre'],request.POST['diocesis_id']):
            return render (request, 'aicespana/altaParroquia.html',{'parroquia_data':parroquia_data, 'ERROR':ERROR_PARROQUIA_EXISTS})
        diocesis_obj = get_diocesis_obj_from_id(request.POST['diocesis_id'])
        parroquia_data = {'diocesis_obj': diocesis_obj}
        list_of_data = ['nombre' ,'calle', 'poblacion', 'provincia', 'codigo','observaciones']
        for item in list_of_data:
            parroquia_data[item] = request.POST[item]
        new_parroquia = Parroquia.objects.create_new_parroquia(parroquia_data)
        return render(request,'aicespana/altaParroquia.html',{'confirmation_data': request.POST['nombre']})

    return render(request,'aicespana/altaParroquia.html',{'parroquia_data':parroquia_data})


@login_required
def alta_grupo(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    grupo_data = {}
    grupo_data['diocesis_id_name_list'] = get_diocesis_id_name_list()
    grupo_data['provincias'] = get_provincias()
    grupo_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    if request.method == 'POST' and request.POST['action'] == 'altaGrupo':
        if check_exists_grupo(request.POST['nombre'],request.POST['diocesis_id']):
            return render (request, 'aicespana/altaGrupo.html',{'grupo_data':grupo_data, 'ERROR':ERROR_GRUPO_EXISTS})
        diocesis_obj = get_diocesis_obj_from_id(request.POST['diocesis_id'])
        data = {'diocesis_obj': diocesis_obj}
        list_of_data = ['nombre' ,'registro','fechaErecion' ,'calle', 'poblacion', 'provincia', 'codigo','observaciones']
        for item in list_of_data:
            data[item] = request.POST[item]
        new_grupo = Grupo.objects.create_new_group(data)
        return render(request,'aicespana/altaGrupo.html',{'confirmation_data': request.POST['nombre']})

    return render(request,'aicespana/altaGrupo.html',{'grupo_data':grupo_data})

@login_required
def alta_personal_iglesia(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
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

@login_required
def alta_proyecto(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    proyecto_data = {}
    proyecto_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    proyecto_data['proyectos_grupos_diocesis_name'] = get_id_proyectos_grupos_diocesis_delegacion_name()

    if request.method == 'POST' and request.POST['action'] == 'altaProyecto':
        if Proyecto.objects.filter(nombreProyecto__iexact = request.POST['nombre']).exists():
            return render(request,'aicespana/altaProyecto.html',{'proyecto_data':proyecto_data, 'ERROR': ERROR_PROYECTO_EXIST})
        data = {}
        data['grupo_obj'] = get_grupo_obj_from_id(request.POST['grupoID'])
        data['alta'] = request.POST['alta']
        data['nombre'] = request.POST['nombre']
        if 'uploadMemoria' in request.FILES:
            data['memoria_file'] = store_file(request.FILES['uploadMemoria'])
        if 'uploadFotografia' in request.FILES:
            data['fotografia_file'] = store_file(request.FILES['uploadFotografia'])

        new_project = Proyecto.objects.create_new_proyecto(data)
        return render(request,'aicespana/altaProyecto.html',{'confirmation_data': request.POST['nombre']})

    return render(request,'aicespana/altaProyecto.html',{'proyecto_data':proyecto_data})

@login_required
def alta_voluntario(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'altaVoluntario':
        confirmation_data = ''
        info_to_fetch = ['nombre', 'apellidos','nif','nacimiento','calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil', 'tipoColaboracion','grupoID', 'boletin']
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field]
        PersonalExterno_obj = PersonalExterno.objects.create_new_external_personel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellidos'] = request.POST['apellidos']

        return render(request,'aicespana/altaVoluntario.html',{'confirmation_data': confirmation_data})
    new_volunteer_data = {'types':get_volunteer_types() ,'provincias':get_provincias()}
    new_volunteer_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_name()
    return render(request,'aicespana/altaVoluntario.html',{'new_volunteer_data':new_volunteer_data})


@login_required
def modificacion_delegacion(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    delegacion_data = delegation_id_and_name_list()
    return render(request,'aicespana/modificacionDelegacion.html',{'delegacion_data':delegacion_data})

@login_required
def modificar_delegacion(request,delegation_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Delegacion.objects.filter(pk__exact = delegation_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DELEGACION_NOT_EXIST})
    delegacion_obj = get_delegation_obj_from_id(delegation_id)
    delegacion = {}
    delegacion['id'] = delegation_id
    delegacion['name'] = delegacion_obj.get_delegacion_name()
    delegacion['image'] = delegacion_obj.get_delegacion_image()
    if request.method == 'POST' and request.POST['action'] == 'modificarDelegacion':
        if Delegacion.objects.filter(nombreDelegacion__iexact = request.POST['nombre']).exclude(pk__exact =request.POST['delegacion_id'] ).exists():
            return render (request,'aicespana/modificarDelegacion.html', {'ERROR': ERROR_DELEGACION_MODIFICATION_EXIST, 'delegacion':delegacion})
        delegation_obj = get_delegation_obj_from_id(request.POST['delegacion_id'])
        delegation_obj.update_delegacion_name_and_image(request.POST['nombre'], request.POST['image'])
        return render(request,'aicespana/modificarDelegacion.html',{'confirmation_data': request.POST['nombre']})

    return render(request,'aicespana/modificarDelegacion.html',{'delegacion':delegacion})

@login_required
def modificacion_diocesis(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    diocesis_data = {}
    #diocesis_data['delegation_data'] = delegation_id_and_name_list()
    diocesis_data['diocesis_list'] = get_diocesis_id_name_and_delegation_name()

    return render(request,'aicespana/modificacionDiocesis.html',{'diocesis_data':diocesis_data})

@login_required
def modificar_diocesis(request,diocesis_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Diocesis.objects.filter(pk__exact = diocesis_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DIOCESIS_NOT_EXIST})
    diocesis_obj = get_diocesis_obj_from_id(diocesis_id)
    diocesis_data = {}
    diocesis_data['delegation_id'] = diocesis_obj.get_delegacion_id()
    diocesis_data['delegation_name'] = diocesis_obj.get_delegacion_name()
    diocesis_data['diocesis_id'] = diocesis_obj.get_diocesis_id()
    diocesis_data['diocesis_name'] = diocesis_obj.get_diocesis_name()
    diocesis_data['delegation_id_name_list'] = delegation_id_and_name_list()

    if request.method == 'POST' and request.POST['action'] == 'modificarDiocesis':
        if Diocesis.objects.filter(nombreDiocesis__iexact = request.POST['diocesisNombre']).exclude(pk__exact =request.POST['diocesisID'] ).exists():
            return render (request,'aicespana/modificarDiocesis.html', {'ERROR': ERROR_DIOCESIS_MODIFICATION_EXIST, 'diocesis_data':diocesis_data})
        delegation_obj = get_delegation_obj_from_id(request.POST['delegacion_id'])
        diocesis_obj = get_diocesis_obj_from_id(request.POST['diocesisID'])
        diocesis_obj.update_diocesis_data(request.POST['diocesisNombre'],delegation_obj)
        return render(request,'aicespana/modificarDiocesis.html',{'confirmation_data': request.POST['diocesisNombre']})

    return render(request,'aicespana/modificarDiocesis.html',{'diocesis_data':diocesis_data})


@login_required
def modificacion_grupo(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    grupo_data = {'grupos_diocesis_name': get_id_grupo_diocesis_delegacion_name()}

    return render(request,'aicespana/modificacionGrupo.html',{'grupo_data':grupo_data})

@login_required
def modificar_grupo(request,grupo_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Grupo.objects.filter(pk__exact = grupo_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_GRUPO_NOT_EXIST})
    grupo_data = get_grupo_data_to_modify(grupo_id)
    grupo_data['diocesis_id_name_list'] = get_diocesis_id_name_list()
    grupo_data['provincias'] = get_provincias()
    if request.method == 'POST' and request.POST['action'] == 'modificarGrupo':
        if Grupo.objects.filter(nombreGrupo__iexact = request.POST['grupo_name'], diocesisDependiente__pk__exact = request.POST['diocesisID']).exclude(pk__exact =request.POST['grupoID'] ).exists():
            return render (request,'aicespana/modificarGrupo.html', {'ERROR': ERROR_GRUPO_MODIFICATION_EXIST, 'grupo_data':grupo_data})
        grupo_obj = get_grupo_obj_from_id(request.POST['grupoID'])
        grupo_obj.update_grupo_data(fetch_grupo_data_to_modify(request.POST))
        return render(request,'aicespana/modificarGrupo.html',{'confirmation_data':request.POST['grupo_name']})
    return render(request,'aicespana/modificarGrupo.html',{'grupo_data':grupo_data})




@login_required
def modificacion_parroquia(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    parroquia_data = {'parroquia_diocesis_name': get_id_parroquia_diocesis_delegacion_name()}

    return render(request,'aicespana/modificacionParroquia.html',{'parroquia_data':parroquia_data})

@login_required
def modificar_parroquia(request,parroquia_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Parroquia.objects.filter(pk__exact = parroquia_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DIOCESIS_NOT_EXIST})
    parroquia_data = get_parroquia_data_to_modify(parroquia_id)
    parroquia_data['diocesis_id_name_list'] = get_diocesis_id_name_list()
    parroquia_data['provincias'] = get_provincias()
    if request.method == 'POST' and request.POST['action'] == 'modificarParroquia':
        if Parroquia.objects.filter(nombreParroquia__iexact = request.POST['parroquia_name'], diocesisDependiente__pk__exact = request.POST['diocesisID']).exclude(pk__exact =request.POST['parroquiaID'] ).exists():
            return render (request,'aicespana/modificarParroquia.html', {'ERROR': ERROR_PARROQUIA_MODIFICATION_EXIST, 'parroquia_data':parroquia_data})
        parroquia_obj = get_parroquia_obj_from_id(request.POST['parroquiaID'])
        parroquia_obj.update_parroquia_data(fetch_parroquia_data_to_modify(request.POST))
        return render(request,'aicespana/modificarParroquia.html',{'confirmation_data':request.POST['parroquia_name']})
    return render(request,'aicespana/modificarParroquia.html',{'parroquia_data':parroquia_data})

@login_required
def modificacion_proyecto(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})

    proyecto_data = {}
    #proyecto_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    proyecto_data['proyectos_grupos_diocesis_name'] = get_id_proyectos_grupos_diocesis_delegacion_name()

    return render(request,'aicespana/modificacionProyecto.html',{'proyecto_data':proyecto_data})


@login_required
def modificar_proyecto(request,proyecto_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Proyecto.objects.filter(pk__exact = proyecto_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_PROYECTO_NOT_EXIST})
    proyecto_data = get_proyecto_data_to_modify(proyecto_id)

    proyecto_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_name()
    #import pdb; pdb.set_trace()
    if request.method == 'POST' and request.POST['action'] == 'modificarProyecto':
        if Proyecto.objects.filter(nombreProyecto__iexact = request.POST['proyecto_name'], grupoAsociado__pk__exact = request.POST['grupoID']).exclude(pk__exact =request.POST['proyectoID'] ).exists():
            return render (request,'aicespana/modificarProyecto.html', {'ERROR': ERROR_PROYECTO_MODIFICATION_EXIST, 'proyecto_data':proyecto_data})
        proyecto_obj = get_proyecto_obj_from_id(request.POST['proyectoID'])
        proyecto_obj.update_proyecto_data(fetch_proyecto_data_to_modify(request.POST, request.FILES))
        return render(request,'aicespana/modificarProyecto.html',{'confirmation_data':request.POST['proyecto_name']})
    return render(request,'aicespana/modificarProyecto.html',{'proyecto_data':proyecto_data})


@login_required
def modificacion_voluntario(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellido'] == '':
            return render(request, 'aicespana/modificacionVoluntario.html')
        if request.POST['nif'] != '':
            if PersonalExterno.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalExterno.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/modificacionVoluntario.html',{'ERROR':error})
                voluntary_data = get_defined_data_for_voluntary(personal_objs[0])
                personal_available_settings.update(get_external_personal_responsability(personal_objs[0]))
                voluntary_data['user_id'] = personal_objs[0].get_personal_id()
                return render(request, 'aicespana/modificacionVoluntario.html', {'voluntary_data':voluntary_data})
            error = ['No hay nigún voluntario que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/modificacionVoluntario.html',{'ERROR':error})
        personal_objs = PersonalExterno.objects.all()
        if request.POST['apellido'] != '':
            personal_objs = personal_objs.filter(apellido__iexact = request.POST['apellido'])
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
        if len(personal_objs) == 0 :
            error = ['No hay nigún voluntario que cumpla los criterios de busqueda', str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
            return render(request, 'aicespana/modificacionVoluntario.html',{'ERROR':error})
        if len(personal_objs) >1 :
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])
            return render(request, 'aicespana/modificacionVoluntario.html', {'personal_list':personal_list})
        voluntary_data = personal_objs[0].get_all_data_from_voluntario()

        #personal_available_settings.update(get_external_personal_responsability(personal_objs[0]))
        #voluntary_data['user_id'] = personal_objs[0].get_personal_id()
        return render(request, 'aicespana/modificacionVoluntario.html', {'voluntary_data':voluntary_data})
    if request.method == 'POST' and request.POST['action'] == 'actualizarCampos':
        user_obj = get_user_obj_from_id(request.POST['user_id'])
        data = {}
        data['cargo'] = request.POST['cargo']
        data['actividad'] = request.POST['actividad']
        data['grupo'] = request.POST['grupo']
        data['proyecto'] = request.POST['proyecto']
        data['colaboracion'] = request.POST['colaboracion']
        user_obj.update_information(data)
        updated_data = get_external_personal_responsability(user_obj)

        return render(request,'aicespana/modificacionVoluntario.html',{'voluntario_data':voluntario_data})
    return render(request,'aicespana/modificacionVoluntario.html')


@login_required
def listado_voluntarios(request):

    return render(request,'listadoVoluntarios.html')

@login_required
def busqueda_personal(request):
    return render(request,'resultadoBusqueda.html')
@login_required
def cargos_personal(request):
    if request.method == 'POST' and request.POST['action'] == 'busquedaPersonal':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellido'] == '':
            return render(request, 'aicespana/cargosPersonal.html')
        if request.POST['nif'] != '':
            if PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/cargosPersonal.html',{'ERROR':error})
                return render(request, 'aicespana/cargosPersonal.html', {'personal_available_settings':personal_available_settings})
            error = [ERROR_NOT_FIND_PERSONAL_NIF, request.POST['nif']]
            return render(request, 'aicespana/cargosPersonal.html',{'ERROR':error})
        personal_objs = PersonalIglesia.objects.all()
        if request.POST['apellido'] != '':
            personal_objs = personal_objs.filter(apellido__iexact = request.POST['apellido'])
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__iexact = request.POST['nombre'])
        if len(personal_objs) == 0:
            error = [ERROR_NOT_FIND_PERSONAl_CRITERIA, str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
            return render(request, 'aicespana/cargosPersonal.html',{'ERROR':error})
        if len(personal_objs) >1 :
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])
            return render(request, 'aicespana/cargosPersonal.html', {'personal_list':personal_list})
        personal_available_settings = get_responsablity_data_for_personel(personal_objs[0])
        personal_available_settings.update(get_personal_responsability(personal_objs[0]))

        personal_available_settings['user_id'] = personal_objs[0].get_personal_id()
        return render(request, 'aicespana/cargosPersonal.html', {'personal_available_settings':personal_available_settings})

    if request.method == 'POST' and request.POST['action'] == 'asignarCargos':
        user_obj = get_personel_obj_from_id(request.POST['user_id'])

        data = {}
        data['cargo'] = request.POST['cargo']
        data['delegacion'] = request.POST['delegacion']
        data['grupo'] = request.POST['grupo']
        user_obj.update_information(data)
        updated_data = get_personal_responsability(user_obj)
        return render(request, 'aicespana/cargosPersonal.html', {'updated_data':updated_data})
    return render(request, 'aicespana/cargosPersonal.html')


@login_required
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
@login_required
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

@login_required
def listado_delegaciones(request):
    delegaciones = []
    if Delegacion.objects.all().exists():
        delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegacion_obj in delegacion_objs:
            delegaciones.append([delegacion_obj.get_delegacion_id(), delegacion_obj.get_delegacion_name()])
    if request.method == 'POST' and request.POST['action'] == 'informacionDelegacion':
        delegacion_data = get_delegation_data(request.POST['delegacion'])
        return render(request,'aicespana/listadoDelegaciones.html', {'delegacion_data':delegacion_data})

    return render(request,'aicespana/listadoDelegaciones.html', {'delegaciones': delegaciones})

@login_required
def listado_delegacion(request, delegacion_id):
    if not allow_all_lists(request):
        if not allow_own_delegation(request):
            return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not Delegacion.objects.filter(pk__exact = delegacion_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DELEGACION_NOT_EXIST})
    delegacion_obj = get_delegation_obj_from_id(delegacion_id)
    #Get the diocesis bolongs to the delegation
    delegacion_data = {}
    delegacion_data['diocesis_list'] = get_diocesis_in_delegation(delegacion_obj)
    #diocesis_data['cargos_diocesis'] = ''
    delegacion_data['summary'] = [get_summary_of_delegation(delegacion_obj)]
    delegacion_data['delegacion_name'] = delegacion_obj.get_delegacion_name()
    delegacion_data['delegacion_image'] = delegacion_obj.get_delegacion_image()
    return render(request,'aicespana/listadoDelegacion.html', {'delegacion_data': delegacion_data})



def listado_diocesis(request,diocesis_id):
    if not allow_all_lists(request):
        if not allow_own_delegation(request):
            return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not Diocesis.objects.filter(pk__exact = diocesis_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DIOCESIS_NOT_EXIST})
    diocesis_obj = get_diocesis_obj_from_id(diocesis_id)
    diocesis_data = {}
    diocesis_data['grupos'] = get_groups_in_diocesis(diocesis_obj)
    diocesis_data['cargos'] = get_diocesis_cargos(diocesis_obj)
    diocesis_data['summary'] = [get_summary_of_diocesis(diocesis_obj)]
    diocesis_data['diocesis_name'] = diocesis_obj.get_diocesis_name()
    import pdb; pdb.set_trace()
    return render(request,'aicespana/listadoDiocesis.html', {'diocesis_data': diocesis_data})

def listado_grupo(request, grupo_id):
    if not allow_all_lists(request):
        if not allow_own_delegation(request):
            return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not Grupo.objects.filter(pk__exact = grupo_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_GRUPO_NOT_EXIST})
    grupo_obj = get_grupo_obj_from_id(grupo_id)
    grupo_data = {}
    grupo_data['nombre_grupo'] = grupo_obj.get_grupo_name()
    grupo_data['cargos'] = get_grupo_cargos(grupo_obj)
    grupo_data['informacion'] = grupo_obj.get_grupo_full_data()
    grupo_data['summary'] = [get_summary_of_group(grupo_obj)]
    grupo_data['lista_voluntarios'] = get_grupo_voluntarios(grupo_obj)
    grupo_data['lista_colaboradores'] = get_grupo_colaboradores(grupo_obj)
    grupo_data['lista_asesores'] = get_grupo_asesores(grupo_obj)
    grupo_data['lista_otros'] = get_grupo_otros(grupo_obj)

    #import pdb; pdb.set_trace()
    return render(request,'aicespana/listadoGrupo.html', {'grupo_data': grupo_data})


@login_required
def listado_voluntarios_grupo(request):
    grupos = []
    if Grupo.objects.all().exists():
        grupo_objs = Grupo.objects.all().order_by('nombreGrupo')
        for grupo_obj in grupo_objs:
            grupos.append([grupo_obj.get_grupo_id(), grupo_obj.get_grupo_name(),grupo_obj.get_diocesis_name() ])
    if request.method == 'POST' and request.POST['action'] == 'nombreGrupo':
        voluntarios_data = get_voluntarios_info_from_grupo(request.POST['grupo_id'])

        return render(request, 'aicespana/listadoVoluntariosGrupo.html', {'voluntarios_data': voluntarios_data})

    return render(request,'aicespana/listadoVoluntariosGrupo.html', {'grupos':grupos})
