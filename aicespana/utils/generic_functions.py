from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Avg, F, Count, Func, Value, CharField
import collections
import os
import xlsxwriter

import aicespana.models
import aicespana.utils.graphics


def allow_see_group_information_voluntary(request, group_obj):
    """
    Description:
        The function will check if the logged user belongs to administracion,
        presidenta nacional to see all delegaciones  or has the
        presidenta diocesana responsability and belongs to the same delegacion
    Input:
        request # contains the session information
        group_obj   # object of the grouo
    Return:
        Return True if the user can see group lists, False if not
    """
    try:
        administracion_groups = Group.objects.get(name="administracion")
        if administracion_groups not in request.user.groups.all():
            todas_delegaciones = Group.objects.get(name="todasDelegaciones")
            if todas_delegaciones not in request.user.groups.all():
                nombre_usuario = request.user.first_name
                apellido_usuario = request.user.last_name
                if not aicespana.models.PersonalExterno.objects.filter(
                    nombre__iexact=nombre_usuario, apellido__iexact=apellido_usuario
                ).exists():
                    return False
                usuario_obj = aicespana.models.PersonalExterno.objects.filter(
                    nombre__iexact=nombre_usuario, apellido__iexact=apellido_usuario
                ).last()
                if "Presidenta Nacional" in usuario_obj.get_responability_belongs_to():
                    return True
                if (
                    "Delegada Regional"
                    not in usuario_obj.get_responability_belongs_to()
                ):
                    return False
                if (
                    usuario_obj.get_delegacion_belongs_to()
                    != group_obj.get_delegacion_name()
                ):
                    return False
                return True
    except Exception:
        return False
    return True


def check_exists_grupo(grupo_name, diocesis_id):
    """
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        grupo_name  # Name of the grupo
        diocesis_id     # id of the diocesis
    Return:
        True/False
    """
    return aicespana.models.Grupo.objects.filter(
        nombreGrupo__iexact=grupo_name, diocesisDependiente__pk__exact=diocesis_id
    ).exists()


def check_exists_parroquia(parroquia_name, diocesis_id):
    """
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        parroquia_name  # Name of the parroquia
        diocesis_id     # id of the diocesis
    Return:
        True/False
    """
    return aicespana.models.Parroquia.objects.filter(
        nombreParroquia__iexact=parroquia_name,
        diocesisDependiente__pk__exact=diocesis_id,
    ).exists()


def check_delegada_regional(user):
    """
    Description:
        The function return if user is delegada regional.
    Input:
        user
    Return:
        True/False
    """
    nombre_usuario = user.first_name
    apellido_usuario = user.last_name
    if not aicespana.models.PersonalExterno.objects.filter(
        nombre__iexact=nombre_usuario, apellido__iexact=apellido_usuario
    ).exists():
        return False
    usuario_obj = aicespana.models.PersonalExterno.objects.filter(
        nombre__iexact=nombre_usuario, apellido__iexact=apellido_usuario
    ).last()
    if usuario_obj.get_responability_belongs_to() == "Delegada Regional":
        return True
    return False


def get_actividades_information(user_type, region=None):
    """
    Description:
        Get the list of activities
    """
    if not aicespana.models.Actividad.objects.filter(actividadActiva=True).exists():
        return data
    if user_type == "manager":
        act_objs = aicespana.models.Actividad.objects.all().exclude(
            actividadActiva=False
        )
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True
        ).exclude(actividadAsociada=None)

    elif user_type == "user" and region is not None:
        act_list = (
            aicespana.models.PersonalExterno.objects.filter(
                grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region,
                personalActivo=True,
            )
            .exclude(actividadAsociada=None)
            .values_list("actividadAsociada__nombreActividad", flat=True)
            .distinct()
        )
        act_objs = []
        for act in act_list:
            act_objs.append(
                aicespana.models.Actividad.objects.filter(
                    nombreActividad__exact=act
                ).last()
            )
        p_ext_objs = (
            aicespana.models.PersonalExterno.objects.filter(
                grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region,
                personalActivo=True,
            )
            .exclude(actividadAsociada=None)
            .values("actividadAsociada__nombreActividad")
        )
    else:
        return
    data = []

    for act_obj in act_objs:
        group_list = list(
            p_ext_objs.filter(actividadAsociada=act_obj)
            .values_list(
                "grupoAsociado__nombreGrupo",
                "grupoAsociado__diocesisDependiente__nombreDiocesis",
                "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion",
            )
            .distinct()
        )
        for group in group_list:
            grp_list = list(group)
            grp_list += act_obj.get_actividad_full_data()
            data.append(grp_list)

    return data


def get_activity_data_in_delegations(actividad_id):
    """
    Description:
        Get the delegaions and the summery information in the activity
    """
    data = {"summary": [0, 0], "delegaciones": {}, "user_list": []}
    actividad_obj = get_actividad_obj_from_id(actividad_id)
    data["actividad_name"] = actividad_obj.get_actividad_name()

    if not aicespana.models.PersonalExterno.objects.filter(
        personalActivo=True, actividadAsociada=actividad_obj
    ).exists():
        return data
    volunt_objs = aicespana.models.PersonalExterno.objects.filter(
        personalActivo=True, actividadAsociada=actividad_obj
    ).order_by("grupoAsociado__diocesisDependiente__delegacionDependiente")
    data["summary"] = [len(volunt_objs)]
    for volunt_obj in volunt_objs:
        delegacion = volunt_obj.get_delegacion_belongs_to()
        if delegacion not in data["delegaciones"]:
            data["delegaciones"][delegacion] = 0
        data["delegaciones"][delegacion] += 1
        data["user_list"].append(volunt_obj.get_data_for_actividad())
    data["summary"].append(len(data["delegaciones"]))
    data["heading"] = [
        "Nombre Apellidos",
        "Actividad",
        "Grupo",
        "Diocesis",
        "Delegación",
    ]
    return data


def get_cargos_per_location(entity, area, area_id):
    """
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        entity # is the entidad cargo
        area  # one of the values delegation/diocesis or group
        area_id # pk of the area
    Return:
        cargos_personal
    """

    cargos_personal = []
    # cargos_personal["cargos"] = []
    if not aicespana.models.Cargo.objects.filter(
        entidadCargo__entidad__iexact=entity
    ).exists():
        return cargos_personal
    cargo_objs = aicespana.models.Cargo.objects.filter(
        entidadCargo__entidad__iexact=entity
    ).order_by("nombreCargo")
    for cargo_obj in cargo_objs:
        if area == "delegation":
            p_ext_objs = cargo_obj.personalexterno_set.filter(
                grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=area_id
            ).exclude(personalActivo=False)
            if len(p_ext_objs) == 0:
                # check if cargo belongs to personal iglesia
                p_ext_objs = cargo_obj.personaliglesia_set.filter(
                    grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=area_id
                ).exclude(personalActivo=False)
                if len(p_ext_objs) == 0:
                    cargos_personal.append([cargo_obj.get_cargo_name(), ""])
                    continue
        elif area == "diocesis":
            p_ext_objs = cargo_obj.personalexterno_set.filter(
                grupoAsociado__diocesisDependiente__pk__exact=area_id
            ).exclude(personalActivo=False)
            if len(p_ext_objs) == 0:
                p_ext_objs = cargo_obj.personaliglesia_set.filter(
                    grupoAsociado__diocesisDependiente__pk__exact=area_id
                ).exclude(personalActivo=False)
                if len(p_ext_objs) == 0:
                    cargos_personal.append([cargo_obj.get_cargo_name(), ""])
                    continue
        elif area == "grupo":
            p_ext_objs = cargo_obj.personalexterno_set.filter(
                grupoAsociado__pk__exact=area_id
            ).exclude(personalActivo=False)
            if len(p_ext_objs) == 0:
                p_ext_objs = cargo_obj.personaliglesia_set.filter(
                    grupoAsociado__pk__exact=area_id
                ).exclude(personalActivo=False)
                if len(p_ext_objs) == 0:
                    cargos_personal.append([cargo_obj.get_cargo_name(), ""])
                    continue
        else:
            return cargos_personal
        for p_ext_obj in p_ext_objs:
            cargos_personal.append(
                [cargo_obj.get_cargo_name(), p_ext_obj.get_personal_name()]
            )

    return cargos_personal


