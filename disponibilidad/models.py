from django.db import models
from usuarios.models import Usuario

class Disponibilidad(models.Model):

    DIAS_SEMANA = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    barbero = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'barbero'}
    )

    dia_semana = models.IntegerField(choices=DIAS_SEMANA)

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.barbero.nombre} - {self.get_dia_semana_display()} ({self.hora_inicio} - {self.hora_fin})"
