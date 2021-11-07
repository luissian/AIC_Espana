from django.db import models
from django.contrib.auth.models import User

class ActividadManager(models.Manager):
    def create_actividad(self,data):

        return new_actividad

class Actividad(models.Model):
    activity_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def __str__ (self):
        return '%s' %(self.activity_name)