def graphic_p_ext_per_activity(region):
    """Create a pie chart of voluntarios doing activities per region

    Parameters
    ----------
    region : _type_
        _description_
    """
    if region == "" or region is None:
        p_ext_per_activity = list(
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(actividadAsociada=None)
            .exclude(grupoAsociado=None)
            .values(
                delegacion=F(
                    "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion"
                )
            )
            .annotate(total=Count("actividadAsociada__nombreActividad"))
        )

        data = aicespana.utils.graphics.conversion_data(
            p_ext_per_activity, "delegacion", "total", "list"
        )
        title = "Voluntarios por delegación"
    else:
        diocesis_objs = aicespana.models.Diocesis.objects.filter(
            delegacionDependiente__nombreDelegacion__iexact=region
        )
        p_ext_per_activity = list(
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .exclude(actividadAsociada=None)
            .exclude(grupoAsociado=None)
            .values(diocesis=F("grupoAsociado__diocesisDependiente__nombreDiocesis"))
            .annotate(total=Count("actividadAsociada__nombreActividad"))
        )

        data = aicespana.utils.graphics.conversion_data(
            p_ext_per_activity, "diocesis", "total", "list"
        )
        title = "Voluntarios por diocesis"

    options = {"title": title}
    return aicespana.utils.graphics.pie_graphic(data["label"], data["value"], options)


def graphic_p_ext_asigned_activity(region):
    """Create a pie graph for the voluntarios asigned/no asigned to activity

    Parameters
    ----------
    region : string
        Name of the region for filtering data. if empty all regions are
        considered
    """
    labels = []
    values = []
    if region == "" or region is None:
        labels.append("En actividad")
        values.append(
            (
                aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
                .exclude(actividadAsociada=None)
                .exclude(grupoAsociado=None)
                .count()
            )
        )
        labels.append("Sin asignar")
        values.append(
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True, actividadAsociada=None
            )
            .exclude(grupoAsociado=None)
            .count()
        )
        num_no_grp = (
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True, grupoAsociado=None
            )
            .exclude(actividadAsociada=None)
            .count()
        )
        if num_no_grp > 0:
            labels.append("Con actividad y sin grupo")
            values.append(num_no_grp)
        num_no_grp_no_act = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True, actividadAsociada=None, grupoAsociado=None
        ).count()
        if num_no_grp_no_act > 0:
            labels.append("Sin actividad y sin grupo")
            values.append(num_no_grp_no_act)
        title = "Voluntarios en las delegaciones"
    else:
        diocesis_objs = aicespana.models.Diocesis.objects.filter(
            delegacionDependiente__nombreDelegacion__iexact=region
        )
        labels.append("En actividad")
        values.append(
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .exclude(actividadAsociada=None)
            .count()
        )
        labels.append("Sin asignar")
        values.append(
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
                actividadAsociada=None,
            ).count()
        )
        title = "Voluntarios en la delegación"
    options = {"title": title}

    return aicespana.utils.graphics.pie_graphic(labels, values, options)


def graphic_activity_per_p_ext(region):
    """Create a pie graph for the voluntarios asigned/no asigned to activity

    Parameters
    ----------
    region : string
        Name of the region for filtering data. if empty all regions are
        considered
    """
    if region == "" or region is None:
        act_voluntarios = (
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(actividadAsociada=None)
            .values(actividad=F("actividadAsociada__nombreActividad"))
            .annotate(total=Count("nombre"))
        )
    else:
        diocesis_objs = aicespana.models.Diocesis.objects.filter(
            delegacionDependiente__nombreDelegacion__iexact=region
        )
        act_voluntarios = (
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .values(actividad=F("actividadAsociada__nombreActividad"))
            .annotate(total=Count("nombre"))
        )
    data = aicespana.utils.graphics.conversion_data(
        act_voluntarios, "actividad", "total", "list"
    )
    title = "Numero de voluntarios por actividad"
    options = {
        "title": title,
        "height": 500,
        "width": 900,
        "yaxis": "Numero de voluntarios",
    }
    return aicespana.utils.graphics.bar_graphic(data["label"], data["value"], options)


def graphic_act_per_delegation(region):
    graph = {}
    if region == "" or region is None:
        act_delegations = list(
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(actividadAsociada=None)
            .exclude(grupoAsociado=None)
            .values(
                delegacion=F(
                    "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion"
                )
            )
            .annotate(actividad=F("actividadAsociada__nombreActividad"))
            .distinct()
        )
        activities = {}
        for act_delegation in act_delegations:
            if act_delegation["actividad"] not in activities:
                activities[act_delegation["actividad"]] = 0
            activities[act_delegation["actividad"]] += 1
        labels = []
        values = []
        for act, val in activities.items():
            labels.append(act)
            values.append(val)
        graph["num_activities"] = len(labels)
        total_activity = aicespana.models.Actividad.objects.filter(
            actividadActiva=True
        ).count()
        if total_activity > len(labels):
            values.append(total_activity - len(labels))
            labels.append("Sin asociar a grupo")

        title = "Actividades por delegación"
        options = {"title": title}

        options = {
            "title": title,
            "height": 500,
            "width": 900,
            "yaxis": "Numero de actividades por delegación",
        }
        graph["graph"] = aicespana.utils.graphics.bar_graphic(labels, values, options)
    return graph


def graphics_per_activity(region):
    """Create a pie chart for voluntarios per delegation/diocesis.
        Create a pie charr for the percentage of voluntarios asigned to projects
    Parameters
    ----------
    region : string
        name of the region to create the graphic
    """
    graphics = {}
    graphics["num_per_ext"] = graphic_p_ext_per_activity(region)
    graphics["act_per_ext"] = graphic_p_ext_asigned_activity(region)
    if region == "" or region is None:
        graphics["act_per_delegation"] = graphic_act_per_delegation(region)
    graphics["num_voluntarios"] = graphic_activity_per_p_ext(region)
    return graphics

    """ 
    # graphic having activities and number of voluntarios
    if region == "" or region is None:
        act_voluntarios = (
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(actividadAsociada=None)
            .values(actividad=F("actividadAsociada__nombreActividad"))
            .annotate(total=Count("nombre"))
        )
    else:
        act_voluntarios = (
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                actividadAsociada__grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .values(actividad=F("actividadAsociada__nombreActividad"))
            .annotate(total=Count("nombre"))
        )
    data = aicespana.utils.graphics.conversion_data(
        act_voluntarios, "actividad", "total", "list"
    )
    title = "Numero de voluntarios por actividad"
    options = {
        "title": title,
        "height": 500,
        "width": 900,
        "yaxis": "Numero de voluntarios",
    }
    graphics["num_voluntarios"] = aicespana.utils.graphics.bar_graphic(
        data["label"], data["value"], options
    )
    return graphics
 """


def graphic_p_ext_per_project(region):
    """Create a pie chart based on region."""
    if region == "" or region is None:
        p_ext_per_projects = list(
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(proyectoAsociado=None)
            .exclude(grupoAsociado=None)
            .values(
                delegacion=F(
                    "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion"
                )
            )
            .annotate(total=Count("proyectoAsociado__nombreProyecto"))
        )

        data = aicespana.utils.graphics.conversion_data(
            p_ext_per_projects, "delegacion", "total", "list"
        )
        title = "Voluntarios por delegación"
    else:
        diocesis_objs = aicespana.models.Diocesis.objects.filter(
            delegacionDependiente__nombreDelegacion__iexact=region
        )
        p_ext_per_projects = list(
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .exclude(proyectoAsociado=None)
            .exclude(grupoAsociado=None)
            .values(diocesis=F("grupoAsociado__diocesisDependiente__nombreDiocesis"))
            .annotate(total=Count("proyectoAsociado__nombreProyecto"))
        )

        data = aicespana.utils.graphics.conversion_data(
            p_ext_per_projects, "diocesis", "total", "list"
        )
        title = "Voluntarios por diocesis"

    options = {"title": title}
    return aicespana.utils.graphics.pie_graphic(data["label"], data["value"], options)


def graphic_p_ext_asigned_project(region):
    """Create a pie graph for the voluntarios asigned/no asigned to project

    Parameters
    ----------
    region : string
        Name of the region for filtering data. if empty all regions are
        considered
    """
    if region == "" or region is None:
        p_ext_in_proj = (
            aicespana.models.PersonalExterno.objects.filter(personalActivo=True)
            .exclude(proyectoAsociado=None)
            .count()
        )
        p_ext_not_in_proj = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True, proyectoAsociado=None
        ).count()
        title = "Voluntarios en las delegaciones"
    else:
        diocesis_objs = aicespana.models.Diocesis.objects.filter(
            delegacionDependiente__nombreDelegacion__iexact=region
        )
        p_ext_in_proj = (
            aicespana.models.PersonalExterno.objects.filter(
                personalActivo=True,
                grupoAsociado__diocesisDependiente__in=diocesis_objs,
            )
            .exclude(proyectoAsociado=None)
            .count()
        )
        p_ext_not_in_proj = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True,
            grupoAsociado__diocesisDependiente__in=diocesis_objs,
            proyectoAsociado=None,
        ).count()
        title = "Voluntarios en la delegación"
    options = {"title": title}

    return aicespana.utils.graphics.pie_graphic(
        ["En projectos", "Sin asignar"], [p_ext_in_proj, p_ext_not_in_proj], options
    )


def graphics_per_project(region):
    """Create a pie chart for voluntarios per delegation/diocesis.
        Create a pie charr for the percentage of voluntarios asigned to projects
    Parameters
    ----------
    region : string
        name of the region to create the graphic
    """
    graphics = {}
    graphics["num_per_ext"] = graphic_p_ext_per_project(region)
    graphics["per_per_ext"] = graphic_p_ext_asigned_project(region)
    return graphics


