import os
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
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



class Delegacion(models.Model):
    nombreDelegacion = models.CharField(max_length=20)


    def __str__(self):
        return '%s' %(self.nombreDelegacion)

    def get_delegacion_id(self):
        return '%s' %(self.pk)

    def get_delegacion_name(self):
        return '%s' %(self.nombreDelegacion)

    def update_delegacion_name(self, name):
        self.nombreDelegacion = name
        self.save()
        return self

class DiocesisManager(models.Manager):
    def create_new_diocesis(self, data):
        if Delegacion.objects.filter(pk__exact = data['delegation_id']).exists():
            delegation_obj = Delegacion.objects.filter(pk__exact = data['delegation_id']).last()
        new_diocesis = self.create(nombreDiocesis = data['name'], delegacionDependiente = delegation_obj )
        return new_diocesis

class Diocesis(models.Model):
    delegacionDependiente = models.ForeignKey(
                        Delegacion,
                        on_delete=models.CASCADE)
    nombreDiocesis = models.CharField(max_length=80)

    def __str__ (self):
        return '%s' %(self.nombreDiocesis)

    def get_diocesis_id(self):
        return '%s' %(self.pk)

    def get_delegacion_id (self):
        if self.delegacionDependiente :
            return '%s' %(self.delegacionDependiente.get_delegacion_id())
        return ''

    def get_delegacion_name (self):
        if self.delegacionDependiente :
            return '%s' %(self.delegacionDependiente.get_delegacion_name())
        return 'No asignado'

    def get_diocesis_name (self):
        return '%s' %(self.nombreDiocesis)

    def update_diocesis_data(self,nombre,delegacion):
        self.nombreDiocesis = nombre
        self.delegacionDependiente = delegacion
        self.save()
        return self

    objects = DiocesisManager()


class ParroquiaManager(models.Manager):
    def create_new_parroquia (self, data):
        new_parroquia = self.create(diocesisDependiente = data['diocesis_obj'], nombreParroquia = data['nombre'],
                    calle = data['calle'],poblacion = data['poblacion'], codigoPostal = data['codigo'],
                    observaciones = data['observaciones'])
        return new_parroquia


