from urllib import request
from django.contrib import messages

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from comprobante.models import Comprobante
from tipoPago.models import TipoPago
from ventas.models import Venta
from barberia.decorators import login_required, role_required
from django.template.loader import get_template
from xhtml2pdf import pisa

@login_required
def comprobante(request):
    """
    Listar todos los comprobantes.
    """
    comprobantes = Comprobante.objects.select_related('venta', 'tipo_pago').all()
    ventas = Venta.objects.all()
    tipo_pagos = TipoPago.objects.all()

    return render(request, 'comprobante.html', {
        'comprobantes': comprobantes,
        'ventas': ventas,
        'tipo_pagos': tipo_pagos
    })


@login_required
def crearComprobante(request):
    """
    Crear un comprobante nuevo.
    """
    if request.method == 'POST':
        venta_id = request.POST.get('venta')
        tipo_pago_id = request.POST.get('tipo_pago')

        venta = get_object_or_404(Venta, id=venta_id)
        tipo_pago = get_object_or_404(TipoPago, id=tipo_pago_id)

        Comprobante.objects.create(
            venta=venta,
            tipo_pago=tipo_pago,
            monto=venta.total  # monto automático
        )
    messages.success(request, "Comprobante creado correctamente")
    return redirect('comprobantes')


@login_required
def comprobante_edit(request, id):
    """
    Editar un comprobante existente.
    """
    comprobante = get_object_or_404(Comprobante, id=id)

    if request.method == 'POST':
        venta_id = request.POST.get('venta')
        tipo_pago_id = request.POST.get('tipo_pago')

        comprobante.venta = get_object_or_404(Venta, id=venta_id)
        comprobante.tipo_pago = get_object_or_404(TipoPago, id=tipo_pago_id)
        comprobante.monto = comprobante.venta.total  # recalcular monto
        comprobante.save()

    messages.success(request, "Comprobante actualizado correctamente")
    return redirect('comprobantes')


@login_required
def comprobante_delete(request, id):
    """
    Eliminar un comprobante.
    """
    comprobante = get_object_or_404(Comprobante, id=id)
    comprobante.delete()
    messages.success(request, "Comprobante eliminado correctamente")
    return redirect('comprobantes')


@login_required
def generar_pdf_comprobantes(request, id=None):

    queryset = Comprobante.objects.select_related(
        'venta__cita__cliente',
        'venta__cita__barbero',
        'tipo_pago'
    )

    if id:
        comprobante = get_object_or_404(queryset, id=id)
        comprobantes = [comprobante]
        filename = f'comprobante_{id}.pdf'
    else:
        comprobantes = queryset
        filename = 'comprobantes.pdf'

    template = get_template('comprobantes_pdf.html')
    html = template.render({'comprobantes': comprobantes})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar PDF <pre>' + html + '</pre>')

    return response