def delegation_name_list():
    """
    Description:
        The function gets a list with all delegation names.
    Return:
        delegation_name_list
    """
    delegation_name_list = []
    delegacion_objs = aicespana.models.Delegacion.objects.all().order_by(
        "nombreDelegacion"
    )
    for delegacion_obj in delegacion_objs:
        delegation_name_list.append(delegacion_obj.get_delegacion_name())
    return delegation_name_list


def delegacion_name_from_loged_user(username):
    if aicespana.models.Delegacion.objects.filter(login_user__iexact=username).exists():
        return (
            aicespana.models.Delegacion.objects.filter(login_user__iexact=username)
            .last()
            .get_delegacion_name()
        )

    return None


def delegation_id_and_name_list():
    """
    Description:
        The function gets a list with the ids and delegation names.
    Return:
        delegation_id_name_list
    """
    delegation_id_name_list = []
    delegacion_objs = aicespana.models.Delegacion.objects.all().order_by(
        "nombreDelegacion"
    )
    for delegacion_obj in delegacion_objs:
        delegation_id_name_list.append(
            [delegacion_obj.get_delegacion_id(), delegacion_obj.get_delegacion_name()]
        )
    return delegation_id_name_list


def get_delegacion_id_from_name(delegation_name):
    """
    Description:
        The function return the delegation id from their name.
    Input:
        delegation_name   # name of the delegation
    Return:
        id of delegation
    """
    if aicespana.models.Delegacion.objects.filter(
        nombreDelegacion__iexact=delegation_name
    ).exists():
        return (
            aicespana.models.Delegacion.objects.filter(
                nombreDelegacion__iexact=delegation_name
            )
            .last()
            .get_delegacion_id()
        )
    return None


def get_delegation_obj_from_id(delegation_id):
    """
    Description:
        The function return the delegation object from their id.
    Input:
        delegation_id   # id of the delegation
    Return:
        object of delegation instance
    """
    return aicespana.models.Delegacion.objects.filter(pk__exact=delegation_id).last()


def get_summary_of_delegation(delegation_obj):
    """
    Description:
        The function return the summary data (number of voluntarios, number of grupos and number of diocesis
    Input:
        delegation_obj   # object of the delegation
    Return:
        summary_data
    """
    num_diocesis = aicespana.models.Diocesis.objects.filter(
        delegacionDependiente=delegation_obj, diocesisActiva=True
    ).count()
    num_grupos = aicespana.models.Grupo.objects.filter(
        diocesisDependiente__delegacionDependiente=delegation_obj, grupoActivo=True
    ).count()
    num_voluntarios = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado__diocesisDependiente__delegacionDependiente=delegation_obj,
        personalActivo=True,
    ).count()
    return [num_voluntarios, num_grupos, num_diocesis]


def get_summary_of_diocesis(diocesis_obj):
    """
    Description:
        The function return the summary data (number of voluntarios and  number of grupos
    Input:
        delegation_obj   # object of the diocesis
    Return:
        summary_data
    """
    num_grupos = aicespana.models.Grupo.objects.filter(
        diocesisDependiente=diocesis_obj, grupoActivo=True
    ).count()
    num_voluntarios = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado__diocesisDependiente=diocesis_obj, personalActivo=True
    ).count()
    return [num_voluntarios, num_grupos]


def get_summary_of_group(grupo_obj):
    """
    Description:
        The function return the summary data (number of voluntarios)
    Input:
        delegation_obj   # object of the diocesis
    Return:
        summary_data
    """
    num_voluntarios = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        personalActivo="True",
        tipoColaboracion__tipoColaboracion="Voluntario",
    ).count()
    num_colaboradores = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        personalActivo="True",
        tipoColaboracion__tipoColaboracion="Colaborador",
    ).count()
    num_asesores = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        personalActivo="True",
        tipoColaboracion__tipoColaboracion="Asesor",
    ).count()
    num_total = aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj, personalActivo="True"
    ).count()
    num_otros = num_total - num_voluntarios - num_colaboradores - num_asesores
    return [num_voluntarios, num_colaboradores, num_asesores, num_otros]


def get_diocesis_obj_from_id(diocesis_id):
    """
    Description:
        The function return the diocesis object from their id.
    Input:
        delegation_id   # id of the diocesis
    Return:
        object of diocesis instance
    """
    return aicespana.models.Diocesis.objects.filter(pk__exact=diocesis_id).last()


def get_diocesis_id_name_and_delegation_name():
    """
    Description:
        The function gets the diocesis id , the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    """
    diocesis_data = []
    diocesis_objs = aicespana.models.Diocesis.objects.all().order_by(
        "delegacionDependiente"
    )
    for diocesis_obj in diocesis_objs:
        diocesis_data.append(
            [
                diocesis_obj.get_diocesis_id(),
                diocesis_obj.get_diocesis_name(),
                diocesis_obj.get_delegacion_name(),
            ]
        )
    return diocesis_data


def get_diocesis_name_and_delegation_name():
    """
    Description:
        The function gets the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    """
    diocesis_data = []
    diocesis_objs = aicespana.models.Diocesis.objects.all().order_by(
        "delegacionDependiente"
    )
    for diocesis_obj in diocesis_objs:
        diocesis_data.append(
            [diocesis_obj.get_diocesis_name(), diocesis_obj.get_delegacion_name()]
        )
    return diocesis_data


def get_diocesis_id_name_list():
    """
    Description:
        The function gets the diocesis id and name
    Return:
        diocesis_data
    """
    diocesis_data = []
    diocesis_objs = aicespana.models.Diocesis.objects.all().order_by("nombreDiocesis")
    for diocesis_obj in diocesis_objs:
        diocesis_data.append(
            [diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()]
        )
    return diocesis_data


def get_diocesis_in_delegation(delegacion_obj):
    """
    Description:
        The function gets the diocesis id and name of one delegacion
    Input:
        delegacion_obj  # object of delegacion
    Return:
        diocesis_data
    """
    diocesis_data = []
    diocesis_objs = aicespana.models.Diocesis.objects.filter(
        delegacionDependiente=delegacion_obj
    ).order_by("delegacionDependiente")
    for diocesis_obj in diocesis_objs:
        diocesis_data.append(
            [diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()]
        )
    return diocesis_data


def get_groups_in_diocesis(diocesis_obj, situation):
    """
    Description:
        The function gets the grupos and their id from a diocesis
    Input:
        diocesis_obj  # object of diocesis
        situation True or False for getting active or close
    Return:
        groups_data
    """
    groups_data = []
    if aicespana.models.Grupo.objects.filter(
        diocesisDependiente=diocesis_obj, grupoActivo=situation
    ).exists():
        grupo_objs = aicespana.models.Grupo.objects.filter(
            diocesisDependiente=diocesis_obj, grupoActivo=situation
        ).order_by("nombreGrupo")
        for grupo_obj in grupo_objs:
            groups_data.append([grupo_obj.get_grupo_id(), grupo_obj.get_grupo_name()])
    return groups_data


def get_grupo_cargos_personal(grupo_obj):
    """
    Description:
        The function gets the information and the personal name and the responsability.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        cargos_data
    """
    cargos_data = {}
    if aicespana.models.Cargo.objects.filter(
        entidadCargo__entidad__iexact="grupo"
    ).exists():
        cargo_objs = aicespana.models.Cargo.objects.filter(
            entidadCargo__entidad__iexact="grupo"
        ).order_by("nombreCargo")
        for cargo_obj in cargo_objs:
            cargo_name = cargo_obj.get_cargo_name()
            if aicespana.models.PersonalIglesia.objects.filter(
                cargo__nombreCargo__exact=cargo_name, grupoAsociado=grupo_obj
            ).exists():
                personal_obj = aicespana.models.PersonalIglesia.objects.filter(
                    cargo__nombreCargo__exact=cargo_name, grupoAsociado=grupo_obj
                ).last()
                cargos_data[cargo_name] = personal_obj.get_personal_name()
            else:
                cargos_data[cargo_name] = "Sin Asignar"
    return cargos_data


def get_grupo_voluntarios(grupo_obj):
    """
    Description:
        The function gets the list of voluntarios for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        voluntario_list
    """
    voluntario_list = {"mayor80": [], "menor80": [], "sin_edad": []}

    if aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        tipoColaboracion__tipoColaboracion__exact="Voluntario",
        personalActivo="True",
    ).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado=grupo_obj,
            tipoColaboracion__tipoColaboracion__exact="Voluntario",
            personalActivo="True",
        ).order_by("apellido")
        for personal_obj in personal_objs:
            old = personal_obj.get_old()
            if old == "":
                voluntario_list["sin_edad"].append(personal_obj.get_personal_name())
            elif old >= 80:
                voluntario_list["mayor80"].append(personal_obj.get_personal_name())
            else:
                voluntario_list["menor80"].append(personal_obj.get_personal_name())
    return voluntario_list


