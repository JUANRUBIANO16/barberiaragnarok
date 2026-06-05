from django.db import models
from citas.models import Cita

class Venta(models.Model):

    cita = models.ForeignKey(
        Cita,
        on_delete=models.PROTECT
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id}"