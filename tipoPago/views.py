from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import TipoPago
from barberia.decorators import login_required, role_required


# 🔐 LISTAR TIPOS DE PAGO (solo admin)
@login_required
@role_required('admin')
def tipoPago(request):
    tipopagos = TipoPago.objects.all()

    return render(request, 'tipoPago.html', {
        'tipoPago': tipopagos
    })


# 🔐 CREAR (solo admin)
@login_required
@role_required('admin')
def crearTipoPago(request):
    if request.method == 'POST':
        metodo = request.POST.get('metodo')

        if metodo:
            TipoPago.objects.create(metodo=metodo)
            messages.success(request, "Tipo de pago creado correctamente")

    return redirect('tipoPago')


# 🔐 EDITAR (solo admin)
@login_required
@role_required('admin')
def editarTipoPago(request, id):
    tipopago = get_object_or_404(TipoPago, id=id)

    if request.method == 'POST':
        metodo = request.POST.get('metodo')

        if metodo:
            tipopago.metodo = metodo
            tipopago.save()
            messages.success(request, "Tipo de pago actualizado correctamente")

    return redirect('tipoPago')


# 🔐 ELIMINAR (solo admin)
@login_required
@role_required('admin')
def eliminarTipoPago(request, id):
    tipopago = get_object_or_404(TipoPago, id=id)

    if request.method == 'POST':
        tipopago.delete()
        messages.success(request, "Tipo de pago eliminado correctamente")

    return redirect('tipoPago')