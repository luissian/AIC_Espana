# import statistics
import os

# from django.contrib.auth.models import User
from django.shortcuts import render

# from django.template import loader
from django.contrib.auth.decorators import login_required
from django.conf import settings
import aicespana.models

# from .message_text import *
# from .utils.generic_functions import *
import aicespana.utils.generic_functions
import aicespana.message_text


def index(request):
    return render(request, "aicespana/index.html")


@login_required
def alta_actividad(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    actividades = aicespana.utils.generic_functions.get_summary_actividades("manager")
    if request.method == "POST" and request.POST["action"] == "altaActividad":
        if aicespana.models.Actividad.objects.filter(
            nombreActividad__iexact=request.POST["nombre"]
        ).exists():
            return render(
                request,
                "aicespana/altaActividad.html",
                {
                    "actividades": actividades,
                    "ERROR": [aicespana.message_text.ERROR_ACTIVIDAD_EXIST],
                },
            )
        data = {}
        data["alta"] = request.POST["alta"]
        data["nombre"] = request.POST["nombre"]
        data["observaciones"] = request.POST["observaciones"]
        if "uploadMemoria" in request.FILES:
            data["memoria_file"] = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadMemoria"]
            )
        if "uploadFotografia" in request.FILES:
            data["fotografia_file"] = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadFotografia"]
            )

        aicespana.models.Actividad.objects.create_new_actividad(data)
        return render(
            request,
            "aicespana/altaActividad.html",
            {"confirmation_data": request.POST["nombre"]},
        )

    return render(request, "aicespana/altaActividad.html", {"actividades": actividades})


@login_required
def alta_delegacion(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    delegaciones = aicespana.utils.generic_functions.delegation_name_list()
    if request.method == "POST" and request.POST["action"] == "altaDelegacion":
        if aicespana.models.Delegacion.objects.filter(
            nombreDelegacion__iexact=request.POST["nombre"]
        ).exists():
            error = [
                aicespana.message_text.ERROR_DELEGACION_EXIST,
                request.POST["nombre"],
            ]
            return render(
                request,
                "aicespana/altaDelegacion.html",
                {"delegaciones": delegaciones, "ERROR": error},
            )
        if "uploadImage" in request.FILES:
            image_folder = os.path.join(settings.MEDIA_ROOT, "images")
            os.makedirs(image_folder, exist_ok=True)
            image_file = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadImage"]
            )
            os.replace(
                os.path.join(settings.MEDIA_ROOT, image_file),
                os.path.join(image_folder, image_file),
            )
        else:
            image_file = None
        data = {"nombre": request.POST["nombre"], "imagen": image_file}
        aicespana.models.Delegacion.objects.create_new_delegacion(data)
        return render(
            request,
            "aicespana/altaDelegacion.html",
            {"delegaciones": delegaciones, "confirmation_data": request.POST["nombre"]},
        )
    return render(
        request, "aicespana/altaDelegacion.html", {"delegaciones": delegaciones}
    )


