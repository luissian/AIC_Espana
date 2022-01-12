from aicespana.models import *
from django.contrib.auth.models import Group, User

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
        delegation_id   # id of the deletation
    Return:
        delegation_id_name_list
    '''
    return Delegacion.objects.filter(pk__exact = delegation_id).last()

def get_diocesis_data(diocesis_id):
    '''
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        diocesis_id  # id of the diocesis
    Return:
        diocesis_data
    '''
    diocesis_data = {}
    diocesis_data['cargos'] = []
    if Diocesis.objects.filter(pk__exact = diocesis_id).exists():
        diocesis_obj = Diocesis.objects.filter(pk__exact = diocesis_id).last()
        diocesis_data['diocesis_name'] = diocesis_obj.get_diocesis_name()
        if Parroquia.objects.filter(diocesisDependiente = diocesis_obj).exists():
            diocesis_data['parroquias'] = []
            parroquia_objs = Parroquia.objects.filter(diocesisDependiente = diocesis_obj)
            for parroquia_obj in parroquia_objs :
                diocesis_data['parroquias'].append(parroquia_obj.get_parroquia_name())
            diocesis_data['poblacion'] = parroquia_obj.get_poblacion_name()
            diocesis_data['provincia'] = parroquia_obj.get_provincia_name()
        if Cargo.objects.filter(entidadCargo__entidad__iexact = 'diocesis').exists():
            cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'diocesis').order_by('nombreCargo')
            for cargo_obj in cargo_objs:
                cargo_name = cargo_obj.get_cargo_name()
                if PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).exists():
                    personal_obj = PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).last()
                    diocesis_data['cargos'].append([cargo_name , personal_obj.get_personal_name(), personal_obj.get_full_address_in_one_line(),
                    personal_obj.get_movil_number(), personal_obj,get_telefone(), personal_obj.get_email()])
                else:
                    diocesis_data['cargos'].append([cargo_name, 'Sin Asignar' , '--' , '--', '--', '--'])

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
    personal_responsability['activity'] = personal_obj.get_activity_belongs_to()
    personal_responsability['activity_id'] = personal_obj.get_activity_id_belongs_to()
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
    personal_responsability['responsability'] = personal_obj.get_responability_belongs_to()
    personal_responsability['responsability_id'] = personal_obj.get_responability_id_belongs_to()
    personal_responsability['delegacion'] = personal_obj.get_delegacion_belongs_to()
    personal_responsability['delegacion_id'] = personal_obj.get_delegacion_id_belongs_to()
    personal_responsability['name'] = personal_obj.get_personal_name()
    return personal_responsability

def get_provincias():

    list_provincias =['Albacete', 'Alicante','Almería,''Álava','Asturias','Ávila','Badajoz','Baleares','Barcelona','Bizkaia','Burgos',
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
    responsability_options['available_responsible'] = []
    if Grupo.objects.all().exists():
        group_objs = Grupo.objects.all().order_by('nombreGrupo')
        for group_obj in group_objs:
            responsability_options['available_groups'].append([group_obj.get_group_id(), group_obj.get_group_name(), group_obj.get_parroquia_name()])
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_options['available_responsible'].append([responsible_obj.get_cargo_id() , responsible_obj.get_cargo_name()])
    if Delegacion.objects.all().exists():
        delegacion_objs = Delegacion.objects.all().order_by('nombreDelegacion')
        for delegacion_obj in delegacion_objs:
            responsability_options['available_delegacion'].append([delegacion_obj.get_delegation_id(), delegacion_obj.get_delegacion_name()])
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
            responsability_optons['available_groups'].append([group_obj.get_group_id(), group_obj.get_group_name(), group_obj.get_parroquia_name()])
    if Proyecto.objects.all().exists():
        project_objs = Proyecto.objects.all().order_by('nombreProyecto')
        for project_obj in project_objs:
            responsability_optons['available_projects'].append([project_obj.get_proyecto_id(), project_obj.get_project_name()])
    if Actividad.objects.all().exists():
        activity_objs = Actividad.objects.all().order_by('nombreActividad')
        for activity_obj in activity_objs:
            responsability_optons['available_actitvities'].append([activity_obj.get_activity_id(),activity_obj.get_activity_name()])
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_optons['available_responsible'].append([responsible_obj.get_cargo_id() , responsible_obj.get_cargo_name()])
    if TipoColaboracion.objects.all().exists():
        collaboration_objs = TipoColaboracion.objects.all().order_by('tipoColaboracion')
        for collaboration_obj in collaboration_objs:
            responsability_optons['available_collaboration'].append([collaboration_obj.get_tipo_colaboracion_id(), collaboration_obj.get_collaboration_name()])
    return responsability_optons

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
            if PersonalExterno.objects.filter(cargo = cargo_obj, grupoAsociado = group_obj).exists():
                personal_obj = PersonalExterno.objects.filter(cargo = cargo_obj, grupoAsociado = group_obj).last()
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
        if PersonalExterno.objects.filter(grupoAsociado = group_obj).exists():
            voluntarios_data['older_than_80'] = []
            voluntarios_data['younger_than_80'] = []
            personal_objs = PersonalExterno.objects.filter(grupoAsociado = group_obj).order_by('apellido')
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


def get_personel_obj_from_id(user_id):
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
        The function will check if the logged user belongs to wetlab
        manager group
    Input:
        request # contains the session information
    Return:
        Return True if the user belongs to Wetlab Manager, False if not
    '''
    try:
        groups = Group.objects.get(name = 'responsable')
        if groups not in request.user.groups.all():
            return False
    except:
        return False

    return True
