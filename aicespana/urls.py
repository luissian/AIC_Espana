from django.urls import path
from django.conf import settings

from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index, name='index'),
    path('altaActividad', views.alta_actividad, name = 'alta_actividad'),
    path('altaDelegacion',views.alta_delegacion, name ='alta_delegacion'),
    path('altaDiocesis', views.alta_diocesis, name = 'alta_diocesis'),
    path('altaGrupo', views.alta_grupo, name = 'alta_grupo'),
    path('altaParroquia',views.alta_parroquia, name = 'alta_parroquia'),
    path('altaPersonalIglesia', views.alta_personal_iglesia, name = 'alta_personal_iglesia'),
    path('altaProyecto', views.alta_proyecto, name = 'alta_proyecto'),
    path('altaVoluntario', views.alta_voluntario, name='alta_voluntario'),
    path('cargosPersonal', views.cargos_personal, name = 'cargos_personal'),
    path('cargosPersonalID=<int:personal_id>', views.cargos_personal_id, name = 'cargos_personal_id'),
    path('cargoVoluntario=<int:voluntario_id>', views.cargo_voluntario, name= 'cargo_voluntario'),
    path('cargosVoluntarios', views.cargos_voluntarios, name = 'cargos_voluntarios'),
    path('informacionPersonal',views.informacion_personal, name = 'informacion_personal'),
    path('informacionPersonalID=<int:personal_id>',views.informacion_personal_id, name = 'informacion_personal_id'),
    path('informacionVoluntario',views.informacion_voluntario, name = 'informacion_voluntario'),
    path('informacionVoluntarioID=<int:voluntario_id>',views.informacion_voluntario_id, name = 'informacion_voluntario_id'),
    path('listadoBoletin', views.listado_boletin, name = 'listado_boletin'),
    path('listadoDelegacion=<int:delegacion_id>', views.listado_delegacion, name ='listado_delegacion'),
    path('listadoDelegaciones', views.listado_delegaciones, name ='listado_delegaciones'),
    path('listadoDelegadosRegionales', views.listado_delegados_regionales, name = 'listado_delegados_regionales'),
    path('listadoDiocesis=<int:diocesis_id>', views.listado_diocesis, name = 'listado_diocesis'),
    path('listadoGrupo=<int:grupo_id>', views.listado_grupo, name = 'listado_grupo'),
    path('listadoPersonalExterno', views.listado_personal_externo, name = 'listado_personal_externo'),
    path('listadoPersonalIglesia', views.listado_personal_iglesia, name ='listado_personal_iglesia'),
    path('listadoPresidentesGrupo', views.listado_presidentes_grupo, name = 'listado_presidentes_grupo'),
    path('listadoVoluntariosGrupo', views.listado_voluntarios_grupo, name='listado_voluntarios_grupo'),
    path('modificarActividad=<int:actividad_id>',views.modificar_actividad, name = 'modificar_actividad'),
    path('modificacionActividad', views.modificacion_actividad, name = "modificacion_actividad"),
    path('modificarGrupo=<int:grupo_id>',views.modificar_grupo, name = 'modificar_grupo'),
    path('modificacionGrupo', views.modificacion_grupo, name = "modificacion_grupo"),
    path('modificarDelegacion=<int:delegation_id>', views.modificar_delegacion, name = 'modificar_delegacion'),
    path('modificacionDelegacion', views.modificacion_delegacion, name = 'modificacion_delegacion'),
    path('modificarDiocesis=<int:diocesis_id>', views.modificar_diocesis, name = 'modificar_diocesis'),
    path('modificacionDiocesis', views.modificacion_diocesis, name = 'modificacion_diocesis'),
    path('modificarParroquia=<int:parroquia_id>',views.modificar_parroquia, name = 'modificar_parroquia'),
    path('modificacionParroquia', views.modificacion_parroquia, name = "modificacion_parroquia"),
    path('modificacionPersonal', views.modificacion_personal, name = "modificacion_personal"),
    path('modificacionPersonalID=<int:personal_id>', views.modificacion_personal_id, name = "modificacion_personal_id"),
    path('modificarProyecto=<int:proyecto_id>',views.modificar_proyecto, name = 'modificar_proyecto'),
    path('modificacionProyecto', views.modificacion_proyecto, name = "modificacion_proyecto"),
    path('modificacionVoluntario', views.modificacion_voluntario, name = "modificacion_voluntario"),
    path('modificacionVoluntarioId=<int:voluntario_id>', views.modificacion_voluntario_id, name = 'modificacion_voluntario_id'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