@login_required
def alta_diocesis(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    diocesis_data = {}
    diocesis_data[
        "delegation_data"
    ] = aicespana.utils.generic_functions.delegation_id_and_name_list()
    diocesis_data[
        "diocesis_list"
    ] = aicespana.utils.generic_functions.get_diocesis_name_and_delegation_name()

    if request.method == "POST" and request.POST["action"] == "altaDiocesis":
        if aicespana.models.Diocesis.objects.filter(
            nombreDiocesis__iexact=request.POST["nombre"]
        ).exists():
            error = [
                aicespana.message_text.ERROR_DIOCESIS_EXIST,
                request.POST["nombre"],
            ]
            return render(
                request,
                "aicespana/altaDiocesis.html",
                {"diocesis_data": diocesis_data, "ERROR": error},
            )
        data = {
            "name": request.POST["nombre"],
            "delegation_id": request.POST["delegacion_id"],
        }
        aicespana.models.Diocesis.objects.create_new_diocesis(data)
        return render(
            request,
            "aicespana/altaDiocesis.html",
            {
                "diocesis_data": diocesis_data,
                "confirmation_data": request.POST["nombre"],
            },
        )
    return render(
        request, "aicespana/altaDiocesis.html", {"diocesis_data": diocesis_data}
    )


@login_required
def alta_parroquia(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    parroquia_data = {}
    parroquia_data[
        "parroquia_diocesis_name"
    ] = aicespana.utils.generic_functions.get_id_parroquia_diocesis_delegacion_name()
    parroquia_data[
        "diocesis_id_name_list"
    ] = aicespana.utils.generic_functions.get_diocesis_id_name_list()
    parroquia_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    if request.method == "POST" and request.POST["action"] == "altaParroquia":
        if aicespana.utils.generic_functions.check_exists_parroquia(
            request.POST["nombre"], request.POST["diocesis_id"]
        ):
            return render(
                request,
                "aicespana/altaParroquia.html",
                {
                    "parroquia_data": parroquia_data,
                    "ERROR": aicespana.message_text.ERROR_PARROQUIA_EXISTS,
                },
            )
        diocesis_obj = aicespana.utils.generic_functions.get_diocesis_obj_from_id(
            request.POST["diocesis_id"]
        )
        parroquia_data = {"diocesis_obj": diocesis_obj}
        list_of_data = [
            "nombre",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "observaciones",
        ]
        for item in list_of_data:
            parroquia_data[item] = request.POST[item]
        aicespana.models.Parroquia.objects.create_new_parroquia(parroquia_data)
        return render(
            request,
            "aicespana/altaParroquia.html",
            {"confirmation_data": request.POST["nombre"]},
        )

    return render(
        request, "aicespana/altaParroquia.html", {"parroquia_data": parroquia_data}
    )


@login_required
def alta_grupo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    grupo_data = {}
    grupo_data[
        "diocesis_id_name_list"
    ] = aicespana.utils.generic_functions.get_diocesis_id_name_list()
    grupo_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    grupo_data[
        "grupos_diocesis_id_name"
    ] = aicespana.utils.generic_functions.get_id_grupo_diocesis_delegacion_name()
    if request.method == "POST" and request.POST["action"] == "altaGrupo":
        if aicespana.utils.generic_functions.check_exists_grupo(
            request.POST["nombre"], request.POST["diocesis_id"]
        ):
            return render(
                request,
                "aicespana/altaGrupo.html",
                {
                    "grupo_data": grupo_data,
                    "ERROR": aicespana.message_text.ERROR_GRUPO_EXISTS,
                },
            )
        diocesis_obj = aicespana.utils.generic_functions.get_diocesis_obj_from_id(
            request.POST["diocesis_id"]
        )
        data = {"diocesis_obj": diocesis_obj}
        list_of_data = [
            "nombre",
            "registro",
            "fechaErecion",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "observaciones",
        ]
        for item in list_of_data:
            data[item] = request.POST[item]
        data[
            "provincia"
        ] = aicespana.utils.generic_functions.get_provincia_name_from_index(
            data["provincia"]
        )
        aicespana.models.Grupo.objects.create_new_group(data)
        return render(
            request,
            "aicespana/altaGrupo.html",
            {"confirmation_data": request.POST["nombre"]},
        )

    return render(request, "aicespana/altaGrupo.html", {"grupo_data": grupo_data})


@login_required
def alta_personal_iglesia(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "altaPersonal":
        confirmation_data = ""
        info_to_fetch = [
            "nombre",
            "apellido",
            "nif",
            "email",
            "fijo",
            "movil",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "nacimiento",
            "rec_boletin",
            "grupoID",
        ]
        personal_data = {}

        for field in info_to_fetch:
            personal_data[field] = request.POST[field].strip()
        personal_data[
            "provincia"
        ] = aicespana.utils.generic_functions.get_provincia_name_from_index(
            personal_data["provincia"]
        )
        if aicespana.models.PersonalIglesia.objects.filter(
            nombre__iexact=personal_data["nombre"],
            apellido__iexact=personal_data["apellido"],
        ).exists():
            return render(
                request,
                "aicespana/altaVoluntario.html",
                {
                    "ERROR": [
                        aicespana.message_text.ERROR_PERSONAL_IGLESIA_ALREADY_IN_DATABASE
                    ]
                },
            )
        aicespana.models.PersonalIglesia.objects.create_new_personel(personal_data)

        confirmation_data = {}
        confirmation_data["nombre"] = request.POST["nombre"]
        confirmation_data["apellido"] = request.POST["apellido"]
        return render(
            request,
            "aicespana/altaPersonalIglesia.html",
            {"confirmation_data": confirmation_data},
        )
    personel_data = {"provincias": aicespana.utils.generic_functions.get_provincias()}
    personel_data[
        "grupos_diocesis_id_name"
    ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
    return render(
        request, "aicespana/altaPersonalIglesia.html", {"personel_data": personel_data}
    )


@login_required
def alta_proyecto(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    proyecto_data = {}
    proyecto_data[
        "p_list"
    ] = aicespana.utils.generic_functions.get_projects_information("manager", "")

    # proyecto_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_delegacion_name()
    proyecto_data[
        "grupos_diocesis_id_name"
    ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
    """
    proyecto_data[
        "proyectos_grupos_diocesis_name"
    ] = (
        aicespana.utils.generic_functions.get_id_proyectos_grupos_diocesis_delegacion_name()
    )
    """
    if request.method == "POST" and request.POST["action"] == "altaProyecto":
        if aicespana.models.Proyecto.objects.filter(
            nombreProyecto__iexact=request.POST["nombre"]
        ).exists():
            return render(
                request,
                "aicespana/altaProyecto.html",
                {
                    "proyecto_data": proyecto_data,
                    "ERROR": [aicespana.message_text.ERROR_PROYECTO_EXIST],
                },
            )
        data = {}
        data["grupo_obj"] = (
            aicespana.utils.generic_functions.get_grupo_obj_from_id(
                request.POST["grupoID"]
            )
            if request.POST["grupoID"] != ""
            else None
        )
        data["alta"] = request.POST["alta"]
        data["nombre"] = request.POST["nombre"].strip()
        data["observaciones"] = request.POST["observaciones"]
        if "uploadMemoria" in request.FILES:
            data["memoria_file"] = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadMemoria"]
            )
        if "uploadFotografia" in request.FILES:
            data["fotografia_file"] = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadFotografia"]
            )

        aicespana.models.Proyecto.objects.create_new_proyecto(data)
        return render(
            request,
            "aicespana/altaProyecto.html",
            {"confirmation_data": request.POST["nombre"]},
        )

    return render(
        request, "aicespana/altaProyecto.html", {"proyecto_data": proyecto_data}
    )


@login_required
def alta_voluntario(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "altaVoluntario":
        confirmation_data = ""
        info_to_fetch = [
            "nombre",
            "apellidos",
            "nif",
            "nacimiento",
            "alta",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "email",
            "fijo",
            "movil",
            "tipoColaboracion",
            "grupoID",
            "rec_boletin",
        ]
        personal_data = {}
        for field in info_to_fetch:
            personal_data[field] = request.POST[field].strip()
        personal_data[
            "provincia"
        ] = aicespana.utils.generic_functions.get_provincia_name_from_index(
            personal_data["provincia"]
        )
        if aicespana.models.PersonalExterno.objects.filter(
            nombre__iexact=personal_data["nombre"],
            apellido__iexact=personal_data["apellidos"],
        ).exists():
            return render(
                request,
                "aicespana/altaVoluntario.html",
                {
                    "ERROR": [
                        aicespana.message_text.ERROR_VOLUNTARIO_ALREADY_IN_DATABASE
                    ]
                },
            )
        aicespana.models.PersonalExterno.objects.create_new_external_personel(
            personal_data
        )
        confirmation_data = {}
        confirmation_data["nombre"] = request.POST["nombre"]
        confirmation_data["apellidos"] = request.POST["apellidos"]

        return render(
            request,
            "aicespana/altaVoluntario.html",
            {"confirmation_data": confirmation_data},
        )
    new_volunteer_data = {
        "types": aicespana.utils.generic_functions.get_volunteer_types(),
        "provincias": aicespana.utils.generic_functions.get_provincias(),
    }
    new_volunteer_data[
        "grupos_diocesis_id_name"
    ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
    # new_volunteer_data['grupos_diocesis_id_name'] = get_id_grupo_diocesis_name()
    return render(
        request,
        "aicespana/altaVoluntario.html",
        {"new_volunteer_data": new_volunteer_data},
    )


@login_required
def modificacion_actividad(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )

    actividad_data = aicespana.utils.generic_functions.get_id_actividad_name()
    return render(
        request,
        "aicespana/modificacionActividad.html",
        {"actividad_data": actividad_data},
    )


@login_required
def modificar_actividad(request, actividad_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Actividad.objects.filter(pk__exact=actividad_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_ACTIVIDAD_NOT_EXIST},
        )
    actividad_data = aicespana.utils.generic_functions.get_actividad_data_to_modify(
        actividad_id
    )

    actividad_data[
        "grupos_diocesis_id_name"
    ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()

    if request.method == "POST" and request.POST["action"] == "modificarActividad":
        # if Actividad.objects.filter(nombreActividad__iexact = request.POST['actividad_name'], grupoAsociado__pk__exact = request.POST['grupoID']).exclude(pk__exact =request.POST['actividadID'] ).exists():
        if (
            aicespana.models.Actividad.objects.filter(
                nombreActividad__iexact=request.POST["actividad_name"]
            )
            .exclude(pk__exact=request.POST["actividadID"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarActividad.html",
                {
                    "ERROR": aicespana.message_text.ERROR_ACTIVIDAD_MODIFICATION_EXIST,
                    "actividad_data": actividad_data,
                },
            )
        actividad_obj = aicespana.utils.generic_functions.get_actividad_obj_from_id(
            request.POST["actividadID"]
        )
        actividad_obj.update_actividad_data(
            aicespana.utils.generic_functions.fetch_actividad_data_to_modify(
                request.POST, request.FILES
            )
        )
        return render(
            request,
            "aicespana/modificarActividad.html",
            {"confirmation_data": request.POST["actividad_name"]},
        )
    return render(
        request, "aicespana/modificarActividad.html", {"actividad_data": actividad_data}
    )


@login_required
def modificacion_delegacion(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    delegacion_data = aicespana.utils.generic_functions.delegation_id_and_name_list()
    return render(
        request,
        "aicespana/modificacionDelegacion.html",
        {"delegacion_data": delegacion_data},
    )


@login_required
def modificar_delegacion(request, delegation_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Delegacion.objects.filter(pk__exact=delegation_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_DELEGACION_NOT_EXIST},
        )
    delegacion_obj = aicespana.utils.generic_functions.get_delegation_obj_from_id(
        delegation_id
    )
    delegacion = {}
    delegacion["id"] = delegation_id
    delegacion["name"] = delegacion_obj.get_delegacion_name()
    delegacion["image"] = delegacion_obj.get_delegacion_image()
    if request.method == "POST" and request.POST["action"] == "modificarDelegacion":
        if (
            aicespana.models.Delegacion.objects.filter(
                nombreDelegacion__iexact=request.POST["nombre"]
            )
            .exclude(pk__exact=request.POST["delegacion_id"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarDelegacion.html",
                {
                    "ERROR": aicespana.message_text.ERROR_DELEGACION_MODIFICATION_EXIST,
                    "delegacion": delegacion,
                },
            )
        delegation_obj = aicespana.utils.generic_functions.get_delegation_obj_from_id(
            request.POST["delegacion_id"]
        )
        if "uploadImage" in request.FILES:
            image_folder = os.path.join(settings.MEDIA_ROOT, "images")
            os.makedirs(image_folder, exist_ok=True)
            image_file = aicespana.utils.generic_functions.store_file(
                request.FILES["uploadImage"]
            )
            os.replace(
                os.path.join(settings.MEDIA_ROOT, image_file),
                os.path.join(image_folder, image_file),
            )
        else:
            image_file = None
        delegation_obj.update_delegacion_name_and_image(
            request.POST["nombre"], image_file
        )
        return render(
            request,
            "aicespana/modificarDelegacion.html",
            {"confirmation_data": request.POST["nombre"]},
        )

    return render(
        request, "aicespana/modificarDelegacion.html", {"delegacion": delegacion}
    )


@login_required
def modificacion_diocesis(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    diocesis_data = {}
    # diocesis_data['delegation_data'] = delegation_id_and_name_list()
    diocesis_data[
        "diocesis_list"
    ] = aicespana.utils.generic_functions.get_diocesis_id_name_and_delegation_name()

    return render(
        request, "aicespana/modificacionDiocesis.html", {"diocesis_data": diocesis_data}
    )


@login_required
def modificar_diocesis(request, diocesis_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Diocesis.objects.filter(pk__exact=diocesis_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_DIOCESIS_NOT_EXIST},
        )
    diocesis_obj = aicespana.utils.generic_functions.get_diocesis_obj_from_id(
        diocesis_id
    )
    diocesis_data = {}
    diocesis_data["delegation_id"] = diocesis_obj.get_delegacion_id()
    diocesis_data["delegation_name"] = diocesis_obj.get_delegacion_name()
    diocesis_data["diocesis_id"] = diocesis_obj.get_diocesis_id()
    diocesis_data["diocesis_name"] = diocesis_obj.get_diocesis_name()
    diocesis_data[
        "delegation_id_name_list"
    ] = aicespana.utils.generic_functions.delegation_id_and_name_list()

    diocesis_data["activo"] = diocesis_obj.get_diocesis_status()
    if len(diocesis_obj.get_diocesis_depending_groups()) > 0:
        diocesis_data["allowed_close"] = False
    else:
        diocesis_data["allowed_close"] = True
    if request.method == "POST" and request.POST["action"] == "modificarDiocesis":
        if (
            aicespana.models.Diocesis.objects.filter(
                nombreDiocesis__iexact=request.POST["diocesisNombre"]
            )
            .exclude(pk__exact=request.POST["diocesisID"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarDiocesis.html",
                {
                    "ERROR": aicespana.message_text.ERROR_DIOCESIS_MODIFICATION_EXIST,
                    "diocesis_data": diocesis_data,
                },
            )
        delegation_obj = aicespana.utils.generic_functions.get_delegation_obj_from_id(
            request.POST["delegacion_id"]
        )
        diocesis_obj = aicespana.utils.generic_functions.get_diocesis_obj_from_id(
            request.POST["diocesisID"]
        )
        diocesis_obj.update_diocesis_data(
            request.POST["diocesisNombre"], delegation_obj, request.POST["activo"]
        )
        return render(
            request,
            "aicespana/modificarDiocesis.html",
            {"confirmation_data": request.POST["diocesisNombre"]},
        )

    return render(
        request, "aicespana/modificarDiocesis.html", {"diocesis_data": diocesis_data}
    )


@login_required
def modificacion_grupo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    grupo_data = {
        "grupos_diocesis_name": aicespana.utils.generic_functions.get_id_grupo_diocesis_delegacion_name()
    }
    return render(
        request, "aicespana/modificacionGrupo.html", {"grupo_data": grupo_data}
    )


@login_required
def modificar_grupo(request, grupo_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Grupo.objects.filter(pk__exact=grupo_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_GRUPO_NOT_EXIST},
        )
    grupo_data = aicespana.utils.generic_functions.get_grupo_data_to_modify(grupo_id)
    grupo_data[
        "diocesis_id_name_list"
    ] = aicespana.utils.generic_functions.get_diocesis_id_name_list()
    grupo_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    grupo_data["provincia_index"] = grupo_data["provincias"].index(
        grupo_data["provincia"]
    )

    if request.method == "POST" and request.POST["action"] == "modificarGrupo":
        if (
            aicespana.models.Grupo.objects.filter(
                nombreGrupo__iexact=request.POST["grupo_name"],
                diocesisDependiente__pk__exact=request.POST["diocesisID"],
            )
            .exclude(pk__exact=request.POST["grupoID"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarGrupo.html",
                {
                    "ERROR": aicespana.message_text.ERROR_GRUPO_MODIFICATION_EXIST,
                    "grupo_data": grupo_data,
                },
            )
        grupo_obj = aicespana.utils.generic_functions.get_grupo_obj_from_id(
            request.POST["grupoID"]
        )
        grupo_obj.update_grupo_data(
            aicespana.utils.generic_functions.fetch_grupo_data_to_modify(request.POST)
        )
        return render(
            request,
            "aicespana/modificarGrupo.html",
            {"confirmation_data": request.POST["grupo_name"]},
        )
    return render(request, "aicespana/modificarGrupo.html", {"grupo_data": grupo_data})


@login_required
def modificacion_parroquia(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    parroquia_data = {
        "parroquia_diocesis_name": aicespana.utils.generic_functions.get_id_parroquia_diocesis_delegacion_name()
    }

    return render(
        request,
        "aicespana/modificacionParroquia.html",
        {"parroquia_data": parroquia_data},
    )


@login_required
def modificar_parroquia(request, parroquia_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Parroquia.objects.filter(pk__exact=parroquia_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_DIOCESIS_NOT_EXIST},
        )
    parroquia_data = aicespana.utils.generic_functions.get_parroquia_data_to_modify(
        parroquia_id
    )
    parroquia_data[
        "diocesis_id_name_list"
    ] = aicespana.utils.generic_functions.get_diocesis_id_name_list()
    parroquia_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    if request.method == "POST" and request.POST["action"] == "modificarParroquia":
        if (
            aicespana.models.Parroquia.objects.filter(
                nombreParroquia__iexact=request.POST["parroquia_name"],
                diocesisDependiente__pk__exact=request.POST["diocesisID"],
            )
            .exclude(pk__exact=request.POST["parroquiaID"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarParroquia.html",
                {
                    "ERROR": aicespana.message_text.ERROR_PARROQUIA_MODIFICATION_EXIST,
                    "parroquia_data": parroquia_data,
                },
            )
        parroquia_obj = aicespana.utils.generic_functions.get_parroquia_obj_from_id(
            request.POST["parroquiaID"]
        )
        parroquia_obj.update_parroquia_data(
            aicespana.utils.generic_functions.fetch_parroquia_data_to_modify(
                request.POST
            )
        )
        return render(
            request,
            "aicespana/modificarParroquia.html",
            {"confirmation_data": request.POST["parroquia_name"]},
        )
    return render(
        request, "aicespana/modificarParroquia.html", {"parroquia_data": parroquia_data}
    )


@login_required
def modificacion_personal_id(request, personal_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.PersonalIglesia.objects.filter(
        pk__exact=personal_id
    ).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_PERSONAL_DOES_NOT_EXIST},
        )
    personal_obj = aicespana.utils.generic_functions.get_personal_obj_from_id(
        personal_id
    )
    personal_data = personal_obj.get_all_data_from_personal()
    personal_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    return render(
        request, "aicespana/modificacionPersonal.html", {"personal_data": personal_data}
    )


@login_required
def modificacion_personal(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaPersonal":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/modificacionPersonal.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalIglesia.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalIglesia.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )

                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request, "aicespana/modificacionPersonal.html", {"ERROR": error}
                    )
                personal_data = personal_objs[0].get_all_data_from_personal()
                personal_data[
                    "provincias"
                ] = aicespana.utils.generic_functions.get_provincias()
                personal_data[
                    "grupo_lista"
                ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
                return render(
                    request,
                    "aicespana/modificacionPersonal.html",
                    {"personal_data": personal_data},
                )
            error = [
                "No hay nigún Personal de la Iglesia que tenga el NIF/NIE",
                request.POST["nif"],
            ]
            return render(
                request, "aicespana/modificacionPersonal.html", {"ERROR": error}
            )
        personal_objs = aicespana.models.PersonalIglesia.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"].strip()
            )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"].strip()
            )
        if len(personal_objs) == 0:
            error = [
                "No hay nigún Personal de Iglesia que cumpla los criterios de busqueda:",
                str(request.POST["nombre"] + " " + request.POST["apellido"]),
            ]
            return render(
                request, "aicespana/modificacionPersonal.html", {"ERROR": error}
            )
        if len(personal_objs) > 1:

            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append(
                    [
                        personal_obj.get_personal_id(),
                        personal_obj.get_personal_name(),
                        personal_obj.get_personal_location(),
                    ]
                )

            return render(
                request,
                "aicespana/modificacionPersonal.html",
                {"personal_list": personal_list},
            )
        personal_data = personal_objs[0].get_all_data_from_personal()
        personal_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
        personal_data[
            "provincia_index"
        ] = aicespana.utils.generic_functions.get_provincia_index_from_name(
            personal_data["provincia"]
        )
        personal_data[
            "grupo_lista"
        ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
        return render(
            request,
            "aicespana/modificacionPersonal.html",
            {"personal_data": personal_data},
        )
    if request.method == "POST" and request.POST["action"] == "actualizarCampos":
        user_obj = aicespana.utils.generic_functions.get_personal_obj_from_id(
            request.POST["user_id"]
        )
        data = {}
        field_list = [
            "nombre",
            "apellido",
            "dni",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "email",
            "fijo",
            "movil",
            "baja",
            "rec_boletin",
            "nacimiento",
            "grupoID",
        ]

        for item in field_list:
            data[item] = request.POST[item]
        # Assign values from switch
        if "activo" in request.POST:
            data["activo"] = "true"
        else:
            data["activo"] = "false"
        if "eliminar_grupo" in request.POST:
            data["grupoID"] = ""
        data[
            "provincia"
        ] = aicespana.utils.generic_functions.get_provincia_name_from_index(
            data["provincia"]
        )
        user_obj.update_all_data_for_personal(data)
        return render(
            request,
            "aicespana/modificacionPersonal.html",
            {
                "confirmation_data": request.POST["nombre"]
                + " "
                + request.POST["apellido"]
            },
        )
    return render(request, "aicespana/modificacionPersonal.html")


@login_required
def modificacion_proyecto(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )

    proyecto_data = {}
    proyecto_data[
        "p_list"
    ] = aicespana.utils.generic_functions.get_projects_information("manager", "")
    return render(
        request, "aicespana/modificacionProyecto.html", {"proyecto_data": proyecto_data}
    )


@login_required
def modificar_proyecto(request, proyecto_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Proyecto.objects.filter(pk__exact=proyecto_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_PROYECTO_NOT_EXIST},
        )
    proyecto_data = aicespana.utils.generic_functions.get_proyecto_data_to_modify(
        proyecto_id
    )

    proyecto_data[
        "grupos_diocesis_id_name"
    ] = (
        aicespana.utils.generic_functions.get_group_list_to_select_in_form()
    )  # get_id_grupo_diocesis_name()

    if request.method == "POST" and request.POST["action"] == "modificarProyecto":
        if (
            aicespana.models.Proyecto.objects.filter(
                nombreProyecto__iexact=request.POST["proyecto_name"],
                grupoAsociado__pk__exact=request.POST["grupoID"],
            )
            .exclude(pk__exact=request.POST["proyectoID"])
            .exists()
        ):
            return render(
                request,
                "aicespana/modificarProyecto.html",
                {
                    "ERROR": aicespana.message_text.ERROR_PROYECTO_MODIFICATION_EXIST,
                    "proyecto_data": proyecto_data,
                },
            )
        proyecto_obj = aicespana.utils.generic_functions.get_proyecto_obj_from_id(
            request.POST["proyectoID"]
        )
        proyecto_obj.update_proyecto_data(
            aicespana.utils.generic_functions.fetch_proyecto_data_to_modify(
                request.POST, request.FILES
            )
        )
        return render(
            request,
            "aicespana/modificarProyecto.html",
            {"confirmation_data": request.POST["proyecto_name"]},
        )
    return render(
        request, "aicespana/modificarProyecto.html", {"proyecto_data": proyecto_data}
    )


@login_required
def modificacion_voluntario_id(request, voluntario_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.PersonalExterno.objects.filter(
        pk__exact=voluntario_id
    ).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_VOLUNTARIO_DOES_NOT_EXIST},
        )
    user_obj = aicespana.utils.generic_functions.get_user_obj_from_id(voluntario_id)
    voluntary_data = user_obj.get_all_data_from_voluntario()
    voluntary_data[
        "provincia_index"
    ] = aicespana.utils.generic_functions.get_provincia_index_from_name(
        voluntary_data["provincia"]
    )
    voluntary_data["provincias"] = aicespana.utils.generic_functions.get_provincias()
    voluntary_data[
        "grupo_lista"
    ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
    voluntary_data[
        "tipo_colaboracion"
    ] = aicespana.utils.generic_functions.get_volunteer_types()
    voluntary_data[
        "proyecto_lista"
    ] = aicespana.utils.generic_functions.get_project_group_diocesis()
    voluntary_data["proyecto_data_form"] = user_obj.get_proyecto_data_for_form()
    voluntary_data[
        "actividad_lista"
    ] = aicespana.utils.generic_functions.get_activity_group_diocesis()
    voluntary_data["actividad_data_form"] = user_obj.get_actividad_data_for_form()

    return render(
        request,
        "aicespana/modificacionVoluntario.html",
        {"voluntary_data": voluntary_data},
    )


@login_required
def modificacion_voluntario(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaVoluntario":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/modificacionVoluntario.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalExterno.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalExterno.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )
                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request,
                        "aicespana/modificacionVoluntario.html",
                        {"ERROR": error},
                    )
                voluntary_data = (
                    aicespana.utils.generic_functions.get_defined_data_for_voluntary(
                        personal_objs[0]
                    )
                )
                voluntary_data.update(
                    aicespana.utils.generic_functions.get_external_personal_responsability(
                        personal_objs[0]
                    )
                )
                voluntary_data["user_id"] = personal_objs[0].get_personal_id()
                return render(
                    request,
                    "aicespana/modificacionVoluntario.html",
                    {"voluntary_data": voluntary_data},
                )
            error = [
                "No hay ningún voluntario que tenga el NIF/NIE",
                request.POST["nif"],
            ]
            return render(
                request, "aicespana/modificacionVoluntario.html", {"ERROR": error}
            )
        personal_objs = aicespana.models.PersonalExterno.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"].strip()
            )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"].strip()
            )
        if len(personal_objs) == 0:
            error = [
                "No hay nigún voluntario que cumpla los criterios de busqueda",
                str(request.POST["nombre"] + " " + request.POST["apellido"]),
            ]
            return render(
                request, "aicespana/modificacionVoluntario.html", {"ERROR": error}
            )
        if len(personal_objs) > 1:
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append(
                    [
                        personal_obj.get_personal_id(),
                        personal_obj.get_personal_name(),
                        personal_obj.get_personal_location(),
                    ]
                )
            return render(
                request,
                "aicespana/modificacionVoluntario.html",
                {"personal_list": personal_list},
            )
        voluntary_data = personal_objs[0].get_all_data_from_voluntario()
        voluntary_data[
            "provincia_index"
        ] = aicespana.utils.generic_functions.get_provincia_index_from_name(
            voluntary_data["provincia"]
        )
        voluntary_data[
            "provincias"
        ] = aicespana.utils.generic_functions.get_provincias()
        voluntary_data[
            "grupo_lista"
        ] = aicespana.utils.generic_functions.get_group_list_to_select_in_form()
        voluntary_data[
            "tipo_colaboracion"
        ] = aicespana.utils.generic_functions.get_volunteer_types()
        voluntary_data[
            "proyecto_lista"
        ] = aicespana.utils.generic_functions.get_project_group_diocesis()
        voluntary_data["proyecto_data_form"] = personal_objs[
            0
        ].get_proyecto_data_for_form()
        voluntary_data[
            "actividad_lista"
        ] = aicespana.utils.generic_functions.get_activity_group_diocesis()
        voluntary_data["actividad_data_form"] = personal_objs[
            0
        ].get_actividad_data_for_form()

        return render(
            request,
            "aicespana/modificacionVoluntario.html",
            {"voluntary_data": voluntary_data},
        )
    if request.method == "POST" and request.POST["action"] == "actualizarCampos":
        user_obj = aicespana.utils.generic_functions.get_user_obj_from_id(
            request.POST["user_id"]
        )
        data = {}
        field_list = [
            "nombre",
            "apellidos",
            "dni",
            "nacimiento",
            "calle",
            "poblacion",
            "provincia",
            "codigo",
            "email",
            "fijo",
            "movil",
            "alta",
            "baja",
            "colaboracion_id",
            "grupoID",
            "rec_boletin",
            "actividadID",
            "proyectoID",
        ]

        for item in field_list:
            data[item] = request.POST[item]
        # update switch values
        if "activo" in request.POST:
            data["activo"] = "true"
        else:
            data["activo"] = "false"

        if "eliminar_grupo" in request.POST:
            data["grupoID"] = ""
        if "eliminar_proyecto" in request.POST:
            data["proyectoID"] = ""
        if "eliminar_actividad":
            data["activiadID"] = ""
        data[
            "provincia"
        ] = aicespana.utils.generic_functions.get_provincia_name_from_index(
            data["provincia"]
        )
        user_obj.update_all_data_for_voluntary(data)

        return render(
            request,
            "aicespana/modificacionVoluntario.html",
            {
                "confirmation_data": request.POST["nombre"]
                + " "
                + request.POST["apellidos"]
            },
        )
    return render(request, "aicespana/modificacionVoluntario.html")


@login_required
def cargos_personal_id(request, personal_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    user_obj = aicespana.utils.generic_functions.get_personal_obj_from_id(personal_id)
    personal_available_settings = (
        aicespana.utils.generic_functions.get_responsablity_data_for_personel(user_obj)
    )
    personal_available_settings.update(
        aicespana.utils.generic_functions.get_personal_responsability(user_obj)
    )

    personal_available_settings["user_id"] = personal_id
    return render(
        request,
        "aicespana/cargosPersonal.html",
        {"personal_available_settings": personal_available_settings},
    )


@login_required
def cargos_personal(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaPersonal":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/cargosPersonal.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalIglesia.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalIglesia.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )
                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request, "aicespana/cargosPersonal.html", {"ERROR": error}
                    )
                personal_available_settings = aicespana.utils.generic_functions.get_responsablity_data_for_personel(
                    personal_objs[0]
                )
                return render(
                    request,
                    "aicespana/cargosPersonal.html",
                    {"personal_available_settings": personal_available_settings},
                )
            error = [
                aicespana.message_text.ERROR_NOT_FIND_PERSONAL_NIF,
                request.POST["nif"],
            ]
            return render(request, "aicespana/cargosPersonal.html", {"ERROR": error})
        personal_objs = aicespana.models.PersonalIglesia.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"].strip()
            )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"].strip()
            )

        if len(personal_objs) == 0:
            error = [
                aicespana.message_text.ERROR_NOT_FIND_PERSONAl_CRITERIA,
                str(request.POST["nombre"] + " " + request.POST["apellido"]),
            ]
            return render(request, "aicespana/cargosPersonal.html", {"ERROR": error})
        if len(personal_objs) > 1:
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append(
                    [
                        personal_obj.get_personal_id(),
                        personal_obj.get_personal_name(),
                        personal_obj.get_personal_location(),
                    ]
                )
            return render(
                request,
                "aicespana/cargosPersonal.html",
                {"personal_list": personal_list},
            )
        personal_available_settings = (
            aicespana.utils.generic_functions.get_responsablity_data_for_personel(
                personal_objs[0]
            )
        )
        personal_available_settings.update(
            aicespana.utils.generic_functions.get_personal_responsability(
                personal_objs[0]
            )
        )

        personal_available_settings["user_id"] = personal_objs[0].get_personal_id()
        return render(
            request,
            "aicespana/cargosPersonal.html",
            {"personal_available_settings": personal_available_settings},
        )

    if request.method == "POST" and request.POST["action"] == "asignarCargos":
        user_obj = aicespana.utils.generic_functions.get_personal_obj_from_id(
            request.POST["user_id"]
        )

        data = {}
        # remove cargo or grupo if switch was set to delete it
        if "eliminar_grupo" in request.POST:
            data["grupo"] = ""
        else:
            data["grupo"] = request.POST["grupo"]
        # cargo
        if "eliminar_cargo" in request.POST:
            data["cargo"] = ""
        else:
            data["cargo"] = request.POST.getlist("cargo")

        data["delegacion"] = request.POST["delegacion"]

        user_obj.update_information(data)
        updated_data = aicespana.utils.generic_functions.get_personal_responsability(
            user_obj
        )
        return render(
            request, "aicespana/cargosPersonal.html", {"updated_data": updated_data}
        )
    return render(request, "aicespana/cargosPersonal.html")


@login_required
def cargo_voluntario(request, voluntario_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    user_obj = aicespana.utils.generic_functions.get_user_obj_from_id(voluntario_id)
    personal_available_settings = (
        aicespana.utils.generic_functions.get_responsablity_data_for_voluntary(user_obj)
    )
    personal_available_settings.update(
        aicespana.utils.generic_functions.get_external_personal_responsability(user_obj)
    )
    personal_available_settings["user_id"] = voluntario_id
    return render(
        request,
        "aicespana/cargosVoluntarios.html",
        {"personal_available_settings": personal_available_settings},
    )


@login_required
def cargos_voluntarios(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaVoluntario":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/cargosVoluntarios.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalExterno.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalExterno.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )
                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request, "aicespana/cargosVoluntarios.html", {"ERROR": error}
                    )
                personal_available_settings = aicespana.utils.generic_functions.get_responsablity_data_for_voluntary(
                    personal_objs[0]
                )
                personal_available_settings.update(
                    aicespana.utils.generic_functions.get_external_personal_responsability(
                        personal_objs[0]
                    )
                )
                return render(
                    request,
                    "aicespana/cargosVoluntarios.html",
                    {"personal_available_settings": personal_available_settings},
                )
            error = [
                "No hay nigún voluntario que tenga el NIF/NIE",
                request.POST["nif"],
            ]
            return render(request, "aicespana/cargosVoluntarios.html", {"ERROR": error})
        personal_objs = aicespana.models.PersonalExterno.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"].strip()
            )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"].strip()
            )
        if len(personal_objs) == 0:
            error = [
                "No hay nigún voluntario que cumpla los criterios de busqueda",
                str(request.POST["nombre"] + " " + request.POST["apellido"]),
            ]
            return render(request, "aicespana/cargosVoluntarios.html", {"ERROR": error})
        if len(personal_objs) > 1:
            personal_list = []
            for personal_obj in personal_objs:
                personal_list.append(
                    [
                        personal_obj.get_personal_id(),
                        personal_obj.get_personal_name(),
                        personal_obj.get_personal_location(),
                    ]
                )
            return render(
                request,
                "aicespana/cargosVoluntarios.html",
                {"personal_list": personal_list},
            )
        personal_available_settings = (
            aicespana.utils.generic_functions.get_responsablity_data_for_voluntary(
                personal_objs[0]
            )
        )
        personal_available_settings.update(
            aicespana.utils.generic_functions.get_external_personal_responsability(
                personal_objs[0]
            )
        )
        personal_available_settings["user_id"] = personal_objs[0].get_personal_id()
        return render(
            request,
            "aicespana/cargosVoluntarios.html",
            {"personal_available_settings": personal_available_settings},
        )
    if request.method == "POST" and request.POST["action"] == "asignarCargos":
        user_obj = aicespana.utils.generic_functions.get_user_obj_from_id(
            request.POST["user_id"]
        )
        data = {}
        # cargo
        if "eliminar_cargo" in request.POST:
            data["cargo"] = ""
        else:
            data["cargo"] = request.POST.getlist("cargo")
        # actividad
        if "eliminar_actividad" in request.POST:
            data["actividad"] = ""
        else:
            data["actividad"] = request.POST["actividad"]
        # grupo
        if "eliminar_grupo" in request.POST:
            data["grupo"] = ""
        else:
            data["grupo"] = request.POST["grupo"]
        # proyecto
        if "eliminar_proyecto" in request.POST:
            data["proyecto"] = ""
        else:
            data["proyecto"] = request.POST["proyecto"]
        data["colaboracion"] = request.POST["colaboracion"]

        user_obj.update_information(data)
        updated_data = "Cargos actualizados"

        return render(
            request, "aicespana/cargosVoluntarios.html", {"updated_data": updated_data}
        )
    return render(request, "aicespana/cargosVoluntarios.html")


@login_required
def informacion_personal_id(request, personal_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.PersonalIglesia.objects.filter(
        pk__exact=personal_id
    ).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_PERSONAL_DOES_NOT_EXIST},
        )
    personal_obj = aicespana.utils.generic_functions.get_personal_obj_from_id(
        personal_id
    )
    info_personal = personal_obj.get_all_data_from_personal()
    info_personal["cargos"] = personal_obj.get_responability_belongs_to()
    return render(
        request, "aicespana/informacionPersonal.html", {"info_personal": info_personal}
    )


@login_required
def informacion_personal(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaPersonal":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/informacionPersonal.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalIglesia.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalIglesia.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )
                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request, "aicespana/informacionPersonal.html", {"ERROR": error}
                    )
                info_voluntario = personal_objs[0].get_all_data_from_personal()
                info_voluntario["cargos"] = personal_objs[
                    0
                ].get_responability_belongs_to()
                return render(
                    request,
                    "aicespana/informacionPersonal.html",
                    {"info_voluntario": info_voluntario},
                )
            error = [
                "No hay nigún Personal de la Iglesia que tenga el NIF/NIE",
                request.POST["nif"],
            ]
            return render(
                request, "aicespana/informacionPersonal.html", {"ERROR": error}
            )
        personal_objs = aicespana.models.PersonalIglesia.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"]
            )
            if len(personal_objs) == 0:
                error = [
                    "No hay nigún Personal de Iglesia que tenga el apellido",
                    request.POST["apellido"],
                ]
                return render(
                    request, "aicespana/informacionPersonal.html", {"ERROR": error}
                )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"]
            )
            if len(personal_objs) == 0:
                error = [
                    "No hay nigún Personal de Iglesia con el nombre",
                    request.POST["nombre"],
                ]
                return render(
                    request, "aicespana/informacionPersonal.html", {"ERROR": error}
                )
        if len(personal_objs) > 1:
            lista_personal = (
                aicespana.utils.generic_functions.get_info_of_voluntarios_personel(
                    personal_objs
                )
            )
            return render(
                request,
                "aicespana/informacionPersonal.html",
                {"lista_personal": lista_personal},
            )
        info_personal = personal_objs[0].get_all_data_from_personal()
        info_personal["cargos"] = personal_objs[0].get_responability_belongs_to()
        return render(
            request,
            "aicespana/informacionPersonal.html",
            {"info_personal": info_personal},
        )
    return render(request, "aicespana/informacionPersonal.html")


@login_required
def informacion_voluntario_id(request, voluntario_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.PersonalExterno.objects.filter(
        pk__exact=voluntario_id
    ).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_VOLUNTARIO_DOES_NOT_EXIST},
        )
    user_obj = aicespana.utils.generic_functions.get_user_obj_from_id(voluntario_id)
    info_voluntario = user_obj.get_all_data_from_voluntario()
    info_voluntario["cargos"] = user_obj.get_responability_belongs_to()
    return render(
        request,
        "aicespana/informacionVoluntario.html",
        {"info_voluntario": info_voluntario},
    )


@login_required
def informacion_voluntario(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if request.method == "POST" and request.POST["action"] == "busquedaVoluntario":
        if (
            request.POST["nif"] == ""
            and request.POST["nombre"] == ""
            and request.POST["apellido"] == ""
        ):
            return render(request, "aicespana/informacionVoluntario.html")
        if request.POST["nif"] != "":
            if aicespana.models.PersonalExterno.objects.filter(
                DNI__iexact=request.POST["nif"]
            ).exists():
                personal_objs = aicespana.models.PersonalExterno.objects.filter(
                    DNI__iexact=request.POST["nif"]
                )
                if len(personal_objs) > 1:
                    error = [
                        "Hay más de 1 persona que tiene el mismo NIF/NIE",
                        request.POST["nif"],
                    ]
                    return render(
                        request,
                        "aicespana/informacionVoluntario.html",
                        {"ERROR": error},
                    )
                info_voluntario = personal_objs[0].get_all_data_from_voluntario()
                info_voluntario["cargos"] = personal_objs[
                    0
                ].get_responability_belongs_to()
                return render(
                    request,
                    "aicespana/informacionVoluntario.html",
                    {"info_voluntario": info_voluntario},
                )
            error = [
                "No hay nigún voluntario que tenga el NIF/NIE",
                request.POST["nif"],
            ]
            return render(
                request, "aicespana/informacionVoluntario.html", {"ERROR": error}
            )
        personal_objs = aicespana.models.PersonalExterno.objects.all()
        if request.POST["apellido"] != "":
            personal_objs = personal_objs.filter(
                apellido__icontains=request.POST["apellido"].strip()
            )
            if len(personal_objs) == 0:
                error = [
                    "No hay nigún voluntario con el apellido",
                    request.POST["apellido"],
                ]
                return render(
                    request, "aicespana/informacionVoluntario.html", {"ERROR": error}
                )
        if request.POST["nombre"] != "":
            personal_objs = personal_objs.filter(
                nombre__icontains=request.POST["nombre"].strip()
            )
            if len(personal_objs) == 0:
                error = [
                    "No hay nigún voluntario con el nombre",
                    request.POST["nombre"],
                ]
                return render(
                    request, "aicespana/informacionVoluntario.html", {"ERROR": error}
                )
        if len(personal_objs) > 1:
            lista_voluntarios = (
                aicespana.utils.generic_functions.get_info_of_voluntarios_personel(
                    personal_objs
                )
            )
            return render(
                request,
                "aicespana/informacionVoluntario.html",
                {"lista_voluntarios": lista_voluntarios},
            )
        info_voluntario = personal_objs[0].get_all_data_from_voluntario()
        info_voluntario["cargos"] = personal_objs[0].get_responability_belongs_to()
        # info_voluntario = [personal_objs[0].get_voluntario_data()]
        return render(
            request,
            "aicespana/informacionVoluntario.html",
            {"info_voluntario": info_voluntario},
        )
    return render(request, "aicespana/informacionVoluntario.html")


@login_required
def listado_boletin(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    listado = aicespana.utils.generic_functions.get_excel_user_request_boletin()
    return render(request, "aicespana/listadoBoletin.html", {"listado": listado})


@login_required
def listado_delegaciones(request):
    delegaciones = []
    if aicespana.models.Delegacion.objects.all().exists():
        delegacion_objs = aicespana.models.Delegacion.objects.all().order_by(
            "nombreDelegacion"
        )
        for delegacion_obj in delegacion_objs:
            delegaciones.append(
                [
                    delegacion_obj.get_delegacion_id(),
                    delegacion_obj.get_delegacion_name(),
                ]
            )
    if request.method == "POST" and request.POST["action"] == "informacionDelegacion":
        delegacion_data = aicespana.utils.generic_functions.get_delegation_data(
            request.POST["delegacion"]
        )
        return render(
            request,
            "aicespana/listadoDelegaciones.html",
            {"delegacion_data": delegacion_data},
        )

    return render(
        request, "aicespana/listadoDelegaciones.html", {"delegaciones": delegaciones}
    )


@login_required
def listado_delegacion(request, delegacion_id):
    # if not allow_all_lists(request):
    #    if not allow_own_delegation(request):
    #        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not aicespana.models.Delegacion.objects.filter(pk__exact=delegacion_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_DELEGACION_NOT_EXIST},
        )
    delegacion_obj = aicespana.utils.generic_functions.get_delegation_obj_from_id(
        delegacion_id
    )
    # Get the diocesis bolongs to the delegation
    delegacion_data = {}
    delegacion_data[
        "diocesis_list"
    ] = aicespana.utils.generic_functions.get_diocesis_in_delegation(delegacion_obj)
    delegacion_data["summary"] = [
        aicespana.utils.generic_functions.get_summary_of_delegation(delegacion_obj)
    ]
    import pdb

    pdb.set_trace()
    delegacion_data["delegacion_name"] = delegacion_obj.get_delegacion_name()
    delegacion_data["delegacion_image"] = delegacion_obj.get_delegacion_image()
    delegacion_data[
        "cargos"
    ] = aicespana.utils.generic_functions.get_cargos_per_location(
        "Delegación", "delegation", delegacion_id
    )

    return render(
        request,
        "aicespana/listadoDelegacion.html",
        {"delegacion_data": delegacion_data},
    )


def listado_diocesis(request, diocesis_id):
    # if not allow_all_lists(request):
    #    if not allow_own_delegation(request):
    #        return render (request,'aicespana/errorPage.html', {'content': ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS})
    if not aicespana.models.Diocesis.objects.filter(pk__exact=diocesis_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_DIOCESIS_NOT_EXIST},
        )
    diocesis_obj = aicespana.utils.generic_functions.get_diocesis_obj_from_id(
        diocesis_id
    )
    diocesis_data = {}
    diocesis_data["grupos"] = aicespana.utils.generic_functions.get_groups_in_diocesis(
        diocesis_obj, True
    )
    diocesis_data["cargos"] = aicespana.utils.generic_functions.get_cargos_per_location(
        "Diocesis", "diocesis", diocesis_id
    )
    diocesis_data["summary"] = [
        aicespana.utils.generic_functions.get_summary_of_diocesis(diocesis_obj)
    ]
    diocesis_data["diocesis_name"] = diocesis_obj.get_diocesis_name()

    return render(
        request, "aicespana/listadoDiocesis.html", {"diocesis_data": diocesis_data}
    )


def listado_grupo(request, grupo_id):
    if not aicespana.models.Grupo.objects.filter(pk__exact=grupo_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_GRUPO_NOT_EXIST},
        )
    grupo_obj = aicespana.utils.generic_functions.get_grupo_obj_from_id(grupo_id)
    if not aicespana.utils.generic_functions.allow_see_group_information_voluntary(
        request, grupo_obj
    ):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_ALLOW_TO_SEE_LISTADOS},
        )
    grupo_data = {}
    grupo_data["nombre_grupo"] = grupo_obj.get_grupo_name()
    grupo_data["cargos"] = aicespana.utils.generic_functions.get_cargos_per_location(
        "Grupo", "grupo", grupo_id
    )
    grupo_data["informacion"] = grupo_obj.get_grupo_full_data()
    grupo_data["summary"] = [
        aicespana.utils.generic_functions.get_summary_of_group(grupo_obj)
    ]
    grupo_data[
        "lista_voluntarios"
    ] = aicespana.utils.generic_functions.get_grupo_voluntarios(grupo_obj)
    grupo_data[
        "lista_colaboradores"
    ] = aicespana.utils.generic_functions.get_grupo_colaboradores(grupo_obj)
    grupo_data["lista_asesores"] = aicespana.utils.generic_functions.get_grupo_asesores(
        grupo_obj
    )
    grupo_data["lista_otros"] = aicespana.utils.generic_functions.get_grupo_otros(
        grupo_obj
    )

    return render(request, "aicespana/listadoGrupo.html", {"grupo_data": grupo_data})


@login_required
def listado_proyectos(request):
    region = None
    user_type = "user"
    project_data = {}
    if not aicespana.utils.generic_functions.is_manager(request):
        # check if loggin user is a delegation name
        delegacion_name = (
            aicespana.utils.generic_functions.delegacion_name_from_loged_user(
                request.user.username
            )
        )
        if delegacion_name is None:
            return render(
                request,
                "aicespana/errorPage.html",
                {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
            )
        region = delegacion_name
    else:
        user_type = "manager"
    project_data["p_list"] = aicespana.utils.generic_functions.get_projects_information(
        user_type, region
    )
    project_data["graphics"] = aicespana.utils.generic_functions.graphics_per_proyect(
        region
    )
    return render(
        request, "aicespana/listadoProyectos.html", {"project_data": project_data}
    )


@login_required
def listado_voluntarios_grupo(request):
    grupos = []
    if aicespana.models.Grupo.objects.all().exists():
        grupo_objs = aicespana.models.Grupo.objects.all().order_by("nombreGrupo")
        for grupo_obj in grupo_objs:
            grupos.append(
                [
                    grupo_obj.get_grupo_id(),
                    grupo_obj.get_grupo_name(),
                    grupo_obj.get_diocesis_name(),
                ]
            )
    if request.method == "POST" and request.POST["action"] == "nombreGrupo":
        voluntarios_data = (
            aicespana.utils.generic_functions.get_voluntarios_info_from_grupo(
                request.POST["grupo_id"]
            )
        )

        return render(
            request,
            "aicespana/listadoVoluntariosGrupo.html",
            {"voluntarios_data": voluntarios_data},
        )

    return render(request, "aicespana/listadoVoluntariosGrupo.html", {"grupos": grupos})


@login_required
def listado_personal_iglesia(request):
    delegacion_name = None
    if not aicespana.utils.generic_functions.is_manager(request):
        # check if loggin user is a delegation name
        delegacion_name = (
            aicespana.utils.generic_functions.delegacion_name_from_loged_user(
                request.user.username
            )
        )
        if delegacion_name is None:
            return render(
                request,
                "aicespana/errorPage.html",
                {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
            )

    listado_personal = aicespana.utils.generic_functions.get_list_personal_iglesia(
        delegacion_name
    )
    return render(
        request,
        "aicespana/listadoPersonalIglesia.html",
        {"listado_personal": listado_personal},
    )


@login_required
def listado_delegados_regionales(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    listado_delegados = aicespana.utils.generic_functions.get_personal_por_cargo(
        "Delegada regional"
    )
    return render(
        request,
        "aicespana/listadoDelegadosRegionales.html",
        {"listado_delegados": listado_delegados},
    )


@login_required
def listado_presidentas_diocesis(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    presidentas = aicespana.utils.generic_functions.get_personal_por_cargo(
        "Presidenta Diocesana"
    )
    return render(
        request,
        "aicespana/listadoPresidentasDiocesis.html",
        {"presidentas": presidentas},
    )


@login_required
def listado_presidentes_grupo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    presidentes = aicespana.utils.generic_functions.get_personal_por_cargo(
        "Presidenta de Grupo"
    )
    return render(
        request,
        "aicespana/listadoPresidentesGrupo.html",
        {"presidentes": presidentes},
    )
    """
    if request.method == "POST" and request.POST["action"] == "listadoPresidentesGrupo":
        presidentes = aicespana.utils.generic_functions.presidentes_grupo(
            request.POST["delegacion_id"]
        )
        if not presidentes:
            error_message = aicespana.message_text.ERROR_NO_PRESIDENTS_IN_DELEGATION
            delegation_data = (
                aicespana.utils.generic_functions.delegation_id_and_name_list()
            )
            return render(
                request,
                "aicespana/listadoPresidentesGrupo.html",
                {"delegation_data": delegation_data, "ERROR": error_message},
            )
    """


@login_required
def listado_personal_externo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        # check if loggin user is a delegation name
        delegacion_name = (
            aicespana.utils.generic_functions.delegacion_name_from_loged_user(
                request.user.username
            )
        )
        if delegacion_name is None:
            return render(
                request,
                "aicespana/errorPage.html",
                {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
            )
        delegacion_id = aicespana.utils.generic_functions.get_delegacion_id_from_name(
            delegacion_name
        )
        if delegacion_id is not None:
            (
                listado_personal,
                excel_file,
            ) = aicespana.utils.generic_functions.get_personal_externo_por_delegacion(
                delegacion_id
            )
            return render(
                request,
                "aicespana/listadoPersonalExterno.html",
                {
                    "listado_personal": listado_personal,
                    "excel_file": excel_file,
                    "delegacion": delegacion_name,
                },
            )
        else:
            return render(
                request,
                "aicespana/errorPage.html",
                {"content": aicespana.message_text.ERROR_DELEGACION_NOT_EXIST},
            )
    if request.method == "POST" and request.POST["action"] == "listadoDelegacion":
        (
            listado_personal,
            excel_file,
        ) = aicespana.utils.generic_functions.get_personal_externo_por_delegacion(
            request.POST["delegacion_id"]
        )
        delegacion = aicespana.utils.generic_functions.get_delegation_obj_from_id(
            request.POST["delegacion_id"]
        ).get_delegacion_name()
        return render(
            request,
            "aicespana/listadoPersonalExterno.html",
            {
                "listado_personal": listado_personal,
                "excel_file": excel_file,
                "delegacion": delegacion,
            },
        )
    delegation_data = aicespana.utils.generic_functions.delegation_id_and_name_list()
    return render(
        request,
        "aicespana/listadoPersonalExterno.html",
        {"delegation_data": delegation_data},
    )


@login_required
def listado_actividades(request):
    region = None
    user_type = "user"
    activity_data = {}
    if not aicespana.utils.generic_functions.is_manager(request):
        # check if loggin user is a delegation name
        delegacion_name = (
            aicespana.utils.generic_functions.delegacion_name_from_loged_user(
                request.user.username
            )
        )
        if delegacion_name is None:
            return render(
                request,
                "aicespana/errorPage.html",
                {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
            )
        region = delegacion_name
    else:
        user_type = "manager"
    activity_data[
        "act_list"
    ] = aicespana.utils.generic_functions.get_summary_actividades(user_type, region)
    activity_data["graphics"] = aicespana.utils.generic_functions.graphics_per_activity(
        region
    )
    activity_data["user_type"] = user_type
    return render(
        request, "aicespana/listadoActividades.html", {"activity_data": activity_data}
    )


@login_required
def listado_actividad(request, actividad_id):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    if not aicespana.models.Actividad.objects.filter(pk__exact=actividad_id).exists():
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_ACTIVIDAD_NOT_EXIST},
        )

    # Get the delgacion which have the avtivity
    actividad_data = aicespana.utils.generic_functions.get_activity_data_in_delegations(
        actividad_id
    )
    if len(actividad_data["user_list"]) > 0:
        actividad_data[
            "excel_file"
        ] = aicespana.utils.generic_functions.store_excel_file(
            actividad_data["user_list"],
            actividad_data["heading"],
            "listado_voluntarios_actividad.xlsx",
        )
    else:
        actividad_data["excel_file"] = False
    return render(
        request, "aicespana/listadoActividad.html", {"actividad_data": actividad_data}
    )


@login_required
def listado_bajas_externo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    bajas_externo = aicespana.utils.generic_functions.bajas_personal_externo_excel()
    return render(
        request, "aicespana/listadoBajasExterno.html", {"bajas_externo": bajas_externo}
    )


@login_required
def listado_bajas_iglesia(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    bajas_iglesia = aicespana.utils.generic_functions.bajas_personal_iglesia_list()
    return render(
        request, "aicespana/listadoBajasIglesia.html", {"bajas_iglesia": bajas_iglesia}
    )


@login_required
def listado_bajas_grupo(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    bajas_grupo = aicespana.utils.generic_functions.bajas_grupo_list()
    return render(
        request, "aicespana/listadoBajasGrupo.html", {"bajas_grupo": bajas_grupo}
    )


@login_required
def listado_bajas_diocesis(request):
    if not aicespana.utils.generic_functions.is_manager(request):
        return render(
            request,
            "aicespana/errorPage.html",
            {"content": aicespana.message_text.ERROR_USER_NOT_MANAGER},
        )
    bajas_diocesis = aicespana.utils.generic_functions.bajas_diocesis_list()
    return render(
        request,
        "aicespana/listadoBajasDiocesis.html",
        {"bajas_diocesis": bajas_diocesis},
    )
