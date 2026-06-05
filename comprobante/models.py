
from django.db import models
from tipoPago.models import TipoPago
from ventas.models import Venta


class Comprobante(models.Model):

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    

    tipo_pago = models.ForeignKey(
    TipoPago,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante {self.id}"