def get_grupo_colaboradores(grupo_obj):
    """
    Description:
        The function gets the list of colaboradores for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        colaborador_list
    """
    colaborador_list = {"mayor80": [], "menor80": [], "sin_edad": []}
    if aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        tipoColaboracion__tipoColaboracion__exact="Colaborador",
        personalActivo="True",
    ).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado=grupo_obj,
            tipoColaboracion__tipoColaboracion__exact="Colaborador",
            personalActivo="True",
        ).order_by("apellido")
        for personal_obj in personal_objs:
            old = personal_obj.get_old()
            if old == "":
                colaborador_list["sin_edad"].append(personal_obj.get_personal_name())
            elif old >= 80:
                colaborador_list["mayor80"].append(personal_obj.get_personal_name())
            else:
                colaborador_list["menor80"].append(personal_obj.get_personal_name())
    return colaborador_list


def get_grupo_asesores(grupo_obj):
    """
    Description:
        The function gets the list of asesores for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        asesor_list
    """
    asesor_list = {"mayor80": [], "menor80": [], "sin_edad": []}
    if aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado=grupo_obj,
        tipoColaboracion__tipoColaboracion__exact="Asesor",
        personalActivo="True",
    ).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado=grupo_obj,
            tipoColaboracion__tipoColaboracion__exact="Asesor",
            personalActivo="True",
        ).order_by("apellido")
        for personal_obj in personal_objs:
            old = personal_obj.get_old()
            if old == "":
                asesor_list["sin_edad"].append(personal_obj.get_personal_name())
            elif old >= 80:
                asesor_list["mayor80"].append(personal_obj.get_personal_name())
            else:
                asesor_list["menor80"].append(personal_obj.get_personal_name())
    return asesor_list


def get_grupo_otros(grupo_obj):
    """
    Description:
        The function gets the list of other tipe of colaborations for the group.
    Input:
        grupo_obj  # obj of the grupo
    Return:
        otros_list
    """
    otros_list = {"mayor80": [], "menor80": [], "sin_edad": []}
    colaboration_list = ["Voluntario", "Asesor", "Colaborador"]
    if (
        aicespana.models.PersonalExterno.objects.filter(grupoAsociado=grupo_obj)
        .exclude(tipoColaboracion__tipoColaboracion__in=colaboration_list)
        .exclude(personalActivo=False)
        .exists()
    ):
        personal_objs = (
            aicespana.models.PersonalExterno.objects.filter(grupoAsociado=grupo_obj)
            .exclude(tipoColaboracion__tipoColaboracion__in=colaboration_list)
            .exclude(personalActivo=False)
            .order_by("apellido")
        )
        for personal_obj in personal_objs:
            old = personal_obj.get_old()
            if old == "":
                otros_list["sin_edad"].append(personal_obj.get_personal_name())
            elif old >= 80:
                otros_list["mayor80"].append(personal_obj.get_personal_name())
            else:
                otros_list["menor80"].append(personal_obj.get_personal_name())
    return otros_list


def get_actividad_obj_from_id(actividad_id):
    """
    Description:
        The function return the actividad object from their id.
    Input:
        actividad_id   # id of the actividad
    Return:
        object of actividad instance
    """
    return aicespana.models.Actividad.objects.filter(pk__exact=actividad_id).last()


def get_actividad_data_to_modify(actividad_id):
    """
    Description:
        The function gets the actividad recorded data to modify in the form
    Return:
        actividad_data
    """
    actividad_data = {}
    actividad_obj = get_actividad_obj_from_id(actividad_id)
    data = actividad_obj.get_actividad_full_data()
    extract_list = [
        "actividad_name",
        "actividadID",
        "alta",
        "baja",
        "activo",
        "memoria",
        "fotografia",
    ]
    for index in range(len(extract_list)):
        actividad_data[extract_list[index]] = data[index]
    return actividad_data


def fetch_parroquia_data_to_modify(data_form):
    """
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
    Return:
        data
    """
    data = {}
    extract_list = [
        "parroquia_name",
        "diocesisID",
        "calle",
        "poblacion",
        "provincia",
        "codigo",
        "observaciones",
    ]
    for item in extract_list:
        data[item] = data_form[item]
    return data


def get_parroquia_obj_from_id(parroquia_id):
    """
    Description:
        The function return the parroquia object from their id.
    Input:
        parroquia_id   # id of the parroquia
    Return:
        object of parroquia instance
    """
    return aicespana.models.Parroquia.objects.filter(pk__exact=parroquia_id).last()


def get_id_parroquia_diocesis_delegacion_name():
    """
    Description:
        The function gets the parroquia the diocesis name and the delegation belogs to
    Return:
        diocesis_data
    """
    diocesis_data = collections.OrderedDict()
    if aicespana.models.Parroquia.objects.all().exists():
        delegation_objs = aicespana.models.Delegacion.objects.all().order_by(
            "nombreDelegacion"
        )
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = aicespana.models.Diocesis.objects.filter(
                delegacionDependiente=delegation_obj
            ).order_by("nombreDiocesis")
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                parroquia_objs = aicespana.models.Parroquia.objects.filter(
                    diocesisDependiente=diocesis_obj
                ).order_by("nombreParroquia")
                for parroquia_obj in parroquia_objs:
                    if delegation_name not in diocesis_data:
                        diocesis_data[delegation_name] = []
                    diocesis_data[delegation_name].append(
                        [
                            parroquia_obj.get_parroquia_id(),
                            parroquia_obj.get_parroquia_name(),
                            diocesis_name,
                        ]
                    )
    return diocesis_data


def get_parroquia_data_to_modify(parroquia_id):
    """
    Description:
        The function gets the parroquia recorded data to modify in the form
    Return:
        parroquia_data
    """
    parroquia_data = {}
    parroquia_obj = get_parroquia_obj_from_id(parroquia_id)
    data = parroquia_obj.get_parroquia_full_data()
    extract_list = [
        "parroquia_name",
        "parroquiaID",
        "diocesis_name",
        "diocesis_id",
        "calle",
        "poblacion",
        "provincia",
        "codigo",
        "observaciones",
    ]
    for index in range(len(extract_list)):
        parroquia_data[extract_list[index]] = data[index]
    return parroquia_data


def get_proyecto_obj_from_id(proyecto_id):
    """
    Description:
        The function return the proyecto object from their id.
    Input:
        proyecto_id   # id of the proyecto
    Return:
        object of proyecto instance
    """
    return aicespana.models.Proyecto.objects.filter(pk__exact=proyecto_id).last()


def get_proyecto_data_to_modify(proyecto_id):
    """
    Description:
        The function gets the proyecto recorded data to modify in the form
    Return:
        proyecto_data
    """
    proyecto_data = {}
    proyecto_obj = get_proyecto_obj_from_id(proyecto_id)
    data = proyecto_obj.get_proyecto_full_data()
    extract_list = [
        "proyecto_name",
        "proyectoID",
        "alta",
        "baja",
        "activo",
        "memoria",
        "fotografia",
    ]
    for index in range(len(extract_list)):
        proyecto_data[extract_list[index]] = data[index]
    return proyecto_data


def fetch_grupo_data_to_modify(data_form):
    """
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
    Return:
        data
    """
    data = {}
    extract_list = [
        "grupo_name",
        "diocesisID",
        "calle",
        "poblacion",
        "provincia",
        "codigo",
        "alta",
        "baja",
        "observaciones",
    ]
    for item in extract_list:
        data[item] = data_form[item]
    data["provincia"] = get_provincia_name_from_index(data["provincia"])
    if "activo" in data_form:
        data["activo"] = "true"
    else:
        data["activo"] = "false"
    return data


def get_info_of_voluntarios_personel(personal_objs):
    voluntarios = []
    for personal_obj in personal_objs:
        data = []
        data.append(personal_obj.get_personal_id())
        data.append(personal_obj.get_personal_name())
        data.append(personal_obj.get_group_belongs_to())
        data.append(personal_obj.get_personal_provincia())
        voluntarios.append(data)
    return voluntarios


def get_grupo_obj_from_id(grupo_id):
    """
    Description:
        The function return the grupo object from their id.
    Input:
        grupo_id   # id of the grupo
    Return:
        object of grupo instance
    """
    return aicespana.models.Grupo.objects.filter(pk__exact=grupo_id).last()


