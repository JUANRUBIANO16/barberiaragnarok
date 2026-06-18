from django.db import models


class Usuario(models.Model):
    TIPO_USUARIO = [
        ('admin', 'Admin'),
        ('barbero', 'Barbero'),
        ('cliente', 'Cliente'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)

    # ✅ PARA CONTROL DE LOGIN
    last_login = models.DateTimeField(null=True, blank=True)

    # ✅ TOKEN RECUPERAR PASSWORD
    reset_token = models.UUIDField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"