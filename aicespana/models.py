import os
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage
from django.conf import settings
documentacion_proyectos = settings.MEDIA_ROOT
carpeta_imagenes= os.path.join(documentacion_proyectos, 'images')
memory_project_path_location = FileSystemStorage(location=documentacion_proyectos)
images_delegation = FileSystemStorage(location=carpeta_imagenes)

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

# class ActividadManager(models.Manager):
#    def create_actividad(self,data):
#        return new_actividad

class DelegacionManager(models.Manager):
    def create_new_delegacion(self, data):
        new_delegacion = self.create(nombreDelegacion = data['nombre'],imagenDelegacion = data['imagen'] )
        return new_delegacion

class Delegacion(models.Model):
    nombreDelegacion = models.CharField(max_length=20)
    #imagenDelegacion = models.CharField(max_length=80, null=True, blank=True)
    imagenDelegacion = models.FileField( storage= images_delegation, null=True, blank = True)


    def __str__(self):
        return '%s' %(self.nombreDelegacion)

    def get_delegacion_id(self):
        return '%s' %(self.pk)

    def get_delegacion_name(self):
        return '%s' %(self.nombreDelegacion)

    def get_delegacion_image(self):
        return '%s' %(self.imagenDelegacion)


    def update_delegacion_name_and_image(self, name,image):
        self.nombreDelegacion = name
        if image:
            self.imagenDelegacion = image
        self.save()
        return self
    objects = DelegacionManager()

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
    diocesisActiva = models.BooleanField(default=True)

    def __str__ (self):
        return '%s' %(self.nombreDiocesis)

    def get_diocesis_id(self):
        return '%s' %(self.pk)

    def get_delegacion_id (self):
        if self.delegacionDependiente :
            return '%s' %(self.delegacionDependiente.get_delegacion_id())
        return ''

    def get_diocesis_status(self):
        if self.diocesisActiva:
            activo = 'true'
        else:
            activo = 'false'
        return activo

    def get_diocesis_depending_groups(self):
        groups = ""
        if Grupo.objects.filter(diocesisDependiente=self, grupoActivo=True).exists():
            groups = Grupo.objects.filter(diocesisDependiente=self, grupoActivo=True).values("nombreGrupo")
        return groups

    def get_delegacion_name (self):
        if self.delegacionDependiente :
            return '%s' %(self.delegacionDependiente.get_delegacion_name())
        return 'No asignado'

    def get_diocesis_name (self):
        return '%s' %(self.nombreDiocesis)

    def update_diocesis_data(self, nombre, delegacion, status):
        self.nombreDiocesis = nombre
        self.delegacionDependiente = delegacion
        if status == 'false':
            self.diocesisActiva = False
        else:
            self.diocesisActiva = True
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
        if data['fechaErecion'] == '':
            data['fechaErecion'] = None
        new_group = self.create(diocesisDependiente = data['diocesis_obj'], nombreGrupo = data['nombre'],
                    calle = data['calle'],poblacion = data['poblacion'], codigoPostal = data['codigo'],
                    observaciones = data['observaciones'],registroNumero = data['registro'],
                    fechaErecion =  data['fechaErecion'], provincia=data["provincia"])

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
        return '%s' %(self.nombreGrupo) + ' en diocesis'+ self.diocesisDependiente.nombreDiocesis

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
        if self.diocesisDependiente :
            return '%s' %(self.diocesisDependiente.get_delegacion_name())
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
        if self.memoriaProyecto :
            memoria_proyecto = os.path.join(settings.MEDIA_URL, str(self.memoriaProyecto))
        else:
            memoria_proyecto = ''
        if self.fotografiaProyecto :
            fotografia_proyecto = os.path.join(settings.MEDIA_URL,str(self.fotografiaProyecto))
        else:
            fotografia_proyecto = ''
        return [self.nombreProyecto, self.pk, self.get_grupo_id(), self.get_grupo_name(), self.get_diocesis_name(), alta, baja, activo, memoria_proyecto, fotografia_proyecto ]

    def update_proyecto_data(self, data):
        self.grupoAsociado = Grupo.objects.filter(pk__exact = data['grupoID']).last()
        self.nombreProyecto = data['proyecto_name']
        if data['activo'] == 'false':
            self.proyectoActivo = False
        else:
            self.proyectoActivo = True
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


