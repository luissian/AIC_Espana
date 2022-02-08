from aicespana.models import *
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import collections


def check_exists_grupo(grupo_name,diocesis_id ):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        grupo_name  # Name of the grupo
        diocesis_id     # id of the diocesis
    Return:
        True/False
    '''
    return Grupo.objects.filter(nombreGrupo__iexact = grupo_name, diocesisDependiente__pk__exact = diocesis_id).exists()

def check_exists_parroquia(parroquia_name,diocesis_id ):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        parroquia_name  # Name of the parroquia
        diocesis_id     # id of the diocesis
    Return:
        True/False
    '''
    return Parroquia.objects.filter(nombreParroquia__iexact = parroquia_name, diocesisDependiente__pk__exact =diocesis_id).exists()

def get_delegation_data(delegation_id):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        delegation_id  # id of the delegation
    Return:
        delegation_data
    '''
    delegation_data = {}
    delegation_data['cargos'] = []
    if Delegacion.objects.filter(pk__exact = delegation_id).exists():
        delegation_data['name'] = Delegacion.objects.filter(pk__exact = delegation_id).last().get_delegacion_name()
        if Cargo.objects.filter(entidadCargo__entidad__iexact = 'delegación').exists():
            cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'delegación').order_by('nombreCargo')
            for cargo_obj in cargo_objs:
                cargo_name = cargo_obj.get_cargo_name()
                if PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).exists():
                    user_name = PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).last().get_personal_name()
                else:
                    user_name = 'Puesto vacante'
                delegation_data['cargos'].append([cargo_name, user_name ])

    return delegation_data

def delegation_name_list():
    '''
    Description:
        The function gets a list with all delegation names.
    Return:
        delegation_name_list
    '''
    delegation_name_list = []
    delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
    for delegacion_obj in delegacion_objs:
        delegation_name_list.append(delegacion_obj.get_delegacion_name())
    return delegation_name_list

def delegation_id_and_name_list():
    '''
    Description:
        The function gets a list with the ids and delegation names.
    Return:
        delegation_id_name_list
    '''
    delegation_id_name_list = []
    delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
    for delegacion_obj in delegacion_objs:
        delegation_id_name_list.append([delegacion_obj.get_delegacion_id(), delegacion_obj.get_delegacion_name()])
    return delegation_id_name_list

def get_delegation_obj_from_id(delegation_id):
    '''
    Description:
        The function return the delegation object from their id.
    Input:
        delegation_id   # id of the delegation
    Return:
        object of delegation instance
    '''
    return Delegacion.objects.filter(pk__exact = delegation_id).last()

def get_summary_of_delegation(delegation_obj):
    '''
    Description:
        The function return the summary data (number of voluntarios, number of grupos and number of diocesis
    Input:
        delegation_obj   # object of the delegation
    Return:
        summary_data
    '''
    num_diocesis = Diocesis.objects.filter(delegacionDependiente = delegation_obj).count()
    num_grupos = Grupo.objects.filter(diocesisDependiente__delegacionDependiente = delegation_obj).count()
    num_voluntarios = PersonalExterno.objects.filter(grupoAsociado__diocesisDependiente__delegacionDependiente = delegation_obj).count()
    return [num_voluntarios ,num_grupos, num_diocesis]


def get_summary_of_diocesis(diocesis_obj):
    '''
    Description:
        The function return the summary data (number of voluntarios and  number of grupos
    Input:
        delegation_obj   # object of the diocesis
    Return:
        summary_data
    '''
    num_grupos = Grupo.objects.filter(diocesisDependiente = diocesis_obj).count()
    num_voluntarios = PersonalExterno.objects.filter(grupoAsociado__diocesisDependiente = diocesis_obj).count()
    return [num_voluntarios ,num_grupos]


def get_summary_of_group(grupo_obj):
    '''
    Description:
        The function return the summary data (number of voluntarios)
    Input:
        delegation_obj   # object of the diocesis
    Return:
        summary_data
    '''
    num_voluntarios = PersonalExterno.objects.filter(grupoAsociado = grupo_obj, personalActivo = 'True', tipoColaboracion__tipoColaboracion = 'Voluntario').count()
    num_colaboradores = PersonalExterno.objects.filter(grupoAsociado = grupo_obj, personalActivo = 'True', tipoColaboracion__tipoColaboracion = 'Colaborador').count()
    num_asesores=  PersonalExterno.objects.filter(grupoAsociado = grupo_obj, personalActivo = 'True', tipoColaboracion__tipoColaboracion = 'Asesor').count()
    num_total =  PersonalExterno.objects.filter(grupoAsociado = grupo_obj, personalActivo = 'True').count()
    num_otros = num_total - num_voluntarios - num_colaboradores - num_asesores
    return [num_voluntarios, num_colaboradores, num_asesores, num_otros]

def get_diocesis_obj_from_id(diocesis_id):
    '''
    Description:
        The function return the diocesis object from their id.
    Input:
        delegation_id   # id of the diocesis
    Return:
        object of diocesis instance
    '''
    return Diocesis.objects.filter(pk__exact = diocesis_id).last()

def get_diocesis_cargos(diocesis_obj):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        diocesis_obj  # obj of the diocesis
    Return:
        cargos_data
    '''
    cargos_data = {}
    if Cargo.objects.filter(entidadCargo__entidad__iexact = 'diocesis').exists():
        cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'diocesis').order_by('nombreCargo')
        for cargo_obj in cargo_objs:
            cargo_name = cargo_obj.get_cargo_name()
            if PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado__diocesisDependiente = diocesis_obj).exists():
                personal_obj = PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado__diocesisDependiente = diocesis_obj).last()
                cargos_data[cargo_name] = personal_obj.get_personal_name()
            else:
                cargos_data[cargo_name] = 'Sin Asignar'

    return cargos_data

