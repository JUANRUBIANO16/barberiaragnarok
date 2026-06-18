from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.contrib.auth.hashers import make_password

from Servicios.models import Servicio
from comprobante.models import Comprobante
from usuarios.models import Usuario
from ventas.models import Venta
from citas.models import Cita
from barberia.decorators import login_required


@login_required
def dashboard(request):
    user_id = int(request.session.get('user_id'))
    rol = request.session.get('user_rol')

    # ===================== VARIABLES GENERALES =====================
    total_usuarios = 0
    total_servicios = Servicio.objects.count()
    total_comprobantes = 0
    ventas_totales = 0
    dinero_total = 0

    mis_citas_hoy = 0
    mis_ventas_hoy = 0
    mi_total_mes = 0

    # 🔥 CLIENTE (NUEVO)
    citas_pendientes = 0
    citas_confirmadas = 0
    citas_canceladas = 0

    hoy = timezone.localdate()
    ahora = timezone.now()

    # ===================== ADMIN =====================
    if rol == 'admin':
        ventas_qs = Venta.objects.all()
        citas_qs = Cita.objects.all()

        total_usuarios = Usuario.objects.count()
        total_comprobantes = Comprobante.objects.count()
        ventas_totales = ventas_qs.count()
        dinero_total = ventas_qs.aggregate(total=Sum('total'))['total'] or 0

        ventas_por_dia = (
            ventas_qs
            .annotate(dia=TruncDay('fecha'))
            .values('dia')
            .annotate(total_dia=Sum('total'))
            .order_by('dia')
        )

        labels_dia = [v['dia'].strftime("%d %b") for v in ventas_por_dia]
        data_dia = [float(v['total_dia']) for v in ventas_por_dia]

        total_subtotal = ventas_qs.aggregate(s=Sum('subtotal'))['s'] or 0
        total_descuento = ventas_qs.aggregate(d=Sum('descuento'))['d'] or 0

        labels_metodo = ['Subtotal', 'Descuentos', 'Total']
        data_metodo = [
            float(total_subtotal),
            float(total_descuento),
            float(dinero_total)
        ]

    # ===================== BARBERO =====================
    elif rol == 'barbero':
        citas_qs = Cita.objects.filter(barbero_id=user_id)

        ventas_qs = Venta.objects.filter(
            cita_id__in=citas_qs.values_list('id', flat=True)
        )

        total_comprobantes = Comprobante.objects.filter(
            venta_id__in=ventas_qs.values_list('id', flat=True)
        ).count()

        mis_citas_hoy = citas_qs.filter(fecha=hoy).count()
        mis_ventas_hoy = ventas_qs.filter(fecha__date=hoy).count()

        mi_total_mes = ventas_qs.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month
        ).aggregate(total=Sum('total'))['total'] or 0

        ventas_totales = mis_ventas_hoy
        dinero_total = mi_total_mes

        ventas_por_dia = (
            ventas_qs
            .annotate(dia=TruncDay('fecha'))
            .values('dia')
            .annotate(total_dia=Sum('total'))
            .order_by('dia')
        )

        labels_dia = [v['dia'].strftime("%d %b") for v in ventas_por_dia]
        data_dia = [float(v['total_dia']) for v in ventas_por_dia]

        servicios_realizados = (
            ventas_qs
            .values('cita__servicio__nombre')
            .annotate(total_servicios=Count('id'))
            .order_by('-total_servicios')
        )

        labels_metodo = [s['cita__servicio__nombre'] for s in servicios_realizados]
        data_metodo = [s['total_servicios'] for s in servicios_realizados]

    # ===================== CLIENTE 🔥 (NUEVO) =====================
    elif rol == 'cliente':

        citas_qs = Cita.objects.filter(cliente_id=user_id)

        citas_pendientes = citas_qs.filter(estado='pendiente').count()
        citas_confirmadas = citas_qs.filter(estado='confirmada').count()
        citas_canceladas = citas_qs.filter(estado='cancelada').count()

        ventas_qs = Venta.objects.none()

        labels_dia = []
        data_dia = []
        labels_metodo = []
        data_metodo = []

    # ===================== OTROS =====================
    else:
        ventas_qs = Venta.objects.none()
        citas_qs = Cita.objects.none()
        labels_dia = []
        data_dia = []
        labels_metodo = []
        data_metodo = []

    return render(request, "administrador/dashboard.html", {
        'total_usuarios': total_usuarios,
        'total_servicios': total_servicios,
        'ventas_totales': ventas_totales,
        'dinero_total': dinero_total,
        'total_comprobantes': total_comprobantes,

        'mis_citas_hoy': mis_citas_hoy,
        'mis_ventas_hoy': mis_ventas_hoy,
        'mi_total_mes': mi_total_mes,

        # 🔥 CLIENTE
        'citas_pendientes': citas_pendientes,
        'citas_confirmadas': citas_confirmadas,
        'citas_canceladas': citas_canceladas,

        'labels_dia': labels_dia,
        'data_dia': data_dia,
        'labels_metodo': labels_metodo,
        'data_metodo': data_metodo
    })


@login_required
def perfil(request):
    user_id = request.session.get('user_id')
    usuario = Usuario.objects.get(id=user_id)

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.email = request.POST.get('email')

        password = request.POST.get('password')
        if password:
            usuario.password = make_password(password)

        if 'foto' in request.FILES:
            usuario.foto = request.FILES['foto']

        usuario.save()
        return redirect('perfil')

    return render(request, 'administrador/perfil.html', {
        'usuario': usuario
    })