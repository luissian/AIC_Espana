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
    path('cargosPersonalIglesia', views.cargos_personal_iglesia, name = 'cargos_personal_iglesia'),
    path('cargosVoluntarios', views.cargos_voluntarios, name = 'cargos_voluntarios'),
    path('informacionVoluntario',views.informacion_voluntario, name = 'informacion_voluntario'),
    path('listadoDelegaciones', views.listado_delegaciones, name ='listado_delegaciones'),
    path('listadoDiocesis', views.listado_diocesis, name = 'listado_diocesis'),
    path('listadoVoluntariosGrupo', views.listado_voluntarios_grupo, name='listado_voluntarios_grupo'),
    path('modificarGrupo=<int:grupo_id>',views.modificar_grupo, name = 'modificar_grupo'),
    path('modificacionGrupo', views.modificacion_grupo, name = "modificacion_grupo"),
    path('modificarDelegacion=<int:delegation_id>', views.modificar_delegacion, name = 'modificar_delegacion'),
    path('modificacionDelegacion', views.modificacion_delegacion, name = 'modificacion_delegacion'),
    path('modificarDiocesis=<int:diocesis_id>', views.modificar_diocesis, name = 'modificar_diocesis'),
    path('modificacionDiocesis', views.modificacion_diocesis, name = 'modificacion_diocesis'),
    path('modificarParroquia=<int:parroquia_id>',views.modificar_parroquia, name = 'modificar_parroquia'),
    path('modificacionParroquia', views.modificacion_parroquia, name = "modificacion_parroquia"),
    path('modificarProyecto=<int:proyecto_id>',views.modificar_proyecto, name = 'modificar_proyecto'),
    path('modificacionProyecto', views.modificacion_proyecto, name = "modificacion_proyecto"),
    #path('modificarVoluntario=<int:voluntario_id>',views.modificar_voluntario, name = 'modificar_voluntario'),
    #path('modificacionVoluntario', views.modificacion_voluntario, name = "modificacion_voluntario"),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