def get_id_grupo_diocesis_delegacion_name():
    """
    Description:
        The function gets the group the diocesis name and the delegation belogs to
    Return:
        group_diocesis_data
    """
    group_diocesis_data = []  # collections.OrderedDict()
    if aicespana.models.Grupo.objects.all().exists():
        delegation_objs = aicespana.models.Delegacion.objects.all().order_by(
            "nombreDelegacion"
        )
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = aicespana.models.Diocesis.objects.filter(
                delegacionDependiente=delegation_obj
            ).order_by("nombreDiocesis")
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                grupo_objs = aicespana.models.Grupo.objects.filter(
                    diocesisDependiente=diocesis_obj
                ).order_by("nombreGrupo")
                for grupo_obj in grupo_objs:
                    """
                    if delegation_name not in group_diocesis_data:
                        group_diocesis_data[delegation_name] = []
                    group_diocesis_data[delegation_name].append(
                        [
                            grupo_obj.get_grupo_id(),
                            grupo_obj.get_grupo_name(),
                            diocesis_name,
                        ]
                    )
                    """
                    group_diocesis_data.append(
                        [
                            delegation_name,
                            diocesis_name,
                            grupo_obj.get_grupo_id(),
                            grupo_obj.get_grupo_name(),
                        ]
                    )

    return group_diocesis_data


def get_group_list_to_select_in_form():
    """
    Description:
        The function gets the group the diocesis name to select in the user form
    Return:
        group_data
    """
    group_data = []
    if aicespana.models.Grupo.objects.all().exists():
        grupo_objs = aicespana.models.Grupo.objects.all().order_by("nombreGrupo")
        for grupo_obj in grupo_objs:
            group_data.append(
                [
                    grupo_obj.get_grupo_id(),
                    grupo_obj.get_grupo_name(),
                    grupo_obj.get_diocesis_name(),
                ]
            )
    return group_data


def get_id_grupo_diocesis_name():
    """
    Description:
        The function gets the group and the diocesis name belogs to
    Return:
        group_diocesis_data
    """
    group_diocesis_data = []
    if aicespana.models.Grupo.objects.all().exists():
        diocesis_objs = aicespana.models.Diocesis.objects.all().order_by(
            "nombreDiocesis"
        )
        for diocesis_obj in diocesis_objs:
            diocesis_name = diocesis_obj.get_diocesis_name()
            grupo_objs = aicespana.models.Grupo.objects.filter(
                diocesisDependiente=diocesis_obj
            ).order_by("nombreGrupo")
            for grupo_obj in grupo_objs:
                group_diocesis_data.append(
                    [
                        grupo_obj.get_grupo_id(),
                        grupo_obj.get_grupo_name(),
                        diocesis_name,
                    ]
                )
    return group_diocesis_data


def get_grupo_data_to_modify(grupo_id):
    """
    Description:
        The function gets the grupo recorded data to modify in the form
    Return:
        grupo_data
    """
    grupo_data = {}
    grupo_obj = get_grupo_obj_from_id(grupo_id)
    data = grupo_obj.get_grupo_full_data()
    extract_list = [
        "grupo_name",
        "grupoID",
        "diocesis_name",
        "diocesis_id",
        "calle",
        "poblacion",
        "provincia",
        "codigo",
        "observaciones",
        "alta",
        "baja",
        "activo",
    ]
    for index in range(len(extract_list)):
        grupo_data[extract_list[index]] = data[index]

    return grupo_data


def get_projects_information(user_type, region=None):
    data = []
    if user_type == "manager":
        project_objs = aicespana.models.Proyecto.objects.all().exclude(
            proyectoActivo=False
        )  # .values_list("nombreProyecto", flat=True).distinct()
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True
        ).exclude(proyectoAsociado=None)
    elif user_type == "user" and region is not None:
        project_list = (
            aicespana.models.PersonalExterno.objects.filter(
                grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region
            )
            .exclude(proyectoAsociado=None, personalActivo=False)
            .values_list("proyectoAsociado__nombreProyecto", flat=True)
            .distinct()
        )
        project_objs = []
        for project in project_list:
            project_objs.append(
                aicespana.models.Proyecto.objects.filter(
                    nombreProyecto__exact=project
                ).last()
            )
        p_ext_objs = (
            aicespana.models.PersonalExterno.objects.filter(
                grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region
            )
            .exclude(proyectoAsociado=None)
            .values("proyectoAsociado__nombreProyecto")
        )
    else:
        return

    for project_obj in project_objs:
        group_list = list(
            p_ext_objs.filter(proyectoAsociado=project_obj)
            .values_list(
                "grupoAsociado__nombreGrupo",
                "grupoAsociado__diocesisDependiente__nombreDiocesis",
                "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion",
            )
            .distinct()
        )
        for group in group_list:
            grp_list = list(group)
            grp_list += project_obj.get_proyecto_full_data()
            data.append(grp_list)
    return data


def fetch_actividad_data_to_modify(data_form, file_form):
    """
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
        file_form   # files upload in the form
    Return:
        data
    """
    data = {}
    extract_list = ["actividad_name", "alta", "baja", "activo", "observaciones"]
    for item in extract_list:
        data[item] = data_form[item]
    if "uploadMemoria" in file_form:
        data["memoria_file"] = store_file(file_form["uploadMemoria"])
    if "uploadFotografia" in file_form:
        data["fotografia_file"] = store_file(file_form["uploadFotografia"])
    return data


def fetch_proyecto_data_to_modify(data_form, file_form):
    """
    Description:
        The function extract the information from the user form and return a dictionnary.
    Input:
        data_form   # data collected in the form
        file_form   # files upload in the form
    Return:
        data
    """
    data = {}
    extract_list = [
        "proyecto_name",
        "alta",
        "baja",
        "activo",
        "observaciones",
    ]
    for item in extract_list:
        data[item] = data_form[item]
    if "uploadMemoria" in file_form:
        data["memoria_file"] = store_file(file_form["uploadMemoria"])
    if "uploadFotografia" in file_form:
        data["fotografia_file"] = store_file(file_form["uploadFotografia"])

    return data


def get_id_actividad_name():
    """
    Description:
        The function gets the actividad , grupo the diocesis name and the delegation belogs to
    Return:
        actividad_grupo_diocesis_data
    """
    actividad_data = []
    if aicespana.models.Actividad.objects.all().exists():
        actividad_objs = aicespana.models.Actividad.objects.all().order_by(
            "nombreActividad"
        )
        for actividad_obj in actividad_objs:
            actividad_data.append(
                [actividad_obj.get_actividad_id(), actividad_obj.get_actividad_name()]
            )

    return actividad_data


"""
def get_id_proyectos_grupos_diocesis_delegacion_name():

    proyecto_grupo_diocesis_data = collections.OrderedDict()
    if aicespana.models.Proyecto.objects.all().exists():
        delegation_objs = aicespana.models.Delegacion.objects.all().order_by(
            "nombreDelegacion"
        )
        for delegation_obj in delegation_objs:
            delegation_name = delegation_obj.get_delegacion_name()
            diocesis_objs = aicespana.models.Diocesis.objects.filter(
                delegacionDependiente=delegation_obj
            ).order_by("nombreDiocesis")
            for diocesis_obj in diocesis_objs:
                diocesis_name = diocesis_obj.get_diocesis_name()
                grupo_objs = aicespana.models.Grupo.objects.filter(
                    diocesisDependiente=diocesis_obj
                ).order_by("nombreGrupo")
                for grupo_obj in grupo_objs:
                    grupo_name = grupo_obj.get_grupo_name()
                    proyecto_objs = aicespana.models.Proyecto.objects.filter(
                        grupoAsociado=grupo_obj
                    ).order_by("nombreProyecto")
                    for proyecto_obj in proyecto_objs:
                        if delegation_name not in proyecto_grupo_diocesis_data:
                            proyecto_grupo_diocesis_data[
                                delegation_name
                            ] = collections.OrderedDict()
                        if (
                            diocesis_name
                            not in proyecto_grupo_diocesis_data[delegation_name]
                        ):
                            proyecto_grupo_diocesis_data[delegation_name][
                                diocesis_name
                            ] = []
                        proyecto_grupo_diocesis_data[delegation_name][
                            diocesis_name
                        ].append(
                            [
                                proyecto_obj.get_proyecto_id(),
                                proyecto_obj.get_proyecto_name(),
                                grupo_name,
                            ]
                        )
    return proyecto_grupo_diocesis_data
"""


def get_project_list():
    """
    Description:
        The function gets the proyecto and the diocesis name
    Return:
        proyecto_grupo_diocesis_list
    """
    proyecto_list = []
    if aicespana.models.Proyecto.objects.all().exists():
        proyecto_objs = aicespana.models.Proyecto.objects.all().order_by(
            "nombreProyecto"
        )
        for proyecto_obj in proyecto_objs:
            proyecto_list.append(
                [
                    proyecto_obj.get_proyecto_id(),
                    proyecto_obj.get_proyecto_name(),
                ]
            )
    return proyecto_list


def get_activity_list():
    """
    Description:
        The function gets the proyecto and the diocesis name
    Return:
        proyecto_grupo_diocesis_list
    """
    activity_list = []
    if aicespana.models.Actividad.objects.all().exists():
        actividad_objs = aicespana.models.Actividad.objects.all().order_by(
            "nombreActividad"
        )
        for actividad_obj in actividad_objs:
            activity_list.append(
                [
                    actividad_obj.get_actividad_id(),
                    actividad_obj.get_actividad_name(),
                ]
            )
    return activity_list


