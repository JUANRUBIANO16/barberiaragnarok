from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ventas.models import Venta
from citas.models import Cita
from barberia.decorators import login_required


# 🔥 DESCUENTO ESCALONADO
def calcular_descuento(subtotal):
    if subtotal >= Decimal('150000'):
        return subtotal * Decimal('0.15')
    elif subtotal >= Decimal('100000'):
        return subtotal * Decimal('0.10')
    elif subtotal >= Decimal('50000'):
        return subtotal * Decimal('0.05')
    return Decimal('0')


# 🔥 SUBTOTAL DESDE SERVICIO
def obtener_subtotal(cita):
    return Decimal(cita.servicio.precio)


@login_required
def ventas(request):
    user_id = int(request.session.get('user_id'))
    rol = request.session.get('user_rol')

    if rol == 'admin':
        ventas_qs = Venta.objects.all()
        citas = Cita.objects.all()
    else:
        citas_barbero = Cita.objects.filter(barbero_id=user_id)
        ventas_qs = Venta.objects.filter(
            cita_id__in=citas_barbero.values_list('id', flat=True)
        )
        citas = citas_barbero

    return render(request, 'ventas.html', {
        'ventas': ventas_qs,
        'citas': citas,
        'ventas_totales': ventas_qs.count()
    })


@login_required
def crearVenta(request):
    if request.method == 'POST':
        try:
            cita_id = request.POST.get('cita')
            cita = get_object_or_404(Cita, id=cita_id)

            # 🔥 subtotal automático
            subtotal = obtener_subtotal(cita)

            descuento = calcular_descuento(subtotal)
            total = subtotal - descuento

            Venta.objects.create(
                cita=cita,
                subtotal=subtotal,
                descuento=descuento,
                total=total
            )

            messages.success(request, "Venta registrada correctamente")

        except Exception:
            messages.error(request, "Error al generar la venta")

    return redirect('ventas')


@login_required
def venta_edit(request, id):
    venta = get_object_or_404(Venta, id=id)

    if request.method == 'POST':
        try:
            cita_id = request.POST.get('cita')
            cita = get_object_or_404(Cita, id=cita_id)

            subtotal = obtener_subtotal(cita)
            descuento = calcular_descuento(subtotal)

            venta.cita = cita
            venta.subtotal = subtotal
            venta.descuento = descuento
            venta.total = subtotal - descuento
            venta.save()

            messages.success(request, "Venta actualizada correctamente")

        except Exception:
            messages.error(request, "Error al actualizar la venta")

    return redirect('ventas')


@login_required
def venta_delete(request, id):
    venta = get_object_or_404(Venta, id=id)
    venta.delete()
    messages.success(request, "Venta eliminada correctamente")

    return redirect('ventas')