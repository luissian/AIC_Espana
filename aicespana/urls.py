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
    path('altaPersonalIglesia', views.alta_personal_iglesia, name = 'alta_personal_iglesia'),
    path('altaProyecto', views.alta_proyecto, name = 'alta_proyecto'),
    path('altaVoluntario', views.alta_voluntario, name='alta_voluntario'),
    path('cargosPersonalIglesia', views.cargos_personal_iglesia, name = 'cargos_personal_iglesia'),
    path('cargosVoluntarios', views.cargos_voluntarios, name = 'cargos_voluntarios'),
    path('informacionVoluntario',views.informacion_voluntario, name = 'informacion_voluntario'),
    path('listadoDelegaciones', views.listado_delegaciones, name ='listado_delegaciones'),
    path('listadoDiocesis', views.listado_diocesis, name = 'listado_diocesis'),
    path('listadoVoluntariosGrupo', views.listado_voluntarios_grupo, name='listado_voluntarios_grupo'),
    path('modificarDelegacion=<int:delegation_id>', views.modificar_delegacion, name = 'modificar_delegacion'),
    path('modificacionDelegacion', views.modificacion_delegacion, name = 'modificacion_delegacion'),


]