def get_diocesis_id_name_and_delegation_name():
    '''
    Description:
        The function gets the diocesis id , the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    '''
    diocesis_data = []
    diocesis_objs = Diocesis.objects.all().order_by('delegacionDependiente')
    for diocesis_obj in diocesis_objs:
        diocesis_data.append([diocesis_obj.get_diocesis_id(),diocesis_obj.get_diocesis_name(),diocesis_obj.get_delegacion_name()])
    return diocesis_data

def get_diocesis_name_and_delegation_name():
    '''
    Description:
        The function gets the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    '''
    diocesis_data = []
    diocesis_objs = Diocesis.objects.all().order_by('delegacionDependiente')
    for diocesis_obj in diocesis_objs:
        diocesis_data.append([diocesis_obj.get_diocesis_name(),diocesis_obj.get_delegacion_name()])
    return diocesis_data

def get_diocesis_id_name_list():
    '''
    Description:
        The function gets the diocesis id and name
    Return:
        diocesis_data
    '''
    diocesis_data = []
    diocesis_objs = Diocesis.objects.all().order_by('delegacionDependiente')
    for diocesis_obj in diocesis_objs:
        diocesis_data.append([diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()])
    return diocesis_data

def get_diocesis_in_delegation(delegacion_obj):
    '''
    Description:
        The function gets the diocesis id and name of one delegacion
    Input:
        delegacion_obj  # object of delegacion
    Return:
        diocesis_data
    '''
    diocesis_data = []
    diocesis_objs = Diocesis.objects.filter(delegacionDependiente = delegacion_obj).order_by('delegacionDependiente')
    for diocesis_obj in diocesis_objs:
        diocesis_data.append([diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()])
    return diocesis_data

def get_groups_in_diocesis(diocesis_obj):
    '''
    Description:
        The function gets the grupos and their id from a diocesis
    Input:
        diocesis_obj  # object of diocesis
    Return:
        groups_data
    '''
    groups_data = []
    if Grupo.objects.filter(diocesisDependiente = diocesis_obj).exists():
        grupo_objs = Grupo.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreGrupo')
        for grupo_obj in grupo_objs:
            groups_data.append([grupo_obj.get_grupo_id(), grupo_obj.get_grupo_name()])
    return groups_data

def get_grupo_cargos(grupo_obj):
    '''
    Description:
        The function gets the information and the voluntario name and the responsability.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        cargos_data
    '''
    cargos_data = {}
    if Cargo.objects.filter(entidadCargo__entidad__iexact = 'grupo').exists():
        cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'grupo').order_by('nombreCargo')
        for cargo_obj in cargo_objs:
            cargo_name = cargo_obj.get_cargo_name()
            if PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).exists():
                personal_obj = PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).last()
                cargos_data[cargo_name] = personal_obj.get_personal_name()
            elif PersonalIglesia.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).exists():
                personal_obj = PersonalIglesia.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).last()
                cargos_data[cargo_name] = personal_obj.get_personal_name()
            else:
                cargos_data[cargo_name] = 'Sin Asignar'
    return cargos_data

