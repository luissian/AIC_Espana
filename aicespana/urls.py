from django.urls import path
from django.conf import settings

from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index, name='index'),
    path('cargosPersonalIglesia', views.cargos_personal_iglesia, name = 'cargos_personal_iglesia'),
    path('cargosVoluntarios', views.cargos_voluntarios, name = 'cargos_voluntarios'),
    path('listadoDelegaciones', views.listado_delegaciones, name ='listado_delegaciones'),
    path('nuevoVoluntario', views.nuevo_voluntario, name='nuevo_voluntario'),
]
