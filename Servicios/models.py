
from django.db import models

class Servicio(models.Model):

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
    def __str__(self):
        return self.nombre