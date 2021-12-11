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
    actions = ['download_file']
    list_display = ['nombreProyecto', 'poblacion', 'provincia', 'memoriaProyecto']
    def download_file(self, request, queryset):
        None
    download_file.short_description = "Download CSV file for selected stats."

class ActividadAdmin(admin.ModelAdmin):
    list_display = ['nombreActividad',  'poblacion', 'provincia']

class PersonalExternoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'DNI', 'fechaNacimiento']

class TipoColaboracionAdmin(admin.ModelAdmin):
    list_display = ['tipoColaboracion']

class PersonalIglesiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'DNI']

admin.site.register(EntidadesConCargo , EntidadesConCargoAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(Delegacion, DelegacionAdmin)
admin.site.register(Diocesis, DiocesisAdmin)
admin.site.register(Parroquia, ParroquiaAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Actividad, ActividadAdmin)
admin.site.register(PersonalExterno,PersonalExternoAdmin)
admin.site.register(TipoColaboracion,TipoColaboracionAdmin)
admin.site.register(PersonalIglesia,PersonalIglesiaAdmin)
