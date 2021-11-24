from aicespana.models import *


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
            cargo_objs = Cargo.objects.filter(entidadCargo__entidad__iexact = 'delegación')
            for cargo_obj in cargo_objs:
                cargo_name = cargo_obj.get_cargo_name()
                if PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).exists():
                    user_name = PersonalExterno.objects.filter(cargo__nombreCargo__exact = cargo_name).last().get_personal_name()
                else:
                    user_name = 'Puesto vacante'
                delegation_data['cargos'].append([cargo_name, user_name ])

    return delegation_data


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
    personal_responsability['group'] = personal_obj.get_group_belongs_to()
    personal_responsability['project'] = personal_obj.get_project_belongs_to()
    personal_responsability['activity'] = personal_obj.get_activity_belongs_to()
    personal_responsability['responsability'] = personal_obj.get_responability_belongs_to()
    personal_responsability['collaboration'] = personal_obj.get_collaboration_belongs_to()
    personal_responsability['group'] = personal_obj.get_group_belongs_to()
    personal_responsability['parroquia'] = personal_obj.get_parroquia_belongs_to()
    personal_responsability['diocesis'] = personal_obj.get_diocesis_belongs_to()
    personal_responsability['delegacion'] = personal_obj.get_delegacion_belongs_to()
    personal_responsability['name'] = personal_obj.get_personal_name()
    return personal_responsability

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
            responsability_optons['available_actitvities'].append([activity_obj.get_actividad_id(),activity_obj.get_activity_name()])
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_optons['available_responsible'].append([responsible_obj.get_cargo_id() , responsible_obj.get_cargo_name()])
    if TipoColaboracion.objects.all().exists():
        colaboration_objs = TipoColaboracion.objects.all().order_by('tipoColaboracion')
        for collaboration_obj in collaboration_objs:
            responsability_optons['available_collaboration'].append([collaboration_obj.get_tipo_colaboracion_id(), collaboration_obj.get_collaboration_name()])
    return responsability_optons

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
