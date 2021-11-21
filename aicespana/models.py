from django.db import models
from django.contrib.auth.models import User


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

    def get_responsability_name(self):
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

    def get_activity_name (self):
        return '%s' %(self.nombreActividad)


class Proyecto(models.Model):
    nombreProyecto = models.CharField(max_length=80)
    memoriaProyecto = models.CharField(max_length=800)
    calle = models.CharField(max_length=40)
    poblacion = models.CharField(max_length=20)
    provincia = models.CharField(max_length=20)

    def __str__(self):
        return '%s' %(self.nombreProyecto)

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


class Parroquia(models.Model):
    diocesisDependiente = models.ForeignKey(
                        Diocesis,
                        on_delete=models.CASCADE)
    nombreParroquia = models.CharField(max_length=60)
    calle = models.CharField(max_length=40)
    poblacion = models.CharField(max_length=20)
    provincia = models.CharField(max_length=20)

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

    def get_group_name (self):
        return '%s' %(self.nombreGrupo)


class TipoColaboracion(models.Model):
    tipoColaboracion = models.CharField(max_length=40)

    def __str__ (self):
        return '%s' %(self.tipoColaboracion)

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
        return '%s,%s' %(self.nombre, self.apellido)

    def get_personal_id(self):
        return '%s' %(self.pk)

    def get_personal_name(self):
        return '%s,%s' %(self.nombre, self.apellido)

    def get_personal_location(self):
        return '%s' %(self.location)


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