class ActividadManager(models.Manager):
    def create_new_actividad(self,data):

        if data['alta'] != '':
            alta = datetime.strptime(data['alta'], "%Y-%m-%d").date()
        else:
            alta = None

        memoria = data['memoria_file'] if 'memoria_file' in data != '' else None
        fotografia = data['fotografia_file'] if 'fotografia_file' in data != '' else None

        new_actividad = self.create(
            nombreActividad=data['nombre'],
            # grupoAsociado = data['grupo_obj'],
            fechaAlta=alta,
            memoriaActividad=memoria,
            fotografiaActividad=fotografia)
        return new_actividad


class Actividad(models.Model):
    grupoAsociado = models.ForeignKey(
                        Grupo,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombreActividad = models.CharField(max_length=200)
    memoriaActividad = models.FileField( storage= memory_project_path_location, null=True, blank = True)
    fotografiaActividad = models.FileField( storage= memory_project_path_location, null=True, blank = True)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    actividadActiva = models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__ (self):
        return '%s' %(self.nombreActividad)

    def get_actividad_id(self):
        return '%s' %(self.pk)

    def get_actividad_name (self):
        return '%s' %(self.nombreActividad)

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

    def get_actividad_full_data(self):
        if self.fechaAlta is None:
            alta = ''
        else:
            alta = self.fechaAlta.strftime("%Y-%m-%d")
        if self.fechaBaja is None:
            baja = ''
        else:
            baja = self.fechaBaja.strftime("%Y-%m-%d")
        if self.actividadActiva:
            activo = 'true'
        else:
            activo = 'false'
        if self.memoriaActividad :
            memoria_actividad = os.path.join(settings.MEDIA_URL, str(self.memoriaActividad))
        else:
            memoria_actividad = ''
        if self.fotografiaActividad :
            fotografia_actividad = os.path.join(settings.MEDIA_URL,str(self.fotografiaActividad))
        else:
            fotografia_actividad = ''
        # return [self.nombreActividad, self.pk, self.get_grupo_id(), self.get_grupo_name(), self.get_diocesis_name(), alta, baja, activo, memoria_actividad, fotografia_actividad ]
        return [self.nombreActividad, self.pk, alta, baja, activo, memoria_actividad, fotografia_actividad]

    def update_actividad_data(self, data):
        # self.grupoAsociado = Grupo.objects.filter(pk__exact = data['grupoID']).last()
        self.nombreActividad = data['actividad_name']
        if data['activo'] == 'false':
            self.actividadActiva = False
        else:
            self.actividadActiva = True
        if data['alta'] != '':
            self.fechaAlta = datetime.strptime(data['alta'],"%Y-%m-%d").date()
        if data['baja'] != '':
            self.fechaBaja = datetime.strptime(data['baja'],"%Y-%m-%d").date()
        self.observaciones = data['observaciones']
        if 'memoria_file' in data:
            self.memoriaActividad = data['memoria_file']
        if 'fotografia_file' in data:
            self.fotografiaActividad = data['fotografia_file']
        self.save()
        return self

    objects = ActividadManager()

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
        if data['rec_boletin'] == '0':
            boletin = False
            online = False
        else:
            boletin = True
            if data['rec_boletin'] == "1":
                online = True
            else:
                online = False
        if data['nacimiento'] == '':
            data['nacimiento'] = None
        if data['alta'] == '':
            data['alta'] = None
        new_ext_personel = self.create(nombre = data['nombre'], apellido = data['apellidos'], calle = data['calle'],
                poblacion = data['poblacion'], provincia = data['provincia'], codigoPostal = data['codigo'],
                DNI = data['nif'], fechaNacimiento = data['nacimiento'],fechaAlta = data['alta'], email = data['email'], telefonoFijo = data['fijo'],
                telefonoMovil = data['movil'],  tipoColaboracion = tipoColaboracion_obj, grupoAsociado = grupo_obj,
                recibirBoletin = boletin, boletinOnline = online)
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
    boletinOnline = models.BooleanField(default= False)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    personalActivo =  models.BooleanField(default= True)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__ (self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_id(self):
        return '%s' %(self.pk)

    def get_personal_name(self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_only_name(self):
        return '%s' %(self.nombre)

    def get_personal_only_apellido(self):
        return '%s' %(self.apellido)

    def get_personal_location(self):
        return '%s' %(self.poblacion)

    def get_personal_provincia(self):
        return '%s' %(self.provincia)

    def get_actividad_belongs_to(self):
        if self.actividadAsociada:
            return '%s' %(self.actividadAsociada.get_actividad_name())
        return ''

    def get_actividad_id_belongs_to(self):
        if self.actividadAsociada:
            return '%s' %(self.actividadAsociada.get_actividad_id())
        return ''
    def get_actividad_data_for_form(self):
        if self.actividadAsociada is None:
            return ['','Sin asignar a Actividad', '', '']
        else:
            return [self.actividadAsociada.get_actividad_id(), self.actividadAsociada.get_actividad_name(),
                        self.actividadAsociada.get_grupo_name(), self.actividadAsociada.get_diocesis_name()]

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
        return ''

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

    def get_proyecto_data_for_form(self):
        if self.proyectoAsociado is None:
            return ['','Sin asignar a Proyecto', '']
        else:
            return [self.proyectoAsociado.get_proyecto_id(), self.proyectoAsociado.get_proyecto_name(),
                        self.proyectoAsociado.get_grupo_name(), self.proyectoAsociado.get_diocesis_name()]

    def get_responability_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_name())
        return ''

    def get_responability_id_belongs_to(self):
        if self.cargo :
            return '%s' %(self.cargo.get_cargo_id())
        return ''

    def get_movil_number(self):
        if self.telefonoMovil:
            return '%s' %(self.telefonoMovil)
        else:
            return ''

    def get_email(self):
        if self.email:
            return '%s' %(self.email)
        else:
            return ''

    def get_all_data_from_voluntario(self):
        if self.fechaAlta is None:
            alta = ''
        else:
            alta = self.fechaAlta.strftime("%Y-%m-%d")
        if self.fechaBaja is None:
            baja = ''
        else:
            baja = self.fechaBaja.strftime("%B %d, %Y")
        if self.fechaNacimiento is None:
            nacimiento = ''
        else:
            nacimiento = self.fechaNacimiento.strftime("%Y-%m-%d")
        if self.personalActivo:
            activo = 'true'
        else:
            activo = 'false'
        if self.recibirBoletin:
            boletin = 'true'
        else:
            boletin = 'false'
        if self.boletinOnline:
            online = "true"
        else:
            online = "false"
        if self.personalActivo:
            activo = 'true'
        else:
            activo = 'false'
        if self.tipoColaboracion is None:
            colaboracion = ''
            colaboracion_id = ''
        else:
            colaboracion = self.tipoColaboracion.get_collaboration_name()
            colaboracion_id = self.tipoColaboracion.get_tipo_colaboracion_id()
        if self.grupoAsociado is None:
            grupo = ''
            grupo_id = ''
            diocesis = ''
        else:
            grupo = self.grupoAsociado.get_grupo_name()
            grupo_id = self.grupoAsociado.get_grupo_id()
            diocesis = self.grupoAsociado.get_diocesis_name()
        if self.proyectoAsociado is None:
            proyecto_id = ''
            proyecto_name = ''
        else:
            proyecto_id = self.proyectoAsociado.get_proyecto_id()
            proyecto_name = self.proyectoAsociado.get_proyecto_name()
        if self.actividadAsociada is None:
            actividad_id = ''
            actividad_name = ''
        else:
            actividad_id = self.actividadAsociada.get_actividad_id()
            actividad_name = self.actividadAsociada.get_actividad_name()
        if boletin == 'true':
            if online == 'true':
                rec_boletin = '1'
            else:
                rec_boletin = '2'
        else:
            rec_boletin = "0"
        data = {}
        data['user_id'] = self.pk
        data['nombre'] = self.nombre
        data['apellido'] = self.apellido
        data['dni'] = self.DNI
        data['email'] = self.email
        data['fijo'] = self.telefonoFijo
        data['movil'] = self.telefonoMovil
        data['baja'] = baja
        data['alta'] = alta
        data['nacimiento'] = nacimiento
        data['calle'] = self.calle
        data['poblacion'] = self.poblacion
        data['provincia'] = self.provincia
        data['codigo'] = self.codigoPostal
        data['boletin'] = boletin
        data['observaciones'] = self.observaciones
        data['colaboracion'] = colaboracion
        data['colaboracion_id'] = colaboracion_id
        data['grupo'] = grupo
        data['grupo_id'] = grupo_id
        data['diocesis'] = diocesis
        data['proyecto_id'] = proyecto_id
        data['proyecto_name'] = proyecto_name
        data['actividad_id'] = actividad_id
        data['actividad_name'] = actividad_name
        data['activo'] = activo
        data['online'] = online
        data['rec_boletin'] = rec_boletin
        return data

    def get_data_for_boletin(self):
        data = []
        data.append(self.nombre)
        data.append(self.apellido)
        data.append(self.get_collaboration_belongs_to())
        data.append(self.calle)
        data.append(self.poblacion)
        data.append(self.provincia)
        data.append(self.codigoPostal)
        return data

    def get_data_for_online_boletin(self):
        data = []
        data.append(self.nombre)
        data.append(self.apellido)
        data.append(self.get_collaboration_belongs_to())
        data.append(self.email)
        return data

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
        data.append(self.get_diocesis_belongs_to())
        return data

    def get_data_for_actividad(self):
        data = []
        data.append(str(self.nombre + ' ' + self.apellido))
        data.append(self.actividadAsociada.get_actividad_name())
        data.append(self.get_group_belongs_to())
        data.append(self.get_diocesis_belongs_to())
        data.append(self.grupoAsociado.get_delegacion_name())
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
        return self

    def update_all_data_for_voluntary(self, data):

        if TipoColaboracion.objects.filter(pk__exact = data['colaboracion_id']).exists():
            tipoColaboracion_obj = TipoColaboracion.objects.get(pk__exact = data['colaboracion_id'])
        else:
            tipoColaboracion_obj = None
        if data['grupoID'] != '':
            if Grupo.objects.filter(pk__exact = data['grupoID']).exists():
                grupo_obj = Grupo.objects.filter(pk__exact = data['grupoID']).last()
            else:
                grupo_obj = None
        else:
            grupo_obj = None
        if data['rec_boletin'] == '0':
            boletin = False
            online = False
        else:
            boletin = True
            if data['rec_boletin'] == '1':
                online = True
            else:
                online = False
        if data['activo'] == 'true':
            activo = True
        else:
            activo = False
        if data['nacimiento'] != '':
            #alta = datetime.strptime(data['alta'],"%Y-%m-%d").date()
            nacimiento = data['nacimiento']
        else:
            nacimiento = None
        if data['alta'] != '':
            #alta = datetime.strptime(data['alta'],"%Y-%m-%d").date()
            alta = data['alta']
        else:
            alta = None
        if data['baja'] != '':
            baja = data['baja']
        else:
            baja = None
        if data['proyectoID'] == '':
            proyecto_obj = None
        else:
            if Proyecto.objects.filter(pk__exact = data['proyectoID']).exists():
                proyecto_obj = Proyecto.objects.filter(pk__exact = data['proyectoID']).last()
            else:
                proyecto_obj = None
        if data['actividadID'] == '':
            actividad_obj = None
        else:
            if Actividad.objects.filter(pk__exact = data['actividadID']).exists():
                actividad_obj = Actividad.objects.filter(pk__exact = data['actividadID']).last()
            else:
                actividad_obj = None
        self.nombre = data['nombre']
        self.apellido = data['apellidos']
        self.calle = data['calle']
        self.poblacion = data['poblacion']
        self.provincia = data['provincia']
        self.codigoPostal = data['codigo']
        self.DNI = data['dni']
        self.fechaNacimiento = nacimiento
        self.fechaAlta = alta
        self.fechaBaja = baja
        self.email = data['email']
        self.telefonoFijo = data['fijo']
        self.telefonoMovil = data['movil']
        self.tipoColaboracion = tipoColaboracion_obj
        self.grupoAsociado = grupo_obj
        self.recibirBoletin = boletin
        self.boletinOnline = online
        self.proyectoAsociado = proyecto_obj
        self.actividadAsociada = actividad_obj
        self.personalActivo = activo
        self.save()
        return self

    objects = PersonalExternoManager()


class PersonalManager(models.Manager):
    def create_new_personel(self, data):
        if data['nacimiento'] == '':
            data['nacimiento'] = None
        if data['rec_boletin'] == '0':
            boletin = False
            online = False
        else:
            boletin = True
            if data['rec_boletin'] == "1":
                online = True
            else:
                online = False
        new_personel = self.create(nombre = data['nombre'], apellido = data['apellido'],
                DNI = data['nif'], email = data['email'], telefonoFijo = data['fijo'],
                telefonoMovil = data['movil'],calle = data['calle'],
                poblacion = data['poblacion'], provincia = data['provincia'],
                codigoPostal = data['codigo'],fechaNacimiento = data['nacimiento'],
                recibirBoletin = boletin, boletinOnline = online)
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
    diocesis = models.ForeignKey(
                        Diocesis,
                        on_delete=models.CASCADE, null=True, blank = True)
    nombre = models.CharField(max_length=40,null=True, blank = True)
    apellido = models.CharField(max_length=40,null=True, blank = True)
    DNI = models.CharField(max_length=20, null=True, blank = True)
    calle = models.CharField(max_length=80, null=True, blank = True)
    poblacion = models.CharField(max_length=60, null=True, blank = True)
    provincia = models.CharField(max_length=40, null=True, blank = True)
    codigoPostal = models.CharField(max_length=20, null=True, blank = True)
    email = models.CharField(max_length=40, null=True, blank = True)
    telefonoFijo = models.CharField(max_length=20, null=True, blank = True)
    telefonoMovil = models.CharField(max_length=40, null=True, blank = True)
    fechaNacimiento = models.DateField(auto_now = False, null=True, blank = True)
    fechaAlta = models.DateField(auto_now = False, null=True, blank = True)
    fechaBaja = models.DateField(auto_now = False, null=True, blank = True)
    personalActivo = models.BooleanField(default= True)
    recibirBoletin = models.BooleanField(default= False)
    boletinOnline = models.BooleanField(default= False)
    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    def __str__ (self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_id(self):
        return '%s' %(self.pk)

    def get_personal_name(self):
        return '%s %s' %(self.nombre, self.apellido)

    def get_personal_location(self):
        return '%s' %(self.poblacion)

    def get_delegacion_belongs_to(self):
        if self.delegacion :
            return '%s' %(self.delegacion.get_delegacion_name())
        return ''

    def get_delegacion_id_belongs_to(self):
        if self.delegacion :
            return '%s' %(self.delegacion.get_delegacion_id())
        return ''

    def get_diocesis_belongs_to(self):
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

    def get_movil_number(self):
        if self.telefonoMovil:
            return '%s' %(self.telefonoMovil)
        else:
            return ''

    def get_email(self):
        if self.email:
            return '%s' %(self.email)
        else:
            return ''

    def get_all_data_from_personal(self):
        if self.fechaAlta is None:
            alta = ''
        else:
            alta = self.fechaAlta.strftime("%Y-%m-%d")
        if self.fechaBaja is None:
            baja = ''
        else:
            baja = self.fechaBaja.strftime("%B %d, %Y")
        if self.personalActivo:
            activo = 'true'
        else:
            activo = 'false'
        if self.recibirBoletin:
            boletin = 'true'
        else:
            boletin = 'false'
        if self.boletinOnline:
            online = "true"
        else:
            online = "false"
        if self.personalActivo:
            activo = 'true'
        else:
            activo = 'false'
        if boletin == 'true':
            if online == 'true':
                rec_boletin = '1'
            else:
                rec_boletin = '2'
        else:
            rec_boletin = "0"
        data = {}
        data['user_id'] = self.pk
        data['nombre'] = self.nombre
        data['apellido'] = self.apellido
        data['dni'] = self.DNI
        data['email'] = self.email
        data['fijo'] = self.telefonoFijo
        data['movil'] = self.telefonoMovil
        data['baja'] = baja
        #data['alta'] = alta
        data['calle'] = self.calle
        data['poblacion'] = self.poblacion
        data['provincia'] = self.provincia
        data['codigo'] = self.codigoPostal
        data['boletin'] = boletin
        data['observaciones'] = self.observaciones
        #data['diocesis'] = diocesis
        data['activo'] = activo
        data['online'] = online
        data['rec_boletin'] = rec_boletin
        return data

    def get_data_for_boletin(self):
        data = []
        data.append(self.nombre)
        data.append(self.apellido)
        data.append('Personal Iglesia')
        data.append(self.calle)
        data.append(self.poblacion)
        data.append(self.provincia)
        data.append(self.codigoPostal)
        return data

    def get_data_for_online_boletin(self):
        data = []
        data.append(self.nombre)
        data.append(self.apellido)
        data.append('Personal Iglesia')
        data.append(self.email)
        return data

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
        '''
        if data['diocesis'] != '':
            try:
                diocesis_obj = Diocesis.objects.get(pk__exact = data['diocesis'])
            except:
                diocesis_obj = None
        else:
            diocesis_obj = None
        '''
        if data['cargo'] != '':
            try:
                cargo_obj = Cargo.objects.get(pk__exact = data['cargo'])
            except:
                cargo_obj = None
        else:
            cargo_obj = None

        self.grupoAsociado = grupo_obj
        self.delegacion = delegacion_obj
        #self.diocesis = diocesis_obj
        self.cargo = cargo_obj
        self.save()
        return self


    def update_all_data_for_personal(self, data):
        if data['rec_boletin'] == '0':
            boletin = False
            online = False
        else:
            boletin = True
            if data['rec_boletin'] == '1':
                online = True
            else:
                online = False
        if data['activo'] == 'true':
            activo = True
        else:
            activo = False

        if data['baja'] != '':
            baja = data['baja']
        else:
            baja = None
        if data['nacimiento'] != '':
            #alta = datetime.strptime(data['alta'],"%Y-%m-%d").date()
            nacimiento = data['nacimiento']
        else:
            nacimiento = None
        if data['activo'] == 'false':
            activo = False
        else:
            activo = True
        self.nombre = data['nombre']
        self.apellido = data['apellidos']
        self.calle = data['calle']
        self.poblacion = data['poblacion']
        self.provincia = data['provincia']
        self.codigoPostal = data['codigo']
        self.DNI = data['dni']
        self.fechaNacimiento = nacimiento
        self.fechaBaja = baja
        self.email = data['email']
        self.telefonoFijo = data['fijo']
        self.telefonoMovil = data['movil']
        self.recibirBoletin = boletin
        self.boletinOnline = online
        self.personalActivo = activo
        self.save()
        return self


    objects = PersonalManager()
