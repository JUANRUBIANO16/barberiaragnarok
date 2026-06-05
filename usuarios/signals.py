from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.db import connection
from .models import Usuario


@receiver(post_migrate)
def crear_admin_por_defecto(sender, **kwargs):
    # revisar si la tabla ya existe
    tablas = connection.introspection.table_names()

    if "usuarios_usuario" not in tablas:
        return

    #  crear admin solo si no existe
    if not Usuario.objects.filter(email="admin@gmail.com").exists():
        Usuario.objects.create(
            nombre="Administrador",
            email="admin@gmail.com",
            password=make_password("admin123"),
            tipo_usuario="admin"
        )
        print(" Admin creado correctamente")