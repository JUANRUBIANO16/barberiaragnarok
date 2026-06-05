from django.db import models
from Servicios.models import Servicio
from usuarios.models import Usuario

class Cita(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')

    barbero = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        related_name='citas_barbero'
    )

    cliente = models.ForeignKey(
    Usuario, 
    on_delete=models.PROTECT, 
    related_name='citas_cliente',
    null=True,
    blank=True
)

    servicio = models.ForeignKey(
        Servicio, 
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Cita {self.id} - {self.fecha}"