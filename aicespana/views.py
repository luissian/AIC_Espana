import statistics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from .message_text import *
from .utils.generic_functions import *

def index(request):
    return render(request,'aicespana/index.html')

@login_required
def alta_actividad(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    actividad_data = {}
    #actividad_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    actividad_data['grupos_diocesis_id_name'] = get_group_list_to_select_in_form()
    actividad_data['actividad_grupos_diocesis_name'] = get_id_actividad_grupos_diocesis_delegacion_name()

    if request.method == 'POST' and request.POST['action'] == 'altaActividad':
        if Actividad.objects.filter(nombreActividad__iexact = request.POST['nombre']).exists():
            return render(request,'aicespana/altaActividad.html',{'actividad_data':actividad_data, 'ERROR': [ERROR_ACTIVIDAD_EXIST]})
        data = {}
        data['grupo_obj'] = get_grupo_obj_from_id(request.POST['grupoID']) if request.POST['grupoID'] != '' else None
        data['alta'] = request.POST['alta']
        data['nombre'] = request.POST['nombre']
        data['observaciones'] = request.POST['observaciones']
        if 'uploadMemoria' in request.FILES:
            data['memoria_file'] = store_file(request.FILES['uploadMemoria'])
        if 'uploadFotografia' in request.FILES:
            data['fotografia_file'] = store_file(request.FILES['uploadFotografia'])

        new_actividad = Actividad.objects.create_new_actividad(data)
        return render(request,'aicespana/altaActividad.html',{'confirmation_data': request.POST['nombre']})
    return render(request,'aicespana/altaActividad.html',{'actividad_data':actividad_data})


@login_required
def alta_delegacion(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    delegaciones = delegation_name_list()
    if request.method == 'POST' and request.POST['action'] == 'altaDelegacion':
        if Delegacion.objects.filter(nombreDelegacion__iexact = request.POST['nombre']).exists():
            error = [ERROR_DELEGACION_EXIST, request.POST['nombre']]
            return render(request,'aicespana/altaDelegacion.html',{'delegaciones':delegaciones, 'ERROR':error})
        imagen_file = None
        if 'uploadImage' in request.FILES:
            image_folder = os.path.join(settings.MEDIA_ROOT,'images')
            os.makedirs(image_folder,exist_ok = True)
            image_file = store_file(request.FILES['uploadImage'])
            os.replace(os.path.join(settings.MEDIA_ROOT,image_file),os.path.join(image_folder,image_file))
        else:
            image_file = None
        data = {'nombre': request.POST['nombre'], 'imagen': image_file}
        new_delegacion_obj = Delegacion.objects.create_new_delegacion(data)
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
        info_to_fetch = ['nombre', 'apellido','nif', 'email', 'fijo', 'movil' , 'calle', 'poblacion', 'provincia', 'codigo','nacimiento']
        personal_data = {}

        for field in info_to_fetch:
            personal_data[field] = request.POST[field].strip()
        if PersonalIglesia.objects.filter(nombre__iexact = personal_data['nombre'], apellido__iexact = personal_data['apellido']).exists():
            return render(request,'aicespana/altaVoluntario.html',{'ERROR': [ERROR_PERSONAL_IGLESIA_ALREADY_IN_DATABASE]})
        PersonalExterno_obj = PersonalIglesia.objects.create_new_personel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellido'] = request.POST['apellido']
        return render(request,'aicespana/altaPersonalIglesia.html',{'confirmation_data': confirmation_data})
    personel_data ={'provincias':get_provincias()}
    return render(request,'aicespana/altaPersonalIglesia.html',{'personel_data':personel_data})

@login_required
def alta_proyecto(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    proyecto_data = {}
    # proyecto_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    proyecto_data['grupos_diocesis_id_name'] = get_group_list_to_select_in_form()
    proyecto_data['proyectos_grupos_diocesis_name'] = get_id_proyectos_grupos_diocesis_delegacion_name()

    if request.method == 'POST' and request.POST['action'] == 'altaProyecto':
        if Proyecto.objects.filter(nombreProyecto__iexact = request.POST['nombre']).exists():
            return render(request,'aicespana/altaProyecto.html',{'proyecto_data':proyecto_data, 'ERROR': [ERROR_PROYECTO_EXIST]})
        data = {}
        data['grupo_obj'] = get_grupo_obj_from_id(request.POST['grupoID']) if request.POST['grupoID'] != '' else None
        data['alta'] = request.POST['alta']
        data['nombre'] = request.POST['nombre'].strip()
        data['observaciones'] = request.POST['observaciones']
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
        info_to_fetch = ['nombre', 'apellidos','nif','nacimiento', 'alta' ,'calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil', 'tipoColaboracion','grupoID', 'boletin']
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field].strip()
        if PersonalExterno.objects.filter(nombre__iexact = personal_data['nombre'], apellido__iexact = personal_data['apellidos']).exists():
            return render(request,'aicespana/altaVoluntario.html',{'ERROR': [ERROR_VOLUNTARIO_ALREADY_IN_DATABASE]})
        PersonalExterno_obj = PersonalExterno.objects.create_new_external_personel(personal_data)
        confirmation_data = {}
        confirmation_data['nombre'] = request.POST['nombre']
        confirmation_data['apellidos'] = request.POST['apellidos']

        return render(request,'aicespana/altaVoluntario.html',{'confirmation_data': confirmation_data})
    new_volunteer_data = {'types':get_volunteer_types() ,'provincias':get_provincias()}
    new_volunteer_data['grupos_diocesis_id_name'] = get_group_list_to_select_in_form()
    #new_volunteer_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_name()
    return render(request,'aicespana/altaVoluntario.html',{'new_volunteer_data':new_volunteer_data})


@login_required
def modificacion_actividad(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})

    actividad_data = {'actividad_grupos_diocesis_name': get_id_actividad_grupos_diocesis_delegacion_name() }

    return render(request,'aicespana/modificacionActividad.html',{'actividad_data':actividad_data})


@login_required
def modificar_actividad(request,actividad_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not Actividad.objects.filter(pk__exact = actividad_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_ACTIVIDAD_NOT_EXIST})
    actividad_data = get_actividad_data_to_modify(actividad_id)

    actividad_data['grupos_diocesis_id_name'] = get_group_list_to_select_in_form()  #get_id_grupo_diocesis_name()

    if request.method == 'POST' and request.POST['action'] == 'modificarActividad':
        if Actividad.objects.filter(nombreActividad__iexact = request.POST['actividad_name'], grupoAsociado__pk__exact = request.POST['grupoID']).exclude(pk__exact =request.POST['actividadID'] ).exists():
            return render (request,'aicespana/modificarActividad.html', {'ERROR': ERROR_ACTIVIDAD_MODIFICATION_EXIST, 'actividad_data':actividad_data})
        actividad_obj = get_actividad_obj_from_id(request.POST['actividadID'])
        actividad_obj.update_actividad_data(fetch_actividad_data_to_modify(request.POST, request.FILES))
        return render(request,'aicespana/modificarActividad.html',{'confirmation_data':request.POST['actividad_name']})
    return render(request,'aicespana/modificarActividad.html',{'actividad_data':actividad_data})

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
        if 'uploadImage' in request.FILES:
            image_folder = os.path.join(settings.MEDIA_ROOT,'images')
            os.makedirs(image_folder,exist_ok = True)
            image_file = store_file(request.FILES['uploadImage'])
            os.replace(os.path.join(settings.MEDIA_ROOT,image_file),os.path.join(image_folder,image_file))
        else:
            image_file = None
        delegation_obj.update_delegacion_name_and_image(request.POST['nombre'],image_file)
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
def modificacion_personal_id(request, personal_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not PersonalIglesia.objects.filter(pk__exact = personal_id).exists():
        return render(request, 'aicespana/errorPage.html', {'content': ERROR_PERSONAL_DOES_NOT_EXIST})
    personal_obj = get_personal_obj_from_id(personal_id)
    personal_data = personal_obj.get_all_data_from_personal()
    personal_data['provincias'] = get_provincias()
    return render(request, 'aicespana/modificacionPersonal.html', {'personal_data':personal_data})

@login_required
def modificacion_personal(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'busquedaPersonal':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellido'] == '':
            return render(request, 'aicespana/modificacionPersonal.html')
        if request.POST['nif'] != '':
            if PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif'])

                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/modificacionPersonal.html',{'ERROR':error})
                personal_data = personal_objs[0].get_all_data_from_personal()
                personal_data['provincias'] = get_provincias()

                return render(request, 'aicespana/modificacionPersonal.html', {'personal_data':personal_data})
            error = ['No hay nigún Personal de la Iglesia que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/modificacionPersonal.html',{'ERROR':error})
        personal_objs = PersonalIglesia.objects.all()
        if request.POST['apellido'] != '':
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellido'].strip())
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'].strip())
        if len(personal_objs) == 0 :
            error = ['No hay nigún Personal de Iglesia que cumpla los criterios de busqueda:', str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
            return render(request, 'aicespana/modificacionPersonal.html',{'ERROR':error})
        if len(personal_objs) >1 :

            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])

            return render(request, 'aicespana/modificacionPersonal.html', {'personal_list':personal_list})
        personal_data = personal_objs[0].get_all_data_from_personal()
        personal_data['provincias'] = get_provincias()


        return render(request, 'aicespana/modificacionPersonal.html', {'personal_data':personal_data})
    if request.method == 'POST' and request.POST['action'] == 'actualizarCampos':
        user_obj = get_personal_obj_from_id(request.POST['user_id'])
        data = {}
        field_list = ['nombre', 'apellidos','dni','calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil',
                'baja', 'boletin' ,'activo','nacimiento']

        for item in field_list:
            data[item] = request.POST[item]

        user_obj.update_all_data_for_personal(data)

        return render(request,'aicespana/modificacionPersonal.html',{'confirmation_data':request.POST['nombre'] + ' ' + request.POST['apellidos']})
    return render(request,'aicespana/modificacionPersonal.html')



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

    proyecto_data['grupos_diocesis_id_name'] = get_group_list_to_select_in_form()  #get_id_grupo_diocesis_name()

    if request.method == 'POST' and request.POST['action'] == 'modificarProyecto':
        if Proyecto.objects.filter(nombreProyecto__iexact = request.POST['proyecto_name'], grupoAsociado__pk__exact = request.POST['grupoID']).exclude(pk__exact =request.POST['proyectoID'] ).exists():
            return render (request,'aicespana/modificarProyecto.html', {'ERROR': ERROR_PROYECTO_MODIFICATION_EXIST, 'proyecto_data':proyecto_data})
        proyecto_obj = get_proyecto_obj_from_id(request.POST['proyectoID'])
        proyecto_obj.update_proyecto_data(fetch_proyecto_data_to_modify(request.POST, request.FILES))
        return render(request,'aicespana/modificarProyecto.html',{'confirmation_data':request.POST['proyecto_name']})
    return render(request,'aicespana/modificarProyecto.html',{'proyecto_data':proyecto_data})

@login_required
def modificacion_voluntario_id(request, voluntario_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not PersonalExterno.objects.filter(pk__exact = voluntario_id).exists():
        return render(request, 'aicespana/errorPage.html', {'content': ERROR_VOLUNTARIO_DOES_NOT_EXIST})
    user_obj = get_user_obj_from_id(voluntario_id)
    voluntary_data = user_obj.get_all_data_from_voluntario()
    voluntary_data['provincias'] = get_provincias()
    voluntary_data['grupo_lista'] = get_group_list_to_select_in_form()
    voluntary_data['tipo_colaboracion'] = get_volunteer_types()
    voluntary_data['proyecto_lista'] = get_project_group_diocesis()
    voluntary_data['proyecto_data_form'] = user_obj.get_proyecto_data_for_form()
    voluntary_data['actividad_lista'] = get_activity_group_diocesis()
    voluntary_data['actividad_data_form'] = user_obj.get_actividad_data_for_form()

    return render(request, 'aicespana/modificacionVoluntario.html', {'voluntary_data':voluntary_data})

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
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellido'].strip())
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'].strip())
        if len(personal_objs) == 0 :
            error = ['No hay nigún voluntario que cumpla los criterios de busqueda', str(request.POST['nombre']  + ' ' + request.POST['apellido']) ]
            return render(request, 'aicespana/modificacionVoluntario.html',{'ERROR':error})
        if len(personal_objs) >1 :
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append([personal_obj.get_personal_id(), personal_obj.get_personal_name(),personal_obj.get_personal_location()])
            return render(request, 'aicespana/modificacionVoluntario.html', {'personal_list':personal_list})
        voluntary_data = personal_objs[0].get_all_data_from_voluntario()
        voluntary_data['provincias'] = get_provincias()
        voluntary_data['grupo_lista'] = get_group_list_to_select_in_form()
        voluntary_data['tipo_colaboracion'] = get_volunteer_types()
        voluntary_data['proyecto_lista'] = get_project_group_diocesis()
        voluntary_data['proyecto_data_form'] = personal_objs[0].get_proyecto_data_for_form()
        voluntary_data['actividad_lista'] = get_activity_group_diocesis()
        voluntary_data['actividad_data_form'] = personal_objs[0].get_actividad_data_for_form()

        return render(request, 'aicespana/modificacionVoluntario.html', {'voluntary_data':voluntary_data})
    if request.method == 'POST' and request.POST['action'] == 'actualizarCampos':
        user_obj = get_user_obj_from_id(request.POST['user_id'])
        data = {}
        field_list = ['nombre', 'apellidos','dni','nacimiento','calle','poblacion', 'provincia', 'codigo', 'email', 'fijo', 'movil',
                'alta', 'baja', 'colaboracion_id','grupoID', 'boletin','activo','actividadID','proyectoID']

        for item in field_list:
            data[item] = request.POST[item]

        user_obj.update_all_data_for_voluntary(data)

        return render(request,'aicespana/modificacionVoluntario.html',{'confirmation_data':request.POST['nombre'] + ' ' + request.POST['apellidos']})
    return render(request,'aicespana/modificacionVoluntario.html')

@login_required
def cargos_personal_id(request, personal_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    user_obj = get_personal_obj_from_id(personal_id)
    personal_available_settings = get_responsablity_data_for_personel(user_obj)
    personal_available_settings.update(get_personal_responsability(user_obj))

    personal_available_settings['user_id'] = personal_id
    return render(request, 'aicespana/cargosPersonal.html', {'personal_available_settings':personal_available_settings})

@login_required
def cargos_personal(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
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
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellido'].strip())
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'].strip())

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
        user_obj = get_personal_obj_from_id(request.POST['user_id'])

        data = {}
        data['cargo'] = request.POST['cargo']
        data['delegacion'] = request.POST['delegacion']
        #data['diocesis'] = request.POST['diocesis']
        data['grupo'] = request.POST['grupo']
        user_obj.update_information(data)
        updated_data = get_personal_responsability(user_obj)
        return render(request, 'aicespana/cargosPersonal.html', {'updated_data':updated_data})
    return render(request, 'aicespana/cargosPersonal.html')


@login_required
def cargo_voluntario(request, voluntario_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    user_obj = get_user_obj_from_id(voluntario_id)
    personal_available_settings = get_responsablity_data_for_voluntary(user_obj)
    personal_available_settings.update(get_external_personal_responsability(user_obj))
    personal_available_settings['user_id'] = voluntario_id
    return render(request, 'aicespana/cargosVoluntarios.html', {'personal_available_settings':personal_available_settings})

@login_required
def cargos_voluntarios(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
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
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellido'].strip())
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'].strip())
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
def informacion_personal_id(request,personal_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not PersonalIglesia.objects.filter(pk__exact = personal_id).exists():
        return render(request, 'aicespana/errorPage.html', {'content': ERROR_PERSONAL_DOES_NOT_EXIST})
    personal_obj = get_personal_obj_from_id(personal_id)
    info_personal = personal_obj.get_all_data_from_personal()
    info_personal['cargos'] = personal_obj.get_responability_belongs_to()
    return render(request,'aicespana/informacionPersonal.html',{'info_personal':info_personal})

@login_required
def informacion_personal(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellidos'] == '':
            return render(request, 'aicespana/informacionVoluntario.html')
        if request.POST['nif'] != '':
            if PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalIglesia.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/informacionPersonal.html',{'ERROR':error})
                info_voluntario = personal_obj.get_all_data_from_personal()
                info_voluntario['cargos'] = personal_obj.get_responability_belongs_to()
                return render(request, 'aicespana/informacionPersonal.html',{'info_voluntario':info_voluntario})
            error = ['No hay nigún Personal de la Iglesia que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/informacionPersonal.html',{'ERROR':error})
        personal_objs = PersonalIglesia.objects.all()
        if request.POST['apellidos'] != '':
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellidos'])
            if len(personal_objs) == 0:
                error = ['No hay nigún Personal de Iglesia que tenga el apellido', request.POST['apellidos']]
                return render(request, 'aicespana/informacionPersonal.html',{'ERROR':error})
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'])
            if len(personal_objs) == 0:
                error = ['No hay nigún Personal de Iglesia con el nombre', request.POST['nombre']]
                return render(request, 'aicespana/informacionPersonal.html',{'ERROR':error})
        if len(personal_objs) >1 :
            error = ['Hay más de un Personal de Iglesia que cumple los criterios de busqueda']
            return render(request, 'aicespana/informacionPersonal.html', {'ERROR':error})
        info_voluntario = personal_obj.get_all_data_from_personal()
        info_voluntario['cargos'] = personal_obj.get_responability_belongs_to()
        return render(request,'aicespana/informacionPersonal.html',{'info_personal':info_personal})



@login_required
def informacion_voluntario_id(request,voluntario_id):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if not PersonalExterno.objects.filter(pk__exact = voluntario_id).exists():
        return render(request, 'aicespana/errorPage.html', {'content': ERROR_VOLUNTARIO_DOES_NOT_EXIST})
    user_obj = get_user_obj_from_id(voluntario_id)
    info_voluntario = user_obj.get_all_data_from_voluntario()
    info_voluntario['cargos'] = user_obj.get_responability_belongs_to()
    return render(request,'aicespana/informacionVoluntario.html',{'info_voluntario':info_voluntario})

@login_required
def informacion_voluntario(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'busquedaVoluntario':
        if request.POST['nif'] == '' and request.POST['nombre'] == '' and request.POST['apellidos'] == '':
            return render(request, 'aicespana/informacionVoluntario.html')
        if request.POST['nif'] != '':
            if PersonalExterno.objects.filter(DNI__iexact = request.POST['nif']).exists():
                personal_objs = PersonalExterno.objects.filter(DNI__iexact = request.POST['nif'])
                if len(personal_objs) > 1:
                    error = ['Hay más de 1 persona que tiene el mismo NIF/NIE', reques.POST['nif']]
                    return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
                info_voluntario = personal_objs[0].get_all_data_from_voluntario()
                info_voluntario['cargos'] = personal_objs[0].get_responability_belongs_to()
                return render(request, 'aicespana/informacionVoluntario.html',{'info_voluntario':info_voluntario})
            error = ['No hay nigún voluntario que tenga el NIF/NIE', request.POST['nif']]
            return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        personal_objs = PersonalExterno.objects.all()
        if request.POST['apellidos'] != '':
            personal_objs = personal_objs.filter(apellido__icontains = request.POST['apellidos'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el apellido', request.POST['apellidos']]
                return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        if request.POST['nombre'] != '':
            personal_objs = personal_objs.filter(nombre__icontains = request.POST['nombre'])
            if len(personal_objs) == 0:
                error = ['No hay nigún voluntario con el nombre', request.POST['nombre']]
                return render(request, 'aicespana/informacionVoluntario.html',{'ERROR':error})
        if len(personal_objs) >1 :
            error = ['Hay más de un voluntario que cumple los criterios de busqueda']
            return render(request, 'aicespana/informacionVoluntario.html', {'ERROR':error})
        info_voluntario = personal_objs[0].get_all_data_from_voluntario()
        info_voluntario['cargos'] = personal_objs[0].get_responability_belongs_to()
        #info_voluntario = [personal_objs[0].get_voluntario_data()]
        return render(request,'aicespana/informacionVoluntario.html',{'info_voluntario':info_voluntario})
    return render(request,'aicespana/informacionVoluntario.html')

@login_required
def listado_boletin(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    listado = get_excel_user_request_boletin()
    return render(request,'aicespana/listadoBoletin.html',{'listado':listado})


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
    #if not allow_all_lists(request):
    #    if not allow_own_delegation(request):
    #        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
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
    delegacion_data.update(get_delegation_data (delegacion_id))
    #import pdb; pdb.set_trace()
    return render(request,'aicespana/listadoDelegacion.html', {'delegacion_data': delegacion_data})



def listado_diocesis(request,diocesis_id):
    #if not allow_all_lists(request):
    #    if not allow_own_delegation(request):
    #        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not Diocesis.objects.filter(pk__exact = diocesis_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_DIOCESIS_NOT_EXIST})
    diocesis_obj = get_diocesis_obj_from_id(diocesis_id)
    diocesis_data = {}
    diocesis_data['grupos'] = get_groups_in_diocesis(diocesis_obj)
    diocesis_data['cargos'] = get_diocesis_cargos(diocesis_obj)
    diocesis_data['summary'] = [get_summary_of_diocesis(diocesis_obj)]
    diocesis_data['diocesis_name'] = diocesis_obj.get_diocesis_name()

    return render(request,'aicespana/listadoDiocesis.html', {'diocesis_data': diocesis_data})

def listado_grupo(request, grupo_id):
    if not Grupo.objects.filter(pk__exact = grupo_id).exists():
        return render (request,'aicespana/errorPage.html', {'content': ERROR_GRUPO_NOT_EXIST})
    grupo_obj = get_grupo_obj_from_id(grupo_id)
    if not allow_see_group_information_voluntary(request, grupo_obj):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    grupo_data = {}
    grupo_data['nombre_grupo'] = grupo_obj.get_grupo_name()
    grupo_data['cargos'] = get_grupo_cargos(grupo_obj)
    grupo_data['informacion'] = grupo_obj.get_grupo_full_data()
    grupo_data['summary'] = [get_summary_of_group(grupo_obj)]
    grupo_data['lista_voluntarios'] = get_grupo_voluntarios(grupo_obj)
    grupo_data['lista_colaboradores'] = get_grupo_colaboradores(grupo_obj)
    grupo_data['lista_asesores'] = get_grupo_asesores(grupo_obj)
    grupo_data['lista_otros'] = get_grupo_otros(grupo_obj)

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


@login_required
def listado_personal_iglesia(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    listado_personal = get_personal_list_order_by_delegacion()
    return render(request,'aicespana/listadoPersonalIglesia.html',{'listado_personal': listado_personal})

@login_required
def listado_delegados_regionales(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    listado_delegados = get_delegados_regionales()
    return render(request,'aicespana/listadoDelegadosRegionales.html',{'listado_delegados': listado_delegados})


@login_required
def listado_presidentes_grupo(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'listadoPresidentesGrupo':
        presidentes = presidentes_grupo(request.POST['delegacion_id'])
        if not presidentes:
            error_message = ERROR_NO_PRESIDENTS_IN_DELEGATION
            delegation_data = delegation_id_and_name_list()
            return render(request,'aicespana/listadoPresidentesGrupo.html',{'delegation_data': delegation_data, 'ERROR':error_message})
        return render(request,'aicespana/listadoPresidentesGrupo.html',{'presidentes': presidentes})

    delegation_data = delegation_id_and_name_list()
    return render(request,'aicespana/listadoPresidentesGrupo.html',{'delegation_data': delegation_data})

@login_required
def listado_personal_externo(request):
    if not is_manager(request):
        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_MANAGER})
    if request.method == 'POST' and request.POST['action'] == 'listadoDelegacion':
        listado_personal , excel_file = get_personal_externo_por_delegacion(request.POST['delegacion_id'])
        delegacion = get_delegation_obj_from_id(request.POST['delegacion_id']).get_delegacion_name()
        return render(request,'aicespana/listadoPersonalExterno.html',{'listado_personal': listado_personal, 'excel_file':excel_file, 'delegacion': delegacion})
    delegation_data = delegation_id_and_name_list()
    return render(request,'aicespana/listadoPersonalExterno.html',{'delegation_data': delegation_data})
