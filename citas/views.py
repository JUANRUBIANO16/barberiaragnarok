from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, time, date, timedelta
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from twilio.rest import Client
from citas.models import Cita
from Servicios.models import Servicio
from usuarios.models import Usuario
from disponibilidad.models import Disponibilidad
from barberia.decorators import login_required
from django.db.models import Count, Sum
from barberia.decorators import role_required

def validar_fecha_hora(fecha, hora):
    if not fecha or not hora:
        return "Fecha y hora obligatorias"

    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
        h = datetime.strptime(hora, "%H:%M").time()
    except ValueError:
        return "Formato inválido"

    ahora = datetime.now()
    fecha_hora = datetime.combine(f, h)

    # 🔥 VALIDACIÓN REAL
    if fecha_hora < ahora:
        return "No puedes agendar en el pasado"

    return None

@login_required
def citas(request):
    return render(request, "citas/citas.html", {
        "citas": Cita.objects.all(),
        "barberos": Usuario.objects.filter(tipo_usuario='barbero'),
        "clientes": Usuario.objects.filter(tipo_usuario='cliente'),
        "servicios": Servicio.objects.all(),
        "estados": Cita.ESTADOS
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, time, date, timedelta
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from twilio.rest import Client
from citas.models import Cita
from Servicios.models import Servicio
from usuarios.models import Usuario
from disponibilidad.models import Disponibilidad
from barberia.decorators import login_required
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa


def validar_fecha_hora(fecha, hora):
    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
        h = datetime.strptime(hora, "%H:%M").time()
    except:
        return "Fecha u hora inválida"

    hoy = date.today()

    if f < hoy:
        return "No puedes agendar en el pasado"

    if f.weekday() == 6:
        return "No domingos"

    return None


@login_required
def citas(request):
    return render(request, "citas/citas.html", {
        "citas": Cita.objects.all(),
        "barberos": Usuario.objects.filter(tipo_usuario='barbero'),
        "clientes": Usuario.objects.filter(tipo_usuario='cliente'),
        "servicios": Servicio.objects.all(),
        "estados": Cita.ESTADOS
    })


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


@login_required
def cita_delete(request, id):
    cita = get_object_or_404(Cita, id=id)

    try:
        cita.delete()
        messages.success(request, "Cita eliminada")
    except ProtectedError:
        messages.error(request, "No se puede eliminar")

    return redirect('citas')


#  AJAX HORAS REALES
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


@login_required
def cita_delete(request, id):
    cita = get_object_or_404(Cita, id=id)

    try:
        cita.delete()
        messages.success(request, "Cita eliminada")
    except ProtectedError:
        messages.error(request, "No se puede eliminar")

    return redirect('citas')


#  AJAX HORAS REALES
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




def reporte_citas(request):
    citas = Cita.objects.select_related('barbero', 'cliente', 'servicio').all()

    # ===== FILTROS =====
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    barbero = request.GET.get('barbero')
    servicio = request.GET.get('servicio')
    estado = request.GET.get('estado')

    if fecha_inicio and fecha_fin:
        citas = citas.filter(fecha__range=[fecha_inicio, fecha_fin])

    if barbero:
        citas = citas.filter(barbero_id=barbero)

    if servicio:
        citas = citas.filter(servicio_id=servicio)

    if estado:
        citas = citas.filter(estado=estado)


    total_citas = citas.count()

    total_ingresos = citas.aggregate(
        total=Sum('servicio__precio')
    )['total'] or 0

    citas_por_barbero = citas.values('barbero__nombre').annotate(total=Count('id'))

    citas_por_servicio = citas.values('servicio__nombre').annotate(total=Count('id'))

    # ===== DATA PARA FILTROS =====
    barberos = Usuario.objects.filter(tipo_usuario='barbero')
    servicios = Servicio.objects.all()

    return render(request, 'citas/reporte_citas.html', {
        'citas': citas,
        'total_citas': total_citas,
        'total_ingresos': total_ingresos,
        'citas_por_barbero': citas_por_barbero,
        'citas_por_servicio': citas_por_servicio,
        'barberos': barberos,
        'servicios': servicios,
        'request': request
    })



def reporte_citas_pdf(request):
    citas = Cita.objects.select_related('barbero', 'cliente', 'servicio').all()

    # ===== FILTROS =====
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    barbero = request.GET.get('barbero')
    servicio = request.GET.get('servicio')
    estado = request.GET.get('estado')

    if fecha_inicio and fecha_fin:
        citas = citas.filter(fecha__range=[fecha_inicio, fecha_fin])

    if barbero:
        citas = citas.filter(barbero_id=barbero)

    if servicio:
        citas = citas.filter(servicio_id=servicio)

    if estado:
        citas = citas.filter(estado=estado)

    # ===== TOTALES =====
    total_citas = citas.count()
    total_ingresos = citas.aggregate(
        total=Sum('servicio__precio')
    )['total'] or 0

    template = get_template('citas/reporte_pdf.html')
    html = template.render({
        'citas': citas,
        'total_citas': total_citas,
        'total_ingresos': total_ingresos
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_citas.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response




from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from Servicios.models import Servicio
from .models import SolicitudCita


@login_required
def agendar_cita(request):

    # 🔵 GET → mostrar formulario
    if request.method == 'GET':
        barberos = Barbero.objects.all()
        servicios = Servicio.objects.all()

        return render(request, 'citas/agendar_cita.html', {
            'barberos': barberos,
            'servicios': servicios
        })

    # 🟢 POST → crear solicitud
    elif request.method == 'POST':

        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        servicio_id = request.POST.get('servicio')

        servicio = None
        if servicio_id:
            servicio = Servicio.objects.filter(id=servicio_id).first()

        SolicitudCita.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            mensaje=mensaje,
            servicio=servicio,
            estado='pendiente'
        )

        return JsonResponse({
            "success": True,
            "message": "Solicitud creada correctamente"
        })

    # 🔴 método no permitido
    return JsonResponse({
        "success": False,
        "error": "Método no permitido"
    })
@login_required
def mis_citas(request):
    user_id = request.session.get('user_id')

    citas = Cita.objects.filter(
        cliente_id=user_id
    ).select_related(
        'barbero',
        'servicio'
    ).order_by('-fecha', '-hora')

    return render(request, 'citas/mis_citas.html', {
        'citas': citas
    })

@login_required
def historial_citas(request):

    user_id = request.session.get('user_id')

    citas = Cita.objects.filter(
        cliente_id=user_id
    ).select_related(
        'barbero',
        'servicio'
    ).order_by('-fecha')

    return render(
        request,
        'citas/historial_citas.html',
        {'citas': citas}
    )