class Parroquia(models.Model):
    diocesisDependiente = models.ForeignKey(
                        Diocesis,
                        on_delete=models.CASCADE)
    nombreParroquia = models.CharField(max_length=80)
    calle = models.CharField(max_length=80)
    poblacion = models.CharField(max_length=60)
    provincia = models.CharField(max_length=40)
    codigoPostal = models.CharField(max_length=20, null=True, blank = True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return '%s' %(self.nombreParroquia)

    def get_parroquia_id(self):
        return '%s' %(self.pk)

    def get_parroquia_name(self):
        return '%s' %(self.nombreParroquia)

    def get_diocesis_name(self):
        if self.diocesisDependiente:
            return '%s' %(self.diocesisDependiente.get_diocesis_name())
        return 'No asignado'
    def get_diocesis_id(self):
        if self.diocesisDependiente:
            return '%s' %(self.diocesisDependiente.get_diocesis_id())
        return ''

    def get_poblacion_name(self):
        return '%s' %(self.poblacion)

    def get_provincia_name(self):
        return '%s' %(self.provincia)

    def get_parroquia_full_data(self):
        return [self.nombreParroquia, self.get_parroquia_id(), self.get_diocesis_name(), self.get_diocesis_id() ,self.calle, self.poblacion, self.provincia,self.codigoPostal,self.observaciones]

    def update_parroquia_data(self, data):
        self.diocesisDependiente = Diocesis.objects.filter(pk__exact = data['diocesisID']).last()
        self.nombreParroquia = data['parroquia_name']
        self.calle = data['calle']
        self.poblacion = data['poblacion']
        self.provincia = data['provincia']
        self.codigoPostal = data['codigo']
        self.observaciones = data['observaciones']
        self.save()
        return self

    objects = ParroquiaManager()


class GrupoManager(models.Manager):
    def create_new_group(self, data):

        new_group = self.create(diocesisDependiente = data['diocesis_obj'], nombreGrupo = data['nombre'],
                    calle = data['calle'],poblacion = data['poblacion'], codigoPostal = data['codigo'],
                    observaciones = data['observaciones'],registroNumero = data['registro'],
                    fechaErecion =  datetime.strptime(data['fechaErecion'],"%Y-%m-%d").date())

        return new_group

class Grupo(models.Model):
    parroquiaDependiente = models.ForeignKey(
                        Parroquia,
                        on_delete=models.CASCADE, null=True, blank = True)
    diocesisDependiente = models.ForeignKey(
                        Diocesis,
                        on_delete=models.CASCADE, null=True, blank = True)
    calle = models.CharField(max_length=80, null=True, blank = True)
    poblacion = models.CharField(max_length=60, null=True, blank = True)
    provincia = models.CharField(max_length=40, null=True, blank = True)
    codigoPostal = models.CharField(max_length=20, null=True, blank = True)
    fechaErecion = models.DateField(auto_now = False, null=True, blank = True)
    registroNumero =  models.CharField(max_length=50)
    nombreGrupo =  models.CharField(max_length=80)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    grupoActivo =  models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)


    def __str__ (self):
        return '%s' %(self.nombreGrupo)

    def get_grupo_id(self):
        return '%s' %(self.pk)

    def get_grupo_name (self):
        return '%s' %(self.nombreGrupo)

    def get_parroquia_name(self):
        if self.parroquiaDependiente :
            return '%s' %(self.parroquiaDependiente.get_parroquia_name())
        return 'No asignado'

    def get_diocesis_id(self):
        if self.diocesisDependiente:
            return '%s' %(self.diocesisDependiente.get_diocesis_id())
        return ''

    def get_diocesis_name(self):
        if self.diocesisDependiente :
            return '%s' %(self.diocesisDependiente.get_diocesis_name())
        return 'No asignado'

    def get_delegacion_name(self):
        if self.parroquiaDependiente :
            return '%s' %(self.parroquiaDependiente.get_diocesis_name())
        return 'No asignado'

    def get_grupo_full_data(self):
        if self.fechaErecion is None:
            alta = ''
        else:
            alta = self.fechaErecion.strftime("%Y-%m-%d")
        if self.fechaBaja is None:
            baja = ''
        else:
            baja = self.fechaBaja.strftime("%B %d, %Y")
        if self.grupoActivo:
            activo = 'true'
        else:
            activo = 'false'
        return [self.nombreGrupo, self.pk, self.get_diocesis_name(), self.get_diocesis_id() ,self.calle, self.poblacion, self.provincia,self.codigoPostal,self.observaciones, alta, baja,activo ]

    def update_grupo_data(self, data):
        self.diocesisDependiente = Diocesis.objects.filter(pk__exact = data['diocesisID']).last()
        self.nombreGrupo = data['grupo_name']
        self.calle = data['calle']
        self.poblacion = data['poblacion']
        self.provincia = data['provincia']
        self.codigoPostal = data['codigo']
        self.fechaErecion = datetime.strptime(data['alta'],"%Y-%m-%d").date()
        if data['activo'] == 'false':
            self.grupoActivo = False
        else:
            self.grupoActivo = True
        if data['baja'] != '':
            self.baja = datetime.strptime(data['baja'],"%Y-%m-%d").date()
        self.observaciones = data['observaciones']
        self.save()
        return self

    objects = GrupoManager()

class ProyectoManager(models.Manager):
    def create_new_proyecto(self,data):

        if data['alta'] != '':
            alta =  datetime.strptime(data['alta'],"%Y-%m-%d").date()
        else:
            alta = None

        memoria = data['memoria_file'] if 'memoria_file' in  data != '' else None
        fotografia = data['fotografia_file'] if 'fotografia_file' in data != '' else None
        import pdb; pdb.set_trace()
        new_project = self.create(nombreProyecto = data['nombre'],grupoAsociado = data['grupo_obj'],
                fechaAlta = alta, memoriaProyecto = memoria, fotografiaProyecto = fotografia )
        return new_project

