import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage

memory_project_path_location = FileSystemStorage(location='memorias_de_proyectos')


class EntidadesConCargo(models.Model):
    entidad =models.CharField(max_length=20)

    def __str__(self):
        return '%s' %(self.entidad)

class Cargo(models.Model):
    entidadCargo = models.ForeignKey(
                        EntidadesConCargo,
                        on_delete=models.CASCADE)
    nombreCargo = models.CharField(max_length=50)

    def __str__(self):
        return '%s,%s' %(self.entidadCargo , self.nombreCargo)

    def get_cargo_id(self):
        return '%s' %(self.pk)

    def get_cargo_name(self):
        return '%s' %(self.nombreCargo)

class ActividadManager(models.Manager):
    def create_actividad(self,data):

        return new_actividad

class Actividad(models.Model):
    nombreActividad = models.CharField(max_length=200)
    calle = models.CharField(max_length=40, null=True, blank = True)
    poblacion = models.CharField(max_length=40, null=True, blank = True)
    provincia = models.CharField(max_length=20, null=True, blank = True)

    def __str__ (self):
        return '%s' %(self.nombreActividad)

    def get_actividad_id(self):
        return '%s' %(self.pk)

    def get_activity_name (self):
        return '%s' %(self.nombreActividad)


class Proyecto(models.Model):
    nombreProyecto = models.CharField(max_length=80)
    memoriaProyecto = models.FileField( storage= memory_project_path_location)
    calle = models.CharField(max_length=40)
    poblacion = models.CharField(max_length=20)
    provincia = models.CharField(max_length=20)

    def __str__(self):
        return '%s' %(self.nombreProyecto)

    def get_proyecto_id(self):
        return '%s' %(self.pk)

    def get_project_name(self):
        return '%s' %(self.nombreProyecto)

class Delegacion(models.Model):
    nombreDelegacion = models.CharField(max_length=20)


    def __str__(self):
        return '%s' %(self.nombreDelegacion)

    def get_delegacion_name(self):
        return '%s' %(self.nombreDelegacion)


class Diocesis(models.Model):
    delegacionDependiente = models.ForeignKey(
                        Delegacion,
                        on_delete=models.CASCADE)
    nombreDiocesis = models.CharField(max_length=20)

    def __str__ (self):
        return '%s' %(self.nombreDiocesis)

    def get_delegacion_name (self):
        if delegacionDependiente :
            return '%s' %(self.delegacionDependiente.get_delegacion_name())
        return 'No asignado'

    def get_diocesis_name (self):
        return '%s' %(self.nombreDiocesis)

class Parroquia(models.Model):
    diocesisDependiente = models.ForeignKey(
                        Diocesis,
                        on_delete=models.CASCADE)
    nombreParroquia = models.CharField(max_length=60)
    calle = models.CharField(max_length=40)
    poblacion = models.CharField(max_length=20)
    provincia = models.CharField(max_length=20)

    def __str__(self):
        return '%s' %(self.nombreParroquia)

    def get_parroquia_name(self):
        return '%s' %(self.nombreParroquia)

    def get_diocesis_name(self):
        if self.diocesisDependiente:
            return '%s' %(self.diocesisDependiente.get_diocesis_name())
        return 'No asignado'

class Grupo(models.Model):
    parroquiaDependiente = models.ForeignKey(
                        Parroquia,
                        on_delete=models.CASCADE)
    calle = models.CharField(max_length=40, null=True, blank = True)
    poblacion = models.CharField(max_length=40, null=True, blank = True)
    provincia = models.CharField(max_length=20, null=True, blank = True)
    fechaErecion = models.DateField(auto_now = False, null=True, blank = True)
    registroNumero =  models.CharField(max_length=20)
    nombreGrupo =  models.CharField(max_length=40)


    def __str__ (self):
        return '%s' %(self.nombreGrupo)

    def get_group_id(self):
        return '%s' %(self.pk)

    def get_group_name (self):
        return '%s' %(self.nombreGrupo)

    def get_parroquia_name(self):
        if self.parroquiaDependiente :
            return '%s' %(self.parroquiaDependiente.get_parroquia_name())
        return 'No asignado'


    def get_diocesis_name(self):
        if self.parroquiaDependiente :
            return '%s' %(self.parroquiaDependiente.get_diocesis_name())
        return 'No asignado'

    def get_delegacion_name(self):
        if self.parroquiaDependiente :
            return '%s' %(self.parroquiaDependiente.get_diocesis_name())
        return 'No asignado'



