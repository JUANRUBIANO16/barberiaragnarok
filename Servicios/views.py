from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from Servicios.models import Servicio
from decimal import Decimal, InvalidOperation
from barberia.decorators import login_required, role_required

from django.db.models.deletion import ProtectedError

MAX_PRECIO = Decimal('99999999.99')

def validar_precio(valor):
    """
    Convierte un valor a Decimal válido:
    - permite coma o punto como separador decimal
    - asegura 2 decimales
    """
    if not valor:
        return None
    try:
        valor = str(valor).replace(',', '.')
        precio = Decimal(valor)
    except (InvalidOperation, TypeError):
        return None

    if precio < 0 or precio > MAX_PRECIO:
        return None

    return precio.quantize(Decimal('0.00'))


@login_required
def lista_servicios(request):
    """
    Lista todos los servicios.
    """
    servicios = Servicio.objects.all()
    return render(request, 'servicios.html', {'servicios': servicios})


def Crear_servicio(request):
    """
    Crear un servicio nuevo, validando el precio.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')

        precio = validar_precio(precio_raw)
        if precio is None:
            precio = Decimal('0.00')
            messages.error(request, 'Precio inválido. Se estableció en 0.00')

        Servicio.objects.create(
            nombre=nombre,
            precio=precio,
            descripcion=descripcion,
            imagen=imagen
        )
        messages.success(request, 'Servicio creado correctamente')
        return redirect('listar_servicios')


def servicio_edit(request, id):
    """
    Editar un servicio existente, actualizar precio y foto.
    """
    servicio = get_object_or_404(Servicio, id=id)

    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio')
        descripcion = request.POST.get('descripcion')

        precio = validar_precio(precio_raw)
        if precio is not None:
            servicio.precio = precio
        else:
            messages.error(request, 'Precio inválido. No se actualizó el precio')

        servicio.descripcion = descripcion

        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']

        servicio.save()
        messages.success(request, 'Servicio actualizado correctamente')

    return redirect('listar_servicios')


def servicio_delete(request, id):
    servicio = get_object_or_404(Servicio, id=id)

    try:
        servicio.delete()
        messages.success(request, 'Servicio eliminado correctamente')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar el servicio porque tiene citas asociadas')

    return redirect('listar_servicios')