class Proyecto(models.Model):
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombreProyecto = models.CharField(max_length=80)
    memoriaProyecto = models.FileField( storage= memory_project_path_location, null=True, blank = True)
    fotografiaProyecto = models.FileField( storage= memory_project_path_location, null=True, blank = True)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    proyectoActivo =  models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return '%s' %(self.nombreProyecto)

    def get_proyecto_id(self):
        return '%s' %(self.pk)

    def get_proyecto_name(self):
        return '%s' %(self.nombreProyecto)

    def get_diocesis_name(self):
        if self.grupoAsociado:
            return '%s' %(self.grupoAsociado.get_diocesis_name())
        return ''

    def get_grupo_name(self):
        if self.grupoAsociado:
            return '%s' %(self.grupoAsociado.get_grupo_name())
        return ''

    def get_grupo_id(self):
        if self.grupoAsociado:
            return '%s' %(self.grupoAsociado.get_grupo_id())
        return ''

    def get_proyecto_full_data(self):
        if self.fechaAlta is None:
            alta = ''
        else:
            alta = self.fechaAlta.strftime("%Y-%m-%d")
        if self.fechaBaja is None:
            baja = ''
        else:
            baja = self.fechaBaja.strftime("%B %d, %Y")
        if self.proyectoActivo:
            activo = 'true'
        else:
            activo = 'false'
        return [self.nombreProyecto, self.pk, self.get_grupo_id(), self.get_grupo_name(), self.get_diocesis_name(), alta, baja, activo, self.memoriaProyecto, self.fotografiaProyecto ]

    def update_proyecto_data(self, data):
        self.grupoAsociado = Grupo.objects.filter(pk__exact = data['grupoID']).last()
        self.nombreProyecto = data['proyecto_name']
        if data['activo'] == 'false':
            self.grupoActivo = False
        else:
            self.grupoActivo = True
        if data['alta'] != '':
            self.fechaAlta = datetime.strptime(data['alta'],"%Y-%m-%d").date()
        if data['baja'] != '':
            self.fechaBaja = datetime.strptime(data['baja'],"%Y-%m-%d").date()
        self.observaciones = data['observaciones']
        if 'memoria_file' in data:
            self.memoriaProyecto = data['memoria_file']
        if 'fotografia_file' in data:
            self.fotografiaProyecto = data['fotografia_file']
        self.save()
        return self



    objects = ProyectoManager()

class Actividad(models.Model):
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombreActividad = models.CharField(max_length=200)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    actividadActiva = models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__ (self):
        return '%s' %(self.nombreActividad)

    def get_activity_id(self):
        return '%s' %(self.pk)

    def get_activity_name (self):
        return '%s' %(self.nombreActividad)


class TipoColaboracion(models.Model):
    tipoColaboracion = models.CharField(max_length=60)

    def __str__ (self):
        return '%s' %(self.tipoColaboracion)

    def get_tipo_colaboracion_id(self):
        return '%s' %(self.pk)

    def get_collaboration_name (self):
        return '%s' %(self.tipoColaboracion)




class PersonalExternoManager(models.Manager):
    def create_new_external_personel(self, data):
        if TipoColaboracion.objects.filter(pk__exact = data['tipoColaboracion']).exists():
            tipoColaboracion_obj = TipoColaboracion.objects.get(pk__exact = data['tipoColaboracion'])
        else:
            tipoColaboracion_obj = None
        if data['grupoID'] != '':
            grupo_obj = Grupo.objects.filter(pk__exact = data['grupoID']).last()
        else:
            grupo_obj = None
        if data['boletin'] == 'true':
            boletin = True
        else:
            boletin = False
        new_ext_personel = self.create(nombre = data['nombre'], apellido = data['apellidos'], calle = data['calle'],
                poblacion = data['poblacion'], provincia = data['provincia'], codigoPostal = data['codigo'],
                DNI = data['nif'], fechaNacimiento = data['nacimiento'], email = data['email'], telefonoFijo = data['fijo'],
                telefonoMovil = data['movil'],  tipoColaboracion = tipoColaboracion_obj, grupoAsociado = grupo_obj,
                recibirBoletin = boletin)
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
    calle = models.CharField(max_length=80, null=True, blank = True)
    poblacion = models.CharField(max_length=60, null=True, blank = True)
    provincia = models.CharField(max_length=40, null=True, blank = True)
    codigoPostal = models.CharField(max_length=20, null=True, blank = True)
    DNI = models.CharField(max_length=20, null=True, blank = True)
    fechaNacimiento = models.DateField(auto_now = False, null=True, blank = True)
    email = models.CharField(max_length=40, null=True, blank = True)
    telefonoFijo = models.CharField(max_length=20, null=True, blank = True)
    telefonoMovil = models.CharField(max_length=40, null=True, blank = True)
    recibirBoletin = models.BooleanField(default= False)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    peronalActivo =  models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

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
            return '%s' %(self.actividadAsociada.get_activity_name())
        return ''

    def get_activity_id_belongs_to(self):
        if self.actividadAsociada:
            return '%s' %(self.actividadAsociada.get_activity_id())
        return ''

    def get_collaboration_belongs_to(self):
        if self.tipoColaboracion:
            return '%s' %(self.tipoColaboracion.get_collaboration_name())
        return ''

    def get_collaboration_id_belongs_to(self):
        if self.tipoColaboracion:
            return '%s' %(self.tipoColaboracion.get_tipo_colaboracion_id())
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
            return '%s' %(self.grupoAsociado.get_grupo_name())
        return ''

    def get_group_id_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_grupo_id())
        return ''

    def get_old(self):
        if self.fechaNacimiento != None:
            return relativedelta(date.today(), self.fechaNacimiento).years
        return 0

    def get_parroquia_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_parroquia_name())
        return ''

    def get_project_belongs_to(self):
        if self.proyectoAsociado :
            return '%s' %(self.proyectoAsociado.get_proyecto_name())
        return ''

    def get_project_id_belongs_to(self):
        if self.proyectoAsociado :
            return '%s' %(self.proyectoAsociado.get_proyecto_id())
        return ''

    def get_responability_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_name())
        return ''

    def get_responability_id_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_id())
        return ''

    def get_voluntario_data(self):
        data = []
        data.append(str(self.nombre + ' ' + self.apellido))
        data.append(self.calle)
        data.append(self.poblacion)
        data.append(self.provincia)
        data.append(self.codigoPostal)
        data.append(self.email)
        data.append(self.DNI)
        data.append(self.telefonoMovil)
        data.append(self.get_group_belongs_to())
        data.append(self.get_responability_belongs_to())
        return data

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


