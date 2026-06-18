from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Count, Sum
from django.template.loader import get_template
from django.db.models.deletion import ProtectedError

from datetime import datetime, date, timedelta

from citas.models import Cita, SolicitudCita
from Servicios.models import Servicio
from usuarios.models import Usuario
from disponibilidad.models import Disponibilidad

from xhtml2pdf import pisa

from barberia.decorators import login_required


# =========================
# VALIDACIÓN
# =========================
def validar_fecha_hora(fecha, hora):
    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
        h = datetime.strptime(hora, "%H:%M").time()
    except:
        return "Fecha u hora inválida"

    if f < date.today():
        return "No puedes agendar en el pasado"

    if f.weekday() == 6:
        return "No domingos"

    return None


# =========================
# LISTAR CITAS
# =========================
@login_required
def citas(request):
    return render(request, "citas/citas.html", {
        "citas": Cita.objects.all(),
        "barberos": Usuario.objects.filter(tipo_usuario='barbero'),
        "clientes": Usuario.objects.filter(tipo_usuario='cliente'),
        "servicios": Servicio.objects.all(),
        "estados": Cita.ESTADOS
    })


# =========================
# CREAR CITA
# =========================
@login_required
def crearCita(request):
    if request.method == "POST":

        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        error = validar_fecha_hora(fecha, hora)
        if error:
            messages.error(request, error)
            return redirect('citas')

        barbero = Usuario.objects.get(id=request.POST['barbero'])
        cliente = Usuario.objects.get(id=request.POST['cliente'])
        servicio = Servicio.objects.get(id=request.POST['servicio'])

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        dia_semana = fecha_obj.weekday()

        disponible = Disponibilidad.objects.filter(
            barbero=barbero,
            dia_semana=dia_semana,
            hora_inicio__lte=hora_obj,
            hora_fin__gt=hora_obj
        ).exists()

        if not disponible:
            messages.error(request, "El barbero no trabaja en ese horario")
            return redirect('citas')

        if Cita.objects.filter(fecha=fecha, hora=hora, barbero=barbero).exists():
            messages.error(request, "Ya existe esa cita")
            return redirect('citas')

        Cita.objects.create(
            fecha=fecha,
            hora=hora,
            estado=request.POST['estado'],
            barbero=barbero,
            cliente=cliente,
            servicio=servicio
        )

        messages.success(request, "Cita creada correctamente")

    return redirect('citas')


# =========================
# EDITAR CITA
# =========================
@login_required
def cita_edit(request, id):
    cita = get_object_or_404(Cita, id=id)

    if request.method == "POST":

        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        error = validar_fecha_hora(fecha, hora)
        if error:
            messages.error(request, error)
            return redirect('citas')

        barbero = Usuario.objects.get(id=request.POST['barbero'])
        cliente = Usuario.objects.get(id=request.POST['cliente'])
        servicio = Servicio.objects.get(id=request.POST['servicio'])

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        dia_semana = fecha_obj.weekday()

        disponible = Disponibilidad.objects.filter(
            barbero=barbero,
            dia_semana=dia_semana,
            hora_inicio__lte=hora_obj,
            hora_fin__gt=hora_obj
        ).exists()

        if not disponible:
            messages.error(request, "El barbero no trabaja en ese horario")
            return redirect('citas')

        if Cita.objects.filter(
            fecha=fecha,
            hora=hora,
            barbero=barbero
        ).exclude(id=id).exists():
            messages.error(request, "Conflicto de horario")
            return redirect('citas')

        cita.fecha = fecha
        cita.hora = hora
        cita.estado = request.POST['estado']
        cita.barbero = barbero
        cita.cliente = cliente
        cita.servicio = servicio
        cita.save()

        messages.success(request, "Cita actualizada")

    return redirect('citas')


# =========================
# ELIMINAR CITA
# =========================
@login_required
def cita_delete(request, id):
    cita = get_object_or_404(Cita, id=id)

    try:
        cita.delete()
        messages.success(request, "Cita eliminada")
    except ProtectedError:
        messages.error(request, "No se puede eliminar")

    return redirect('citas')


# =========================
# HORAS DISPONIBLES (AJAX)
# =========================
@login_required
def obtener_horas_disponibles(request):
    barbero_id = request.GET.get('barbero')
    fecha = request.GET.get('fecha')

    if not barbero_id or not fecha:
        return JsonResponse({'horas': []})

    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
    dia_semana = fecha_obj.weekday()

    disponibilidad = Disponibilidad.objects.filter(
        barbero_id=barbero_id,
        dia_semana=dia_semana
    )

    horas = []

    for d in disponibilidad:
        inicio = datetime.combine(fecha_obj, d.hora_inicio)
        fin = datetime.combine(fecha_obj, d.hora_fin)

        while inicio < fin:
            hora_str = inicio.strftime("%H:%M")

            ocupado = Cita.objects.filter(
                barbero_id=barbero_id,
                fecha=fecha,
                hora=hora_str
            ).exists()

            if not ocupado:
                horas.append(hora_str)

            inicio += timedelta(minutes=30)

    return JsonResponse({'horas': horas})


# =========================
# REPORTE PDF
# =========================
@login_required
def reporte_citas_pdf(request):
    citas = Cita.objects.select_related('barbero', 'cliente', 'servicio').all()

    template = get_template('citas/reporte_pdf.html')
    html = template.render({'citas': citas})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_citas.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


# =========================
# AGENDAR SOLICITUD (SIN BARBERO MODELO)
# =========================
@login_required
def agendar_cita(request):

    if request.method == 'GET':
        barberos = Usuario.objects.filter(tipo_usuario='barbero')
        servicios = Servicio.objects.all()

        return render(request, 'citas/agendar_cita.html', {
            'barberos': barberos,
            'servicios': servicios
        })

    elif request.method == 'POST':

        SolicitudCita.objects.create(
            nombre=request.POST.get('nombre'),
            telefono=request.POST.get('telefono'),
            email=request.POST.get('email'),
            mensaje=request.POST.get('mensaje'),
            servicio_id=request.POST.get('servicio') or None,
            estado='pendiente'
        )

        return JsonResponse({"success": True})


# =========================
# MIS CITAS
# =========================
@login_required
def mis_citas(request):
    user_id = request.session.get('user_id')

    citas = Cita.objects.filter(
        cliente_id=user_id
    ).select_related('barbero', 'servicio').order_by('-fecha')

    return render(request, 'citas/mis_citas.html', {'citas': citas})


# =========================
# HISTORIAL
# =========================
@login_required
def historial_citas(request):
    user_id = request.session.get('user_id')

    citas = Cita.objects.filter(
        cliente_id=user_id
    ).select_related('barbero', 'servicio').order_by('-fecha')

    return render(request, 'citas/historial_citas.html', {'citas': citas})