def get_external_personal_responsability(personal_obj):
    """
    Description:
        The function gets the voluntary responsability.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        personal_responsability
    """
    personal_responsability = {}
    personal_responsability["project"] = personal_obj.get_project_belongs_to()
    personal_responsability["project_id"] = personal_obj.get_project_id_belongs_to()
    personal_responsability["activity"] = personal_obj.get_actividad_belongs_to()
    personal_responsability["activity_id"] = personal_obj.get_actividad_id_belongs_to()
    personal_responsability[
        "responsability"
    ] = personal_obj.get_responability_belongs_to(include_id=True)
    personal_responsability[
        "collaboration"
    ] = personal_obj.get_collaboration_belongs_to()
    personal_responsability[
        "collaboration_id"
    ] = personal_obj.get_collaboration_id_belongs_to()
    personal_responsability["group"] = personal_obj.get_group_belongs_to()
    personal_responsability["group_id"] = personal_obj.get_group_id_belongs_to()
    personal_responsability["parroquia"] = personal_obj.get_parroquia_belongs_to()
    personal_responsability["diocesis"] = personal_obj.get_diocesis_belongs_to()
    personal_responsability["delegacion"] = personal_obj.get_delegacion_belongs_to()
    personal_responsability["name"] = personal_obj.get_personal_name()

    return personal_responsability


def get_personal_responsability(personal_obj):
    """
    Description:
        The function gets the personal responsability.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        personal_responsability
    """
    personal_responsability = {}
    personal_responsability["group"] = personal_obj.get_group_belongs_to()
    personal_responsability["group_id"] = personal_obj.get_group_id_belongs_to()
    personal_responsability["diocesis"] = personal_obj.get_diocesis_belongs_to()
    personal_responsability[
        "responsability"
    ] = personal_obj.get_responability_belongs_to(include_id=True)
    personal_responsability["delegacion"] = personal_obj.get_delegacion_belongs_to()
    personal_responsability[
        "delegacion_id"
    ] = personal_obj.get_delegacion_id_belongs_to()
    personal_responsability["name"] = personal_obj.get_personal_name()
    return personal_responsability


def get_provincia_index_from_name(prov_name):
    provincias = get_provincias()
    try:
        return str(provincias.index(prov_name))
    except ValueError:
        return "0"


def get_provincia_name_from_index(prov_index):
    provincias = get_provincias()
    try:
        int_index = int(prov_index)
        return provincias[int_index]
    except KeyError:
        return ""


def get_provincias():

    list_provincias = [
        "Albacete",
        "Alicante",
        "Almería",
        "Álava",
        "Asturias",
        "Ávila",
        "Badajoz",
        "Baleares",
        "Barcelona",
        "Bizkaia",
        "Burgos",
        "Cáceres",
        "Cádiz",
        "Cantabria",
        "Castellón",
        "Ciudad Real",
        "Córdoba",
        "Coruña",
        "Cuenca",
        "Guipuzkoa",
        "Girona",
        "Granada",
        "Guadalajara",
        "Huelva",
        "Huesca",
        "Jaén",
        "León",
        "Lleida",
        "Lugo",
        "Madrid",
        "Málaga",
        "Murcia",
        "Navarra",
        "Ourense",
        "Palencia",
        "Palmas, Las",
        "Pontevedra",
        "Rioja, La",
        "Salamanca",
        "Santa Cruz de Tenerife",
        "Segovia",
        "Sevilla",
        "Soria",
        "Tarragona",
        "Teruel",
        "Toledo",
        "Valencia",
        "Valladolid",
        "Zamora",
        "Zaragoza",
        "Ceuta",
        "Melilla",
    ]
    return list_provincias


def get_responsablity_data_for_personel(personal_obj):
    """
    Description:
        The function gets the available options that a personel of AIC can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        responsability_options
    """
    responsability_options = {}
    responsability_options["available_groups"] = []
    responsability_options["available_delegacion"] = []
    responsability_options["available_diocesis"] = []
    responsability_options["available_responsible"] = []
    if aicespana.models.Grupo.objects.all().exists():
        group_objs = aicespana.models.Grupo.objects.all().order_by("nombreGrupo")
        for group_obj in group_objs:
            responsability_options["available_groups"].append(
                [
                    group_obj.get_grupo_id(),
                    group_obj.get_grupo_name(),
                    group_obj.get_diocesis_name(),
                ]
            )
    if aicespana.models.Cargo.objects.all().exists():
        responsible_objs = aicespana.models.Cargo.objects.all().order_by("nombreCargo")
        for responsible_obj in responsible_objs:
            responsability_options["available_responsible"].append(
                [responsible_obj.get_cargo_id(), responsible_obj.get_cargo_name()]
            )
    if aicespana.models.Delegacion.objects.all().exists():
        delegacion_objs = aicespana.models.Delegacion.objects.all().order_by(
            "nombreDelegacion"
        )
        for delegacion_obj in delegacion_objs:
            responsability_options["available_delegacion"].append(
                [
                    delegacion_obj.get_delegacion_id(),
                    delegacion_obj.get_delegacion_name(),
                ]
            )
    if aicespana.models.Diocesis.objects.all().exists():
        diocesis_objs = aicespana.models.Diocesis.objects.all().order_by(
            "nombreDiocesis"
        )
        for diocesis_obj in diocesis_objs:
            responsability_options["available_diocesis"].append(
                [diocesis_obj.get_diocesis_id(), diocesis_obj.get_diocesis_name()]
            )
    return responsability_options


def get_responsablity_data_for_voluntary(personal_obj):
    """
    Description:
        The function gets the available options that a voluntary can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        responsability_optons
    """
    responsability_optons = {}
    responsability_optons["available_groups"] = []
    responsability_optons["available_projects"] = []
    responsability_optons["available_actitvities"] = []
    responsability_optons["available_responsible"] = []
    responsability_optons["available_collaboration"] = []
    if aicespana.models.Grupo.objects.all().exists():
        group_objs = aicespana.models.Grupo.objects.all().order_by("nombreGrupo")
        for group_obj in group_objs:
            responsability_optons["available_groups"].append(
                [
                    group_obj.get_grupo_id(),
                    group_obj.get_grupo_name(),
                    group_obj.get_diocesis_name(),
                ]
            )
    if aicespana.models.Proyecto.objects.all().exists():
        project_objs = aicespana.models.Proyecto.objects.all().order_by(
            "nombreProyecto"
        )
        for project_obj in project_objs:
            responsability_optons["available_projects"].append(
                [project_obj.get_proyecto_id(), project_obj.get_proyecto_name()]
            )
    if aicespana.models.Actividad.objects.all().exists():
        activity_objs = aicespana.models.Actividad.objects.all().order_by(
            "nombreActividad"
        )
        for activity_obj in activity_objs:
            responsability_optons["available_actitvities"].append(
                [activity_obj.get_actividad_id(), activity_obj.get_actividad_name()]
            )
    if aicespana.models.Cargo.objects.all().exists():
        responsible_objs = aicespana.models.Cargo.objects.all().order_by("nombreCargo")
        for responsible_obj in responsible_objs:
            responsability_optons["available_responsible"].append(
                [responsible_obj.get_cargo_id(), responsible_obj.get_cargo_name()]
            )
    if aicespana.models.TipoColaboracion.objects.all().exists():
        collaboration_objs = aicespana.models.TipoColaboracion.objects.all().order_by(
            "tipoColaboracion"
        )
        for collaboration_obj in collaboration_objs:
            responsability_optons["available_collaboration"].append(
                [
                    collaboration_obj.get_tipo_colaboracion_id(),
                    collaboration_obj.get_collaboration_name(),
                ]
            )
    return responsability_optons


def get_defined_data_for_voluntary(personal_obj):
    """
    Description:
        The function gets the available options that a voluntary can have.
    Input:
        personal_obj  # instance of the personel to get data
    Return:
        defined_data
    """
    defined_data = {}
    data = personal_obj.get_voluntario_data()
    fields = [
        "nombre_apellidos",
        "calle",
        "poblacion",
        "provincia",
        "codigo",
        "email",
        "dni",
        "movil",
        "grupo",
    ]
    for index in range(len(fields)):
        defined_data[fields[index]] = data[index]
    defined_data["nombre"] = personal_obj.get_personal_only_name()
    defined_data["apellido"] = personal_obj.get_personal_only_apellido()
    defined_data["user_id"] = personal_obj.get_personal_id()
    return defined_data