class PersonalManager(models.Manager):
    def create_new_personel(self, data):
        new_personel = self.create(nombre = data['nombre'], apellido = data['apellido'],
                DNI = data['nif'], email = data['email'], telefonoFijo = data['fijo'],
                telefonoMovil = data['movil'])
        return new_personel


class PersonalIglesia(models.Model):
    cargo = models.ForeignKey(
                        Cargo,
                        on_delete=models.CASCADE, null=True, blank = True)
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    delegacion = models.ForeignKey(
                        Delegacion,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombre = models.CharField(max_length=40,null=True, blank = True)
    apellido = models.CharField(max_length=40,null=True, blank = True)
    DNI = models.CharField(max_length=20, null=True, blank = True)
    email = models.CharField(max_length=40, null=True, blank = True)
    telefonoFijo = models.CharField(max_length=20, null=True, blank = True)
    telefonoMovil = models.CharField(max_length=40, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    personalActivo = models.BooleanField(default= True)
    recibirBoletin = models.BooleanField(default= False)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__ (self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_id(self):
        return '%s' %(self.pk)

    def get_personal_name(self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_delegacion_belongs_to(self):
        if self.delegacion :
            return '%s' %(self.delegacion.get_delegacion_name())
        return ''

    def get_delegacion_id_belongs_to(self):
        if self.delegacion :
            return '%s' %(self.delegacion.get_delegacion_id())
        return ''

    def get_dicesis_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_diocesis_name())
        return ''

    def get_group_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_grupo_name())
        return ''

    def get_group_id_belongs_to(self):
        if self.grupoAsociado :
            return '%s' %(self.grupoAsociado.get_grupo_id())
        return ''

    def get_responability_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_name())
        return ''

    def get_responability_id_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_id())
        return ''


    def update_information(self, data):
        if data['grupo'] != '':
            try:
                grupo_obj = Grupo.objects.get(pk__exact = data['grupo'])
            except:
                grupo_obj = None
        else:
            grupo_obj = None
        if data['delegacion'] != '':
            try:
                delegacion_obj = Delegacion.objects.get(pk__exact = data['delegacion'])
            except:
                delegacion_obj = None
        else:
            delegacion_obj = None
        if data['cargo'] != '':
            try:
                cargo_obj = Cargo.objects.get(pk__exact = data['cargo'])
            except:
                cargo_obj = None
        else:
            cargo_obj = None

        self.grupoAsociado = grupo_obj
        self.delegacion = delegacion_obj
        self.cargo = cargo_obj
        self.save()
        return self

    objects = PersonalManager()
