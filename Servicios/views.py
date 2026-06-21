from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.deletion import ProtectedError
from decimal import Decimal, InvalidOperation

from Servicios.models import Servicio
from barberia.decorators import login_required, role_required

MAX_PRECIO = Decimal('99999999.99')


# =========================
# VALIDACIÓN DE PRECIO
# =========================
def validar_precio(valor):
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


# =========================
# LISTAR SERVICIOS (TODOS)
# =========================
@login_required
def lista_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicios.html', {'servicios': servicios})
# =========================
# CREAR SERVICIO (SOLO ADMIN)
# =========================
@login_required
@role_required('admin')
def crear_servicio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')

        precio = validar_precio(precio_raw)

        if precio is None:
            messages.error(request, 'Precio inválido')
            return redirect('listar_servicios')

        Servicio.objects.create(
            nombre=nombre,
            precio=precio,
            descripcion=descripcion,
            imagen=imagen
        )

        messages.success(request, 'Servicio creado correctamente')
        return redirect('listar_servicios')

    return render(request, 'crear_servicio.html')


# =========================
# EDITAR SERVICIO (SOLO ADMIN)
# =========================
@login_required
@role_required('admin')
def servicio_edit(request, id):
    servicio = get_object_or_404(Servicio, id=id)

    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')

        precio = validar_precio(request.POST.get('precio'))
        if precio:
            servicio.precio = precio
        else:
            messages.error(request, 'Precio inválido, no se actualizó')

        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']

        servicio.save()
        messages.success(request, 'Servicio actualizado correctamente')

    return redirect('listar_servicios')


# =========================
# ELIMINAR SERVICIO (SOLO ADMIN)
# =========================
@login_required
@role_required('admin')
def servicio_delete(request, id):
    servicio = get_object_or_404(Servicio, id=id)

    try:
        servicio.delete()
        messages.success(request, 'Servicio eliminado correctamente')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: tiene citas asociadas')

    return redirect('listar_servicios')