def get_responsibles_in_the_group(group_obj):
    """
    Description:
        The function gets the voluntary information from a group.
    Input:
        grupo_obj  # instance of the group
    Return:
        responsible_data
    """
    responsible_data = []
    if aicespana.models.Cargo.objects.filter(
        entidadCargo__entidad__exact="Grupo"
    ).exists():
        cargo_objs = aicespana.models.Cargo.objects.filter(
            entidadCargo__entidad__exact="Grupo"
        ).order_by("nombreCargo")
        for cargo_obj in cargo_objs:
            if (
                aicespana.models.PersonalExterno.objects.filter(
                    cargo=cargo_obj, grupoAsociado=group_obj
                )
                .exclude(personalActivo=False)
                .exists()
            ):
                personal_obj = (
                    aicespana.models.PersonalExterno.objects.filter(
                        cargo=cargo_obj, grupoAsociado=group_obj
                    )
                    .exclude(personalActivo=False)
                    .last()
                )
                responsible_data.append(personal_obj.get_voluntario_data())
            else:
                empty_data = ["-"] * 9
                empty_data[0] = "No esta asignado"
                empty_data.append(cargo_obj.get_cargo_name())
                responsible_data.append(empty_data)

    return responsible_data


def get_voluntarios_info_from_grupo(grupo_id):
    """
    Description:
        The function gets the voluntary information from a group.
    Input:
        grupo_id  # pk of the group
    Functions:
        get_responsibles_in_the_group   # located at this file
    Return:
        voluntarios_data
    """
    voluntarios_data = {}

    if aicespana.models.Grupo.objects.filter(pk__exact=grupo_id).exists():
        group_obj = aicespana.models.Grupo.objects.filter(pk__exact=grupo_id).last()
        voluntarios_data["cargos"] = get_responsibles_in_the_group(group_obj)
        if (
            aicespana.models.PersonalExterno.objects.filter(grupoAsociado=group_obj)
            .exclude(personalActivo=False)
            .exists()
        ):
            voluntarios_data["older_than_80"] = []
            voluntarios_data["younger_than_80"] = []
            personal_objs = (
                aicespana.models.PersonalExterno.objects.filter(grupoAsociado=group_obj)
                .exclude(personalActivo=False)
                .order_by("apellido")
            )
            for personal_obj in personal_objs:
                if personal_obj.get_old() > 80:
                    voluntarios_data["older_than_80"].append(
                        personal_obj.get_personal_name()
                    )
                else:
                    voluntarios_data["younger_than_80"].append(
                        personal_obj.get_personal_name()
                    )
    return voluntarios_data


def get_volunteer_types():
    """
    Description:
        The function gets the possible type of volunteer
    Return:
        volunteer_types
    """
    volunteer_types = []
    if aicespana.models.TipoColaboracion.objects.all().exists():
        colaboracion_objs = aicespana.models.TipoColaboracion.objects.all().order_by(
            "tipoColaboracion"
        )
        for colaboracion_obj in colaboracion_objs:
            volunteer_types.append(
                [
                    colaboracion_obj.get_tipo_colaboracion_id(),
                    colaboracion_obj.get_collaboration_name(),
                ]
            )
    return volunteer_types


def get_user_obj_from_id(user_id):
    """
    Description:
        The function gets the personal instance from the the primary key.
    Input:
        user_id  # pk of the user
    Return:
        the personel instance or false
    """
    if aicespana.models.PersonalExterno.objects.filter(pk__exact=user_id).exists():
        return aicespana.models.PersonalExterno.objects.filter(pk__exact=user_id).last()
    return False


def get_personal_obj_from_id(user_id):
    """
    Description:
        The function gets the personal instance from the the primary key.
    Input:
        user_id  # pk of the user
    Return:
        the personel instance or false
    """
    if aicespana.models.PersonalIglesia.objects.filter(pk__exact=user_id).exists():
        return aicespana.models.PersonalIglesia.objects.filter(pk__exact=user_id).last()
    return False


def is_manager(request):
    """
    Description:
        The function will check if the logged user belongs to administracion  manager group
    Input:
        request # contains the session information
    Return:
        Return True if the user belongs to administracion group, False if not
    """
    try:
        groups = Group.objects.filter(name="administracion").last()
        if groups in request.user.groups.all():
            return True
    except Exception:
        return False

    return False


def get_list_personal_iglesia(delegacion=None):
    """
    Description:
        The function get the personel list ordered by delegation - Diocesis - grupo
    Return:
        Return personal_list
    """
    personal_list = collections.OrderedDict()
    if delegacion is not None:
        personal_objs = aicespana.models.PersonalIglesia.objects.filter(
            delegacion__nombreDelegacion__iexact=delegacion
        ).exclude(personalActivo=False)
    else:
        personal_objs = aicespana.models.PersonalIglesia.objects.all().exclude(
            personalActivo=False
        )

    for personal_obj in personal_objs:
        delegation_name = personal_obj.get_delegacion_belongs_to()
        diocesis_name = personal_obj.get_diocesis_belongs_to()
        if delegation_name not in personal_list:
            personal_list[delegation_name] = collections.OrderedDict()
        if diocesis_name not in personal_list[delegation_name]:
            personal_list[delegation_name][diocesis_name] = []
        personal_list[delegation_name][diocesis_name].append(
            [
                personal_obj.get_personal_id(),
                personal_obj.get_personal_name(),
                personal_obj.get_responability_belongs_to(),
                personal_obj.get_group_belongs_to(),
            ]
        )

    return personal_list


def get_personal_por_cargo(cargo):
    """
    Description:
        The function get the voluntairs which have the cargo name
    Return:
        Return p_cargo
    """
    p_cargo = []
    if not aicespana.models.Cargo.objects.filter(nombreCargo__iexact=cargo).exists():
        return p_cargo
    cargo_obj = aicespana.models.Cargo.objects.filter(nombreCargo__iexact=cargo).last()
    p_externo_objs = cargo_obj.personalexterno_set.all().exclude(personalActivo=False)
    for p_externo_obj in p_externo_objs:
        p_cargo.append(
            [
                "externo",
                p_externo_obj.get_delegacion_belongs_to(),
                p_externo_obj.get_diocesis_belongs_to(),
                p_externo_obj.get_group_belongs_to(),
                p_externo_obj.get_personal_id(),
                p_externo_obj.get_personal_name(),
                cargo,
                p_externo_obj.get_movil_number(),
                p_externo_obj.get_email(),
            ]
        )
    p_iglesia_objs = cargo_obj.personaliglesia_set.all().exclude(personalActivo=False)
    for p_iglesia_obj in p_iglesia_objs:
        p_cargo.append(
            [
                "iglesia",
                p_iglesia_obj.get_delegacion_belongs_to(),
                p_iglesia_obj.get_diocesis_belongs_to(),
                p_iglesia_obj.get_group_belongs_to(),
                p_iglesia_obj.get_personal_id(),
                p_iglesia_obj.get_personal_name(),
                cargo,
                p_iglesia_obj.get_movil_number(),
                p_iglesia_obj.get_email(),
            ]
        )

    return p_cargo


def get_personal_externo_por_delegacion(delegacion_id):
    """
    Description:
        The function get the Personal externo for the requested delegation and create the excel file
    Return:
        Return personal_externo
    """
    personal_externo = []
    f_name = "Listado_por_delegacion.xlsx"
    heading = [
        "Nombre",
        "Apellidos",
        "DNI",
        "email",
        "Telefono fijo",
        "Telefono movil",
        "Fecha nacimiento",
        "Tipo de colaboración",
        "Situación",
        "Fecha Alta",
        "Fecha Baja",
        "Grupo",
        "Parroquia",
        "Diocesis",
        "Delegación",
        "Proyecto",
        "Actividad",
        "Calle",
        "Población",
        "Provincia",
        "Código Postal",
        "Recibir boletin",
    ]
    lista = [heading]
    if aicespana.models.PersonalExterno.objects.filter(
        grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=delegacion_id
    ).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=delegacion_id,
            personalActivo=True,
        ).order_by("apellido")
        for personal_obj in personal_objs:
            lista.append(personal_obj.get_data_for_voluntary_list())
            personal_externo.append(
                [
                    personal_obj.get_personal_only_name(),
                    personal_obj.get_personal_only_apellido(),
                ]
            )

    excel_file = os.path.join(settings.MEDIA_ROOT, f_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(lista):
            worksheet.write_row(row_num, 0, data)
    return personal_externo, os.path.join(settings.MEDIA_URL, f_name)


"""
def presidentas_diocesis():
  
    presidentas_dioc_data = []
    if aicespana.models.PersonalExterno.objects.filter(
        cargo__nombreCargo="Presidenta Diocesana", personalActivo=True
    ).exists():
        presidenta_objs = aicespana.models.PersonalExterno.objects.filter(
            cargo__nombreCargo="Presidenta Diocesana", personalActivo=True
        )
        for presidenta_obj in presidenta_objs:
            data = []
            data.append(presidenta_obj.get_diocesis_belongs_to())
            data.append(presidenta_obj.get_personal_id())
            data.append(presidenta_obj.get_personal_name())
            data.append(presidenta_obj.get_movil_number())
            data.append(presidenta_obj.get_email())
            presidentas_dioc_data.append(data)
    return presidentas_dioc_data
"""

"""
def presidentes_grupo(delegation_id):
    
    Description:
        The function get the presidentes for each group for te given delegation
    Return:
        presidentes_data
    
    presidentes_data = []
    if aicespana.models.PersonalExterno.objects.filter(
        cargo__nombreCargo="Presidenta de Grupo",
        grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=delegation_id,
    ).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            cargo__nombreCargo="Presidenta de Grupo",
            grupoAsociado__diocesisDependiente__delegacionDependiente__pk__exact=delegation_id,
        ).order_by("grupoAsociado__nombreGrupo")
        for personal_obj in personal_objs:
            presidentes_data.append(
                [
                    personal_obj.get_personal_name(),
                    personal_obj.get_movil_number(),
                    personal_obj.get_group_belongs_to(),
                    personal_obj.get_diocesis_belongs_to(),
                    personal_obj.get_delegacion_belongs_to(),
                ]
            )

    return presidentes_data
"""


def bajas_personal_externo_excel():
    """
    Description:
        Get the list of personal externo whom are no longer belongs to AIC
    Return:
        bajas_externo
    """
    import xlsxwriter

    f_name = "Listado_bajas_voluntarios.xlsx"
    heading = ["Nombre y Apellidos", "Grupo", "Población", "Provincia"]
    lista = [heading]
    if aicespana.models.PersonalExterno.objects.filter(personalActivo=False).exists():
        personal_objs = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=False
        )
        for personal_obj in personal_objs:
            lista.append(
                [
                    personal_obj.get_personal_name(),
                    personal_obj.get_group_belongs_to(),
                    personal_obj.get_personal_location(),
                    personal_obj.get_personal_provincia(),
                ]
            )
    excel_file = os.path.join(settings.MEDIA_ROOT, f_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(lista):
            worksheet.write_row(row_num, 0, data)
    baja_file = os.path.join(settings.MEDIA_URL, f_name)

    return baja_file


def store_excel_file(user_data, heading, f_name):
    """ """
    import xlsxwriter

    user_data.insert(0, heading)
    excel_file = os.path.join(settings.MEDIA_ROOT, f_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(user_data):
            worksheet.write_row(row_num, 0, data)
    ex_file = os.path.join(settings.MEDIA_URL, f_name)
    return ex_file


def bajas_personal_iglesia_list():
    """
    Description:
        Get the list of iglesia personal whom are no longer belongs
    Return:
        bajas_iglesia
    """
    bajas_iglesia = []
    if aicespana.models.PersonalIglesia.objects.filter(personalActivo=False).exists():
        personal_objs = aicespana.models.PersonalIglesia.objects.filter(
            personalActivo=False
        )
        for personal_obj in personal_objs:
            bajas_iglesia.append(personal_obj.get_personal_name())
    return bajas_iglesia


def bajas_grupo_list():
    """
    Description:
        Get the list of groups that are no longer active
    Return:
        bajas_grupo
    """
    bajas_grupo = []
    if aicespana.models.Grupo.objects.filter(grupoActivo=False).exists():
        grupo_objs = aicespana.models.Grupo.objects.filter(grupoActivo=False).order_by(
            "nombreGrupo"
        )
        for grupo_obj in grupo_objs:
            bajas_grupo.append(
                [
                    grupo_obj.get_grupo_name(),
                    grupo_obj.get_diocesis_name(),
                    grupo_obj.get_delegacion_name(),
                ]
            )
    return bajas_grupo


def bajas_diocesis_list():
    """
    Description:
        Get the list of diocesis that are no longer active
    Return:
        bajas_diocesis
    """
    bajas_diocesis = []
    if aicespana.models.Diocesis.objects.filter(diocesisActiva=False).exists():
        dio_objs = aicespana.models.Diocesis.objects.filter(
            diocesisActiva=False
        ).order_by("nombreDiocesis")
        for dio_obj in dio_objs:
            bajas_diocesis.append(
                [dio_obj.get_diocesis_name(), dio_obj.get_delegacion_name()]
            )
    return bajas_diocesis


def get_excel_user_request_boletin():
    """
    Description:
        The function get the user and their mail addres to send the boletin
    Return:
        Return the path for collecting the boletin
    """
    import xlsxwriter

    files = {}
    f_mail_name = "Listado_boletin_correo.xlsx"
    f_online_name = "Listado_boletin_online.xlsx"
    heading = [
        "Nombre",
        "Apellidos",
        "Tipo de colaboración",
        "Calle",
        "Población",
        "Provincia",
        "Código Postal",
    ]
    lista = [heading]
    if (
        aicespana.models.PersonalExterno.objects.filter(
            recibirBoletin=True, boletinOnline=False
        )
        .exclude(personalActivo=False)
        .exists()
    ):
        externo_objs = (
            aicespana.models.PersonalExterno.objects.filter(
                recibirBoletin=True, boletinOnline=False
            )
            .exclude(personalActivo=False)
            .order_by("codigoPostal")
        )
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_boletin())

    if (
        aicespana.models.PersonalIglesia.objects.filter(
            recibirBoletin=True, boletinOnline=False
        )
        .exclude(personalActivo=False)
        .exists()
    ):
        externo_objs = (
            aicespana.models.PersonalIglesia.objects.filter(
                recibirBoletin=True, boletinOnline=False
            )
            .exclude(personalActivo=False)
            .order_by("codigoPostal")
        )
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_boletin())
    excel_file = os.path.join(settings.MEDIA_ROOT, f_mail_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(lista):
            worksheet.write_row(row_num, 0, data)
    files["mail"] = os.path.join(settings.MEDIA_URL, f_mail_name)

    heading = ["Nombre", "Apellidos", "Tipo de colaboración", "E-mail"]
    lista = [heading]

    if (
        aicespana.models.PersonalExterno.objects.filter(
            recibirBoletin=True, boletinOnline=True
        )
        .exclude(personalActivo=False)
        .exists()
    ):
        externo_objs = (
            aicespana.models.PersonalExterno.objects.filter(
                recibirBoletin=True, boletinOnline=True
            )
            .exclude(personalActivo=False)
            .order_by("codigoPostal")
        )
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_online_boletin())

    if (
        aicespana.models.PersonalIglesia.objects.filter(
            recibirBoletin=True, boletinOnline=True
        )
        .exclude(personalActivo=False)
        .exists()
    ):
        externo_objs = (
            aicespana.models.PersonalIglesia.objects.filter(
                recibirBoletin=True, boletinOnline=True
            )
            .exclude(personalActivo=False)
            .order_by("codigoPostal")
        )
        for externo_obj in externo_objs:
            lista.append(externo_obj.get_data_for_online_boletin())
    excel_file = os.path.join(settings.MEDIA_ROOT, f_online_name)
    if os.path.isfile(excel_file):
        os.remove(excel_file)
    with xlsxwriter.Workbook(excel_file) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(lista):
            worksheet.write_row(row_num, 0, data)
    files["online"] = os.path.join(settings.MEDIA_URL, f_online_name)

    return files


def store_file(user_file):
    """
    Description:
        The function save the user input file
    Input:
        request # contains the session information
    Return:
        Return True if the user belongs to Wetlab Manager, False if not
    """
    import time

    filename, file_extension = os.path.splitext(user_file.name)
    file_name = filename + "_" + str(time.strftime("%Y%m%d-%H%M%S")) + file_extension
    fs = FileSystemStorage()
    filename = fs.save(file_name, user_file)
    # saved_file = os.path.join(settings.MEDIA_ROOT, file_name)
    return file_name


def voluntarios_per_activity(user_type, region):
    if user_type == "manager":
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True
        )

    elif user_type == "user" and region is not None:
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region,
            personalActivo=True,
        )
    p_ext_objs = p_ext_objs.exclude(actividadAsociada=None).exclude(grupoAsociado=None)
    data = list(
        p_ext_objs.values_list(
            "nombre",
            "apellido",
            "actividadAsociada__nombreActividad",
            "grupoAsociado__nombreGrupo",
            "grupoAsociado__diocesisDependiente__nombreDiocesis",
            "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion",
        )
    )
    return data


def voluntarios_per_project(user_type, region):
    """_summary_

    Parameters
    ----------
    region : _type_
        _description_
    """
    if user_type == "manager":
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            personalActivo=True
        )

    elif user_type == "user" and region is not None:
        p_ext_objs = aicespana.models.PersonalExterno.objects.filter(
            grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion__iexact=region,
            personalActivo=True,
        )
    p_ext_objs = p_ext_objs.exclude(proyectoAsociado=None).exclude(grupoAsociado=None)
    data = list(
        p_ext_objs.values_list(
            "nombre",
            "apellido",
            "proyectoAsociado__nombreProyecto",
            "grupoAsociado__nombreGrupo",
            "grupoAsociado__diocesisDependiente__nombreDiocesis",
            "grupoAsociado__diocesisDependiente__delegacionDependiente__nombreDelegacion",
        )
    )
    return data
