from django.contrib import admin
import aicespana.models


class EntidadesConCargoAdmin(admin.ModelAdmin):
    list_display = ["entidad"]


class CargoAdmin(admin.ModelAdmin):
    list_display = ["nombreCargo", "entidadCargo"]
    search_fields = ("nombreCargo__icontains",)


class DelegacionAdmin(admin.ModelAdmin):
    list_display = ["nombreDelegacion", "login_user"]
    search_fields = ("nombreDelegacion__icontains",)


class DiocesisAdmin(admin.ModelAdmin):
    list_display = ["nombreDiocesis", "delegacionDependiente", "diocesisActiva"]
    search_fields = ("nombreDiocesis__icontains",)


class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ["nombreParroquia", "diocesisDependiente"]
    search_fields = ("nombreParroquia__icontains",)


class GrupoAdmin(admin.ModelAdmin):
    list_display = ["nombreGrupo", "grupoActivo", "diocesisDependiente", "provincia"]
    search_fields = ("nombreGrupo__icontains",)


class ProyectoAdmin(admin.ModelAdmin):
    actions = ["download_file"]
    list_display = ["nombreProyecto", "proyectoActivo", "fechaAlta", "fechaBaja"]

    def download_file(self, request, queryset):
        None
    download_file.short_description = "Download CSV file for selected stats."
    search_fields = ("nombreProyecto__icontains",)


class ActividadAdmin(admin.ModelAdmin):
    list_display = ["nombreActividad", "actividadActiva" , "fechaAlta", "fechaBaja"]
    search_fields = ("nombreActividad__icontains",)


class PersonalExternoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "apellido", "DNI", "fechaNacimiento"]
    search_fields = ("apellido__icontains",)


class TipoColaboracionAdmin(admin.ModelAdmin):
    list_display = ["tipoColaboracion"]


class PersonalIglesiaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "apellido", "DNI"]
    search_fields = ("apellido__icontains",)


admin.site.register(aicespana.models.EntidadesConCargo, EntidadesConCargoAdmin)
admin.site.register(aicespana.models.Cargo, CargoAdmin)
admin.site.register(aicespana.models.Delegacion, DelegacionAdmin)
admin.site.register(aicespana.models.Diocesis, DiocesisAdmin)
admin.site.register(aicespana.models.Parroquia, ParroquiaAdmin)
admin.site.register(aicespana.models.Grupo, GrupoAdmin)
admin.site.register(aicespana.models.Proyecto, ProyectoAdmin)
admin.site.register(aicespana.models.Actividad, ActividadAdmin)
admin.site.register(aicespana.models.PersonalExterno, PersonalExternoAdmin)
admin.site.register(aicespana.models.TipoColaboracion, TipoColaboracionAdmin)
admin.site.register(aicespana.models.PersonalIglesia, PersonalIglesiaAdmin)
