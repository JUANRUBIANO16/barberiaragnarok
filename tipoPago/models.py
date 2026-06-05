from django.db import models

class TipoPago(models.Model):

    metodo = models.CharField(max_length=100)

    def __str__(self):
        return self.metodo
