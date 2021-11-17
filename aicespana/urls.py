from django.urls import path
from django.conf import settings

from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index, name='index'),
    path('nuevoVoluntario', views.nuevo_voluntario, name='nuevo_voluntario')
]