def get_grupo_cargos_personal(grupo_obj):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        cargos_data
    '''
    cargos_data = {}
    if Cargo.objects.filter(entidadCargo__entidad__iexact = 'grupo').exists():
        cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'grupo').order_by('nombreCargo')
        for cargo_obj in cargo_objs:
            cargo_name = cargo_obj.get_cargo_name()
            if PersonalIglesia.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).exists():
                personal_obj = PersonalIglesia.objects.filter(cargo__nombreCargo__exact = cargo_name, grupoAsociado = grupo_obj).last()
                cargos_data[cargo_name] = personal_obj.get_personal_name()
            else:
                cargos_data[cargo_name] = 'Sin Asignar'
    return cargos_data

def get_grupo_voluntarios(grupo_obj):
    '''
    Description:
        The function gets the list of voluntarios for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        voluntario_list
    '''
    voluntario_list = {'mayor80':[], 'menor80':[], 'sin_edad':[]}

    if PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Voluntario').exists():
        personal_objs = PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Voluntario').order_by('apellido')
        for personal_obj in personal_objs:
            old =  personal_obj.get_old()
            if old == '' :
                voluntario_list['sin_edad'].append(personal_obj.get_personal_name())
            elif old  >= 80 :
                voluntario_list['mayor80'].append(personal_obj.get_personal_name())
            else:
                voluntario_list['menor80'].append(personal_obj.get_personal_name())
    return voluntario_list

def get_grupo_colaboradores(grupo_obj):
    '''
    Description:
        The function gets the list of colaboradores for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        colaborador_list
    '''
    colaborador_list = {'mayor80':[], 'menor80':[], 'sin_edad':[]}
    if PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Colaborador').exists():
        personal_objs = PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Colaborador').order_by('apellido')
        for personal_obj in personal_objs:
            old =  personal_obj.get_old()
            if old == '' :
                colaborador_list['sin_edad'].append(personal_obj.get_personal_name())
            elif old  >= 80 :
                colaborador_list['mayor80'].append(personal_obj.get_personal_name())
            else:
                colaborador_list['menor80'].append(personal_obj.get_personal_name())
    return colaborador_list

def get_grupo_asesores(grupo_obj):
    '''
    Description:
        The function gets the list of asesores for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        asesor_list
    '''
    asesor_list = {'mayor80':[], 'menor80':[], 'sin_edad':[]}
    if PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Asesor').exists():
        personal_objs = PersonalExterno.objects.filter(grupoAsociado = grupo_obj, tipoColaboracion__tipoColaboracion__exact = 'Asesor').order_by('apellido')
        for personal_obj in personal_objs:
            old =  personal_obj.get_old()
            if old == '' :
                asesor_list['sin_edad'].append(personal_obj.get_personal_name())
            elif old  >= 80 :
                asesor_list['mayor80'].append(personal_obj.get_personal_name())
            else:
                asesor_list['menor80'].append(personal_obj.get_personal_name())
    return asesor_list

def get_grupo_otros(grupo_obj):
    '''
    Description:
        The function gets the list of other tipe of colaborations for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        otros_list
    '''
    otros_list = {'mayor80':[], 'menor80':[], 'sin_edad':[]}
    colaboration_list = ['Voluntario', 'Asesor','Colaborador']
    if PersonalExterno.objects.filter(grupoAsociado = grupo_obj).exclude(tipoColaboracion__tipoColaboracion__in = colaboration_list).exists():
        personal_objs = PersonalExterno.objects.filter(grupoAsociado = grupo_obj).exclude(tipoColaboracion__tipoColaboracion__in = colaboration_list).order_by('apellido')
        for personal_obj in personal_objs:
            old =  personal_obj.get_old()
            if old == '' :
                otros_list['sin_edad'].append(personal_obj.get_personal_name())
            elif old  >= 80 :
                otros_list['mayor80'].append(personal_obj.get_personal_name())
            else:
                otros_list['menor80'].append(personal_obj.get_personal_name())
    return otros_list



def get_actividad_obj_from_id(actividad_id):
    '''
    Description:
        The function return the actividad object from their id.
    Input:
        actividad_id   # id of the actividad
    Return:
        object of actividad instance
    '''
    return Actividad.objects.filter(pk__exact = actividad_id).last()

def get_actividad_data_to_modify(actividad_id):
    '''
    Description:
        The function gets the actividad recorded data to modify in the form
    Return:
        actividad_data
    '''
    actividad_data = {}
    actividad_obj = get_actividad_obj_from_id(actividad_id)
    data = actividad_obj.get_actividad_full_data()
    extract_list = ['actividad_name', 'actividadID', 'grupoID', 'grupo_name', 'diocesis_name', 'alta', 'baja', 'activo', 'memoria', 'fotografia']
    for index in range(len(extract_list)):
        actividad_data[extract_list[index]] = data[index]
    return actividad_data



def fetch_parroquia_data_to_modify(data_form):
    '''
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
    Return:
        data
    '''
    data = {}
    extract_list = ['parroquia_name','diocesisID','calle','poblacion','provincia','codigo','observaciones']
    for item in extract_list:
        data[item] = data_form[item]
    return data

def get_parroquia_obj_from_id(parroquia_id):
    '''
    Description:
        The function return the parroquia object from their id.
    Input:
        parroquia_id   # id of the parroquia
    Return:
        object of parroquia instance
    '''
    return Parroquia.objects.filter(pk__exact = parroquia_id).last()

def get_id_parroquia_diocesis_delegacion_name():
    '''
    Description:
        The function gets the parroquia the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    '''
    diocesis_data = collections.OrderedDict()
    if Parroquia.objects.all().exists():
        delegation_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = Diocesis.objects.filter(delegacionDependiente = delegation_obj).order_by('nombreDiocesis')
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                parroquia_objs = Parroquia.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreParroquia')
                for parroquia_obj in parroquia_objs:
                    if not delegation_name in diocesis_data:
                        diocesis_data[delegation_name] = []
                    diocesis_data[delegation_name].append([parroquia_obj.get_parroquia_id(),parroquia_obj.get_parroquia_name(),diocesis_name ])
    return diocesis_data

def get_parroquia_data_to_modify(parroquia_id):
    '''
    Description:
        The function gets the parroquia recorded data to modify in the form
    Return:
        parroquia_data
    '''
    parroquia_data = {}
    parroquia_obj = get_parroquia_obj_from_id(parroquia_id)
    data = parroquia_obj.get_parroquia_full_data()
    extract_list = ['parroquia_name', 'parroquiaID','diocesis_name','diocesis_id','calle','poblacion','provincia','codigo','observaciones']
    for index in range(len(extract_list)):
        parroquia_data[extract_list[index]] = data[index]
    return parroquia_data

def get_proyecto_obj_from_id(proyecto_id):
    '''
    Description:
        The function return the proyecto object from their id.
    Input:
        proyecto_id   # id of the proyecto
    Return:
        object of proyecto instance
    '''
    return Proyecto.objects.filter(pk__exact = proyecto_id).last()

def get_proyecto_data_to_modify(proyecto_id):
    '''
    Description:
        The function gets the proyecto recorded data to modify in the form
    Return:
        proyecto_data
    '''
    proyecto_data = {}
    proyecto_obj = get_proyecto_obj_from_id(proyecto_id)
    data = proyecto_obj.get_proyecto_full_data()
    extract_list = ['proyecto_name', 'proyectoID', 'grupoID', 'grupo_name', 'diocesis_name', 'alta', 'baja', 'activo', 'memoria', 'fotografia']
    for index in range(len(extract_list)):
        proyecto_data[extract_list[index]] = data[index]
    return proyecto_data

def fetch_grupo_data_to_modify(data_form):
    '''
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
    Return:
        data
    '''
    data = {}
    extract_list = ['grupo_name','diocesisID','calle','poblacion','provincia','codigo','alta', 'baja','activo', 'observaciones']
    for item in extract_list:
        data[item] = data_form[item]
    return data

def get_grupo_obj_from_id(grupo_id):
    '''
    Description:
        The function return the grupo object from their id.
    Input:
        grupo_id   # id of the grupo
    Return:
        object of grupo instance
    '''
    return Grupo.objects.filter(pk__exact = grupo_id).last()

def get_id_grupo_diocesis_delegacion_name():
    '''
    Description:
        The function gets the group the diocesis name and the delegation belogs to
    Return:
        group_diocesis_data
    '''
    group_diocesis_data = collections.OrderedDict()
    if Grupo.objects.all().exists():
        delegation_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = Diocesis.objects.filter(delegacionDependiente = delegation_obj).order_by('nombreDiocesis')
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                grupo_objs = Grupo.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreGrupo')
                for grupo_obj in grupo_objs:
                    if not delegation_name in group_diocesis_data:
                        group_diocesis_data[delegation_name] = []
                    group_diocesis_data[delegation_name].append([grupo_obj.get_grupo_id(),grupo_obj.get_grupo_name(),diocesis_name ])

    return group_diocesis_data
def get_group_list_to_select_in_form():
    '''
    Description:
        The function gets the group the diocesis name to select in the user form
    Return:
        group_data
    '''
    group_data = []
    if Grupo.objects.all().exists():
        grupo_objs = Grupo.objects.all().order_by('nombreGrupo')
        for grupo_obj in grupo_objs:
            group_data.append([grupo_obj.get_grupo_id(),grupo_obj.get_grupo_name(), grupo_obj.get_diocesis_name()])
    return group_data

def get_id_grupo_diocesis_name():
    '''
    Description:
        The function gets the group and the diocesis name belogs to
    Return:
        group_diocesis_data
    '''
    group_diocesis_data =[]
    if Grupo.objects.all().exists():
        diocesis_objs = Diocesis.objects.all().order_by('nombreDiocesis')
        for diocesis_obj in diocesis_objs:
            diocesis_name = diocesis_obj.get_diocesis_name()
            grupo_objs = Grupo.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreGrupo')
            for grupo_obj in grupo_objs:
                group_diocesis_data.append([grupo_obj.get_grupo_id(),grupo_obj.get_grupo_name(),diocesis_name ])
    return group_diocesis_data

def  get_grupo_data_to_modify(grupo_id):
    '''
    Description:
        The function gets the grupo recorded data to modify in the form
    Return:
        grupo_data
    '''
    grupo_data = {}
    grupo_obj = get_grupo_obj_from_id(grupo_id)
    data = grupo_obj.get_grupo_full_data()
    extract_list = ['grupo_name', 'grupoID','diocesis_name','diocesis_id','calle','poblacion','provincia','codigo','observaciones','alta', 'baja', 'activo']
    for index in range(len(extract_list)):
        grupo_data[extract_list[index]] = data[index]

    return grupo_data

def fetch_actividad_data_to_modify (data_form,file_form):
    '''
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
        file_form   # files upload in the form
    Return:
        data
    '''
    data = {}
    extract_list = ['actividad_name','grupoID','alta', 'baja','activo', 'observaciones']
    for item in extract_list:
        data[item] = data_form[item]
    if 'uploadMemoria' in file_form:
        data['memoria_file'] = store_file(file_form['uploadMemoria'])
    if 'uploadFotografia' in file_form:
        data['fotografia_file'] = store_file(file_form['uploadFotografia'])
    return data


def fetch_proyecto_data_to_modify (data_form,file_form):
    '''
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
        file_form   # files upload in the form
    Return:
        data
    '''
    data = {}
    extract_list = ['proyecto_name','grupoID','alta', 'baja','activo', 'observaciones']
    for item in extract_list:
        data[item] = data_form[item]
    if 'uploadMemoria' in file_form:
        data['memoria_file'] = store_file(file_form['uploadMemoria'])
    if 'uploadFotografia' in file_form:
        data['fotografia_file'] = store_file(file_form['uploadFotografia'])

    return data



def get_id_actividad_grupos_diocesis_delegacion_name():
    '''
    Description:
        The function gets the actividad , grupo the diocesis name and the delegation belogs to
    Return:
        actividad_grupo_diocesis_data
    '''
    actividad_grupo_diocesis_data = collections.OrderedDict()
    if Actividad.objects.all().exists():
        delegation_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = Diocesis.objects.filter(delegacionDependiente = delegation_obj).order_by('nombreDiocesis')
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                grupo_objs = Grupo.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreGrupo')
                for grupo_obj in grupo_objs:
                    grupo_name = grupo_obj.get_grupo_name()
                    actividad_objs = Actividad.objects.filter(grupoAsociado = grupo_obj).order_by('nombreActividad')
                    for actividad_obj in actividad_objs:
                        if not delegation_name in actividad_grupo_diocesis_data:
                            actividad_grupo_diocesis_data[delegation_name] = collections.OrderedDict()
                        if not diocesis_name in actividad_grupo_diocesis_data[delegation_name]:
                            actividad_grupo_diocesis_data[delegation_name][diocesis_name] = []
                        actividad_grupo_diocesis_data[delegation_name][diocesis_name].append([actividad_obj.get_actividad_id(),actividad_obj.get_actividad_name(),grupo_name ])
    return actividad_grupo_diocesis_data


def get_id_proyectos_grupos_diocesis_delegacion_name():
    '''
    Description:
        The function gets the proyecto the diocesis name and the delegation belogs to
    Return:
        proyecto_grupo_diocesis_data
    '''
    proyecto_grupo_diocesis_data = collections.OrderedDict()
    if Proyecto.objects.all().exists():
        delegation_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = Diocesis.objects.filter(delegacionDependiente = delegation_obj).order_by('nombreDiocesis')
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                grupo_objs = Grupo.objects.filter(diocesisDependiente = diocesis_obj).order_by('nombreGrupo')
                for grupo_obj in grupo_objs:
                    grupo_name = grupo_obj.get_grupo_name()
                    proyecto_objs = Proyecto.objects.filter(grupoAsociado = grupo_obj).order_by('nombreProyecto')
                    for proyecto_obj in proyecto_objs:
                        if not delegation_name in proyecto_grupo_diocesis_data:
                            proyecto_grupo_diocesis_data[delegation_name] = collections.OrderedDict()
                        if not diocesis_name in proyecto_grupo_diocesis_data[delegation_name]:
                            proyecto_grupo_diocesis_data[delegation_name][diocesis_name] = []
                        proyecto_grupo_diocesis_data[delegation_name][diocesis_name].append([proyecto_obj.get_proyecto_id(),proyecto_obj.get_proyecto_name(),grupo_name ])
    return proyecto_grupo_diocesis_data


def get_project_group_diocesis():
    '''
    Description:
        The function gets the proyecto and the diocesis name
    Return:
        proyecto_grupo_diocesis_list
    '''
    proyecto_grupo_diocesis_list = []
    if Proyecto.objects.all().exists():
        proyecto_objs = Proyecto.objects.all().order_by('nombreProyecto')
        for proyecto_obj in proyecto_objs:
            proyecto_grupo_diocesis_list.append([proyecto_obj.get_proyecto_id() , proyecto_obj.get_proyecto_name() ,proyecto_obj.get_grupo_name() , proyecto_obj.get_diocesis_name()])
    return proyecto_grupo_diocesis_list






def get_activity_group_diocesis():
    '''
    Description:
        The function gets the proyecto and the diocesis name
    Return:
        proyecto_grupo_diocesis_list
    '''
    activity_grupo_diocesis_list = []
    if Actividad.objects.all().exists():
        actividad_objs = Actividad.objects.all().order_by('nombreActividad')
        for actividad_obj in actividad_objs:
            activity_grupo_diocesis_list.append([actividad_obj.get_actividad_id() , actividad_obj.get_actividad_name() ,actividad_obj.get_grupo_name() , actividad_obj.get_diocesis_name()])
    return activity_grupo_diocesis_list


def get_external_personal_responsability(personal_obj):
    '''
    Description:
        The function gets the voluntary responsability.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        personal_responsability
    '''
    personal_responsability ={}
    personal_responsability['project'] = personal_obj.get_project_belongs_to()
    personal_responsability['project_id'] = personal_obj.get_project_id_belongs_to()
    personal_responsability['activity'] = personal_obj.get_actividad_belongs_to()
    personal_responsability['activity_id'] = personal_obj.get_actividad_id_belongs_to()
    personal_responsability['responsability'] = personal_obj.get_responability_belongs_to()
    personal_responsability['responsability_id'] = personal_obj.get_responability_id_belongs_to()
    personal_responsability['collaboration'] = personal_obj.get_collaboration_belongs_to()
    personal_responsability['collaboration_id'] = personal_obj.get_collaboration_id_belongs_to()
    personal_responsability['group'] = personal_obj.get_group_belongs_to()
    personal_responsability['group_id'] = personal_obj.get_group_id_belongs_to()
    personal_responsability['parroquia'] = personal_obj.get_parroquia_belongs_to()
    personal_responsability['diocesis'] = personal_obj.get_diocesis_belongs_to()
    personal_responsability['delegacion'] = personal_obj.get_delegacion_belongs_to()
    personal_responsability['name'] = personal_obj.get_personal_name()

    return personal_responsability

def get_personal_responsability(personal_obj):
    '''
    Description:
        The function gets the personal responsability.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        personal_responsability
    '''
    personal_responsability ={}
    personal_responsability['group'] = personal_obj.get_group_belongs_to()
    personal_responsability['group_id'] = personal_obj.get_group_id_belongs_to()
    personal_responsability['diocesis'] = personal_obj.get_diocesis_belongs_to()
    personal_responsability['responsability'] = personal_obj.get_responability_belongs_to()
    personal_responsability['responsability_id'] = personal_obj.get_responability_id_belongs_to()
    personal_responsability['delegacion'] = personal_obj.get_delegacion_belongs_to()
    personal_responsability['delegacion_id'] = personal_obj.get_delegacion_id_belongs_to()
    personal_responsability['name'] = personal_obj.get_personal_name()
    return personal_responsability

def get_provincias():

    list_provincias =['Albacete', 'Alicante','Almería','Álava','Asturias','Ávila','Badajoz','Baleares','Barcelona','Bizkaia','Burgos',
        'Cáceres','Cádiz','Cantabria','Castellón','Ciudad Real','Córdoba','Coruña','Cuenca','Gipuzkoa','Girona','Granada','Guadalajara',
        'Huelva', 'Huesca','Jaén','León','Lleida','Lugo','Madrid','Málaga','Murcia','Navarra','Ourense','Palencia','Palmas, Las',
        'Pontevedra','Rioja, La','Salamanca','Santa Cruz de Tenerife','Segovia','Sevilla','Soria','Tarragona','Teruel','Toledo',
        'Valencia','Valladolid','Zamora','Zaragoza','Ceuta','Melilla']
    return list_provincias

def get_responsablity_data_for_personel(personal_obj):
    '''
    Description:
        The function gets the available options that a personel of AIC can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        responsability_options
    '''
    responsability_options = {}
    responsability_options['available_groups'] = []
    responsability_options['available_delegacion'] = []
    responsability_options['available_diocesis'] = []
    responsability_options['available_responsible'] = []
    if Grupo.objects.all().exists():
        group_objs = Grupo.objects.all().order_by('nombreGrupo')
        for group_obj in group_objs:
            responsability_options['available_groups'].append([group_obj.get_grupo_id(), group_obj.get_grupo_name(), group_obj.get_diocesis_name()])
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_options['available_responsible'].append([responsible_obj.get_cargo_id() , responsible_obj.get_cargo_name()])
    if Delegacion.objects.all().exists():
        delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegacion_obj in delegacion_objs:
            responsability_options['available_delegacion'].append([delegacion_obj.get_delegacion_id(), delegacion_obj.get_delegacion_name()])
    if Diocesis.objects.all().exists():
        diocesis_objs = Diocesis.objects.all().order_by('nombreDiocesis')
        for diocesis_obj in diocesis_objs:
            responsability_options['available_diocesis'].append([diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()])
    return responsability_options

def get_responsablity_data_for_voluntary(personal_obj):
    '''
    Description:
        The function gets the available options that a voluntary can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        responsability_optons
    '''
    responsability_optons = {}
    responsability_optons['available_groups'] = []
    responsability_optons['available_projects'] = []
    responsability_optons['available_actitvities'] = []
    responsability_optons['available_responsible'] = []
    responsability_optons['available_collaboration'] = []
    if Grupo.objects.all().exists():
        group_objs = Grupo.objects.all().order_by('nombreGrupo')
        for group_obj in group_objs:
            responsability_optons['available_groups'].append([group_obj.get_grupo_id(), group_obj.get_grupo_name(), group_obj.get_diocesis_name()])
    if Proyecto.objects.all().exists():
        project_objs = Proyecto.objects.all().order_by('nombreProyecto')
        for project_obj in project_objs:
            responsability_optons['available_projects'].append([project_obj.get_proyecto_id(), project_obj.get_proyecto_name()])
    if Actividad.objects.all().exists():
        activity_objs = Actividad.objects.all().order_by('nombreActividad')
        for activity_obj in activity_objs:
            responsability_optons['available_actitvities'].append([activity_obj.get_actividad_id(),activity_obj.get_actividad_name()])
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_optons['available_responsible'].append([responsible_obj.get_cargo_id() , responsible_obj.get_cargo_name()])
    if TipoColaboracion.objects.all().exists():
        collaboration_objs = TipoColaboracion.objects.all().order_by('tipoColaboracion')
        for collaboration_obj in collaboration_objs:
            responsability_optons['available_collaboration'].append([collaboration_obj.get_tipo_colaboracion_id(), collaboration_obj.get_collaboration_name()])
    return responsability_optons


def get_defined_data_for_voluntary(personal_obj):
    '''
    Description:
        The function gets the available options that a voluntary can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        defined_data
    '''
    defined_data ={}
    data = personal_obj.get_voluntario_data()
    fields =['nombre_apellidos', 'calle', 'poblacion', 'provincia','codigo','email', 'dni','movil','grupo' ]
    for index in range(len(fields)):
        defined_data[fields[index]] = data[index]
    defined_data['nombre'] = personal_obj.get_personal_only_name()
    defined_data['apellido'] = personal_obj.get_personal_only_apellido()
    defined_data['user_id'] = personal_obj.get_personal_id()
    return_data




def get_responsibles_in_the_group(group_obj):
    '''
    Description:
        The function gets the voluntary information from a group.
    Input:
        grupo_obj  # instance of the group
    Return:
        responsible_data
    '''
    responsible_data = []
    if Cargo.objects.filter(entidadCargo__entidad__exact ='Grupo').exists():
        cargo_objs = Cargo.objects.filter(entidadCargo__entidad__exact ='Grupo').order_by('nombreCargo')
        for cargo_obj in cargo_objs:
            p_data = []
            if PersonalExterno.objects.filter(cargo = cargo_obj, grupoAsociado = group_obj).exclude(personalActivo = False).exists():
                personal_obj = PersonalExterno.objects.filter(cargo = cargo_obj, grupoAsociado = group_obj).exclude(personalActivo = False).last()
                responsible_data.append(personal_obj.get_voluntario_data())
            else:
                empty_data = ['-']*9
                empty_data[0] = 'No esta asignado'
                empty_data.append(cargo_obj.get_cargo_name())
                responsible_data.append(empty_data)

    return responsible_data

def get_voluntarios_info_from_grupo(grupo_id):
    '''
    Description:
        The function gets the voluntary information from a group.
    Input:
        grupo_id  # pk of the group
    Functions:
        get_responsibles_in_the_group   # located at this file
    Return:
        voluntarios_data
    '''
    voluntarios_data = {}

    if Grupo.objects.filter(pk__exact = grupo_id).exists():
        group_obj = Grupo.objects.filter(pk__exact = grupo_id).last()
        voluntarios_data['cargos'] = get_responsibles_in_the_group(group_obj)
        if PersonalExterno.objects.filter(grupoAsociado = group_obj).exclude(personalActivo = False).exists():
            voluntarios_data['older_than_80'] = []
            voluntarios_data['younger_than_80'] = []
            personal_objs = PersonalExterno.objects.filter(grupoAsociado = group_obj).exclude(personalActivo = False).order_by('apellido')
            for personal_obj in personal_objs:
                if personal_obj.get_old() > 80 :
                    voluntarios_data['older_than_80'].append(personal_obj.get_personal_name())
                else:
                    voluntarios_data['younger_than_80'].append(personal_obj.get_personal_name())
    return voluntarios_data

def get_volunteer_types():
    '''
    Description:
        The function gets the possible type of volunteer
    Return:
        volunteer_types
    '''
    volunteer_types = []
    if TipoColaboracion.objects.all().exists():
        colaboracion_objs = TipoColaboracion.objects.all().order_by('tipoColaboracion')
        for colaboracion_obj in colaboracion_objs:
            volunteer_types.append([colaboracion_obj.get_tipo_colaboracion_id(),colaboracion_obj.get_collaboration_name()])
    return volunteer_types

def get_user_obj_from_id(user_id):
    '''
    Description:
        The function gets the personal instance from the the primary key.
    Input:
        user_id  # pk of the user
    Return:
        the personel instance or false
    '''
    if PersonalExterno.objects.filter(pk__exact = user_id).exists():
        return PersonalExterno.objects.filter(pk__exact = user_id).last()
    return False


def get_personal_obj_from_id(user_id):
    '''
    Description:
        The function gets the personal instance from the the primary key.
    Input:
        user_id  # pk of the user
    Return:
        the personel instance or false
    '''
    if PersonalIglesia.objects.filter(pk__exact = user_id).exists():
        return PersonalIglesia.objects.filter(pk__exact = user_id).last()
    return False


def is_manager (request):
    '''
    Description:
        The function will check if the logged user belongs to administracion  manager group
    Input:
        request # contains the session information
    Return:
        Return True if the user belongs to administracion group, False if not
    '''
    try:
        groups = Group.objects.get(name = 'administracion')
        if groups not in request.user.groups.all():
            return False
    except:
        return False

    return True
def allow_see_group_information_voluntary (request, group_obj):
    '''
    Description:
        The function will check if the logged user belongs to administracion, todasDelegaciones groups
        or has the presidenta diocesana responsability and belongs to the same delegacion
    Input:
        request # contains the session information
        group_obj   # object of the grouo
    Return:
        Return True if the user can see group lists, False if not
    '''
    try:
        administracion_groups = Group.objects.get(name = 'administracion')
        if administracion_groups not in request.user.groups.all():
            todas_delegaciones = Group.objects.get(name = 'todasDelegaciones')
            if todas_delegaciones not in request.user.groups.all():
                nombre_usuario = request.user.first_name
                apellido_usuario = request.user.last_name
                if not PersonalExterno.objects.filter(nombre__iexact = nombre_usuario, apellido__iexact = apellido_usuario).exists():
                    return False
                usuario_obj = PersonalExterno.objects.filter(nombre__iexact = nombre_usuario, apellido__iexact = apellido_usuario).last()
                if usuario_obj.get_responability_belongs_to() != 'Presidenta Diocesana':
                    return False
                if usuario_obj.get_delegacion_belongs_to() != group_obj.get_delegacion_name():
                    return False
                return True
    except:
        return False
    return True

def get_personal_list_order_by_delegacion():
    '''
    Description:
        The function get the personel list ordered by delegation - Diocesis - grupo
    Return:
        Return personal_list
    '''
    personal_list = collections.OrderedDict()
    if PersonalIglesia.objects.all().exclude(personalActivo = False).exists():
        personal_objs = PersonalIglesia.objects.all().exclude(personalActivo = False).order_by('delegacion').order_by('grupoAsociado__diocesisDependiente').order_by('grupoAsociado').order_by('nombre')
        for personal_obj in personal_objs:
            delegation_name = personal_obj.get_delegacion_belongs_to()
            diocesis_name = personal_obj.get_diocesis_belongs_to()
            if not delegation_name in personal_list:
                personal_list[delegation_name] = collections.OrderedDict()
            if not diocesis_name in personal_list[delegation_name]:
                personal_list[delegation_name][diocesis_name] = []
            personal_list[delegation_name][diocesis_name].append([personal_obj.get_personal_id(),personal_obj.get_personal_name(),personal_obj.get_responability_belongs_to() ])

    return personal_list

def get_delegados_regionales():
    '''
    Description:
        The function get the delegados regionales ordered by delegation
    Return:
        Return delegados_list
    '''
    delegados_list = collections.OrderedDict()
    if PersonalIglesia.objects.filter(cargo__entidadCargo__entidad__exact = 'Delegación').exclude(personalActivo = False).exists():
        personal_objs = PersonalIglesia.objects.filter(cargo__entidadCargo__entidad__exact = 'Delegación').exclude(personalActivo = False).order_by('delegacion').order_by('cargo__nombreCargo')
        for personal_obj in personal_objs:
            delegation_name = personal_obj.get_delegacion_belongs_to()
            if not delegation_name in delegados_list:
                delegados_list[delegation_name] = []
            delegados_list[delegation_name].append(['iglesia'  , personal_obj.get_personal_id(),personal_obj.get_personal_name(),personal_obj.get_responability_belongs_to(),personal_obj.get_movil_number(),personal_obj.get_email() ])
    if PersonalExterno.objects.filter(cargo__entidadCargo__entidad__exact = 'Delegación').exclude(personalActivo = False).exists():
        personal_objs = PersonalExterno.objects.filter(cargo__entidadCargo__entidad__exact = 'Delegación').exclude(personalActivo = False).order_by('grupoAsociado__diocesisDependiente__delegacionDependiente').order_by('cargo__nombreCargo')
        for personal_obj in personal_objs:
            delegation_name = personal_obj.get_delegacion_belongs_to()
            if not delegation_name in delegados_list:
                delegados_list[delegation_name] = []
            delegados_list[delegation_name].append(['externo' , personal_obj.get_personal_id(),personal_obj.get_personal_name(),personal_obj.get_responability_belongs_to(),personal_obj.get_movil_number(),personal_obj.get_email() ])

    return delegados_list

def get_excel_user_request_boletin():
    '''
    Description:
        The function get the user and their mail addres to send the boletin
    Return:
        Return the path for collecting the boletin
    '''
    import xlsxwriter
    f_name =  'Listado_boletin.xlsx'
    heading = ['Nombre', 'Apellidos', 'Tipo de colaboración' ,'Calle','Población', 'Provincia', 'Código Postal']
    lista = [heading]
    if PersonalExterno.objects.filter(recibirBoletin = True).exclude(personalActivo = False).exists():
        externo_objs = PersonalExterno.objects.filter(recibirBoletin = True).exclude(personalActivo = False).order_by('codigoPostal')
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_boletin())

    if PersonalIglesia.objects.filter(recibirBoletin = True).exists():
        externo_objs = PersonalIglesia.objects.filter(recibirBoletin = True).exclude(personalActivo = False).order_by('codigoPostal')
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_boletin())
    excel_file = os.path.join(settings.MEDIA_ROOT, f_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(lista):
            worksheet.write_row(row_num, 0, data)
    return os.path.join(settings.MEDIA_URL,f_name)

def store_file (user_file):
    '''
    Description:
        The function save the user input file
    Input:
        request # contains the session information
    Return:
        Return True if the user belongs to Wetlab Manager, False if not
    '''
    import time
    filename, file_extension = os.path.splitext(user_file.name)
    file_name = filename+ '_' + str( time.strftime("%Y%m%d-%H%M%S")) + file_extension
    fs = FileSystemStorage()
    filename = fs.save(file_name,  user_file)
    #saved_file = os.path.join(settings.MEDIA_ROOT, file_name)
    return file_name