class TipoColaboracion(models.Model):
    tipoColaboracion = models.CharField(max_length=40)

    def __str__ (self):
        return '%s' %(self.tipoColaboracion)

    def get_tipo_colaboracion_id(self):
        return '%s' %(self.pk)

    def get_collaboration_name (self):
        return '%s' %(self.tipoColaboracion)


class PersonalExternoManager(models.Manager):
    def create_new_external_pesonel(self, data):
        new_ext_personel = self.create(nombre = data['nombre'], apellido = data['apellidos'], calle = data['calle'],
                poblacion = data['poblacion'], provincia = data['provincia'], codigoPostal = data['codigo'],
                DNI = data['nif'], fechaNacimiento = data['nacimiento'], email = data['email'], telefonoFijo = data['fijo'],
                telefonoMovil = data['movil'] )
        return new_ext_personel

class PersonalExterno(models.Model):
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    proyectoAsociado = models.ForeignKey(
                        Proyecto,
                        on_delete=models.CASCADE, null=True, blank = True)
    actividadAsociada = models.ForeignKey(
                        Actividad,
                        on_delete=models.CASCADE, null=True, blank = True)
    cargo = models.ForeignKey(
                        Cargo,
                        on_delete=models.CASCADE, null=True, blank = True)
    tipoColaboracion = models.ForeignKey(
                        TipoColaboracion,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    calle = models.CharField(max_length=40, null=True, blank = True)
    poblacion = models.CharField(max_length=40, null=True, blank = True)
    provincia = models.CharField(max_length=20, null=True, blank = True)
    codigoPostal = models.CharField(max_length=20, null=True, blank = True)
    DNI = models.CharField(max_length=20, null=True, blank = True)
    fechaNacimiento = models.DateField(auto_now = False, null=True, blank = True)
    email = models.CharField(max_length=40, null=True, blank = True)
    telefonoFijo = models.CharField(max_length=20, null=True, blank = True)
    telefonoMovil = models.CharField(max_length=40, null=True, blank = True)

    def __str__ (self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_id(self):
        return '%s' %(self.pk)

    def get_personal_name(self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_location(self):
        return '%s' %(self.location)

    def get_activity_belongs_to(self):
        if self.actividadAsociada:
            return '%s' %(self.get_activity_name())
        return ''

    def get_collaboration_belongs_to(self):
        if self.tipoColaboracion:
            return '%s' %(self.get_collaboration_name())
        return ''

    def get_diocesis_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_diocesis_name())
        return ''

    def get_delegacion_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_delegacion_name())
        return ''

    def get_group_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_group_name())
        return ''
    def get_parroquia_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_parroquia_name())
        return ''

    def get_project_belongs_to(self):
        if self.proyectoAsociado :
            return '%s' %(self.proyectoAsociado.get_project_name())
        return ''

    def get_responability_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_name())
        return ''

    def update_information(self, data):
        if data['grupo'] != '':
            try:
                grupo_obj = Grupo.objects.get(pk__exact = data['grupo'])
            except:
                grupo_obj = None
        else:
            grupo_obj = None
        if data['proyecto'] != '':
            try:
                proyecto_obj = Proyecto.objects.get(pk__exact = data['proyecto'])
            except:
                proyecto_obj = None
        else:
            proyecto_obj = None
        if data['actividad'] != '':
            try:
                actividad_obj = Actividad.objects.get(pk__exact = data['actividad'])
            except:
                actividad_obj = None
        else:
            actividad_obj = None
        if data['cargo'] != '':
            try:
                cargo_obj = Cargo.objects.get(pk__exact = data['cargo'])
            except:
                cargo_obj = None
        else:
            cargo_obj = None
        if data['colaboracion'] != '':
            try:
                colaboracion_obj = TipoColaboracion.objects.get(pk__exact = data['colaboracion'])
            except:
                colaboracion_obj = None
        else:
            colaboracion_obj = None
        self.grupoAsociado = grupo_obj
        self.proyectoAsociado = proyecto_obj
        self.actividadAsociada = actividad_obj
        self.cargo = cargo_obj
        self.tipoColaboracion = colaboracion_obj
        self.save()
        return

    objects = PersonalExternoManager()

class PersonalIglesia(models.Model):
    cargo = models.ForeignKey(
                        Cargo,
                        on_delete=models.CASCADE, null=True, blank = True)
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    delegacion = models.ForeignKey(
                        Delegacion,
                        on_delete=models.CASCADE)
