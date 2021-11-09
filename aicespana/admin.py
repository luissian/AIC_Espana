from django.contrib import admin
from .models import *

class EntidadesConCargoAdmin(admin.ModelAdmin):
    list_display = ['entidad']


class CargoAdmin(admin.ModelAdmin):
    list_display =['nombreCargo','entidadCargo']

class DelegacionAdmin(admin.ModelAdmin):
    list_display = ['nombreDelegacion']

class DiocesisAdmin(admin.ModelAdmin):
    list_display = ['nombreDiocesis', 'delegacionDependiente']

class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ['nombreParroquia', 'diocesisDependiente']

class GrupoAdmin(admin.ModelAdmin):
    list_display = ['nombreGrupo', 'parroquiaDependiente', 'provincia']

class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombreProyecto', 'poblacion', 'provincia']

class ActividadAdmin(admin.ModelAdmin):
    list_display = ['nombreActividad', 'domicilioSocial']

admin.site.register(EntidadesConCargo , EntidadesConCargoAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(Delegacion, DelegacionAdmin)
admin.site.register(Diocesis, DiocesisAdmin)
admin.site.register(Parroquia, ParroquiaAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Actividad, ActividadAdmin)
