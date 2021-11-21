from aicespana.models import *


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
        group_objs = Grupo.objects.all(),order_by('nombreGrupo')
        for group_obj in group_objs:
            responsability_optons['available_groups'].append(group_obj.get_group_name())
    if Proyecto.objects.all().exists():
        project_objs = Proyecto.objects.all().order_by('nombreProyecto')
        for project_obj in project_objs:
            responsability_optons['available_projects'].append(project_obj.get_project_name())
    if Actividad.objects.all().exists():
        activity_objs = Actividad.objects.all().order_by('nombreActividad')
        for activity_obj in activity_objs:
            responsability_optons['available_actitvities'].append(activity_obj.get_activity_name())
    if Cargo.objects.all().exists():
        responsible_objs = Cargo.objects.all().order_by('nombreCargo')
        for responsible_obj in responsible_objs:
            responsability_optons['available_responsible'].append(responsible_obj.get_responsability_name())
    if TipoColaboracion.objects.all().exists():
        colaboration_objs = TipoColaboracion.objects.all().order_by('tipoColaboracion')
        for collaboration_obj in collaboration_objs:
            responsability_optons['available_collaboration'].append(collaboration_obj.get_collaboration_name())
    return responsability_optons


    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    proyectoAsociado = models.ForeignKey(
                        Proyecto,
                        on_delete=models.CASCADE, null=True, blank = True)
    actividadAsociada = models.ForeignKey(
                        Actividad,
                        on_delete=models.CASCADE, null=True, blank = True)
    cargo = models.ForeignKey(
                        Cargo,
                        on_delete=models.CASCADE, null=True, blank = True)
    tipoColaboracion
