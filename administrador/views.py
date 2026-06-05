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

    # inicializo variables generales
    total_usuarios = 0
    total_servicios = Servicio.objects.count()
    total_comprobantes = 0
    ventas_totales = 0
    dinero_total = 0

    # variables específicas del barbero
    mis_citas_hoy = 0
    mis_ventas_hoy = 0
    mi_total_mes = 0

    # fecha actual para filtrar citas y ventas
    hoy = timezone.localdate()  # para DateField
    ahora = timezone.now()      # para DateTimeField

    # ===================== ADMIN =====================
    if rol == 'admin':
        ventas_qs = Venta.objects.all()
        citas_qs = Cita.objects.all()

        total_usuarios = Usuario.objects.count()
        total_comprobantes = Comprobante.objects.count()
        ventas_totales = ventas_qs.count()
        dinero_total = ventas_qs.aggregate(total=Sum('total'))['total'] or 0

        # gráfico de flujo mensual
        ventas_por_dia = (
            ventas_qs
            .annotate(dia=TruncDay('fecha'))
            .values('dia')
            .annotate(total_dia=Sum('total'))
            .order_by('dia')
        )
        labels_dia = [v['dia'].strftime("%d %b") for v in ventas_por_dia]
        data_dia = [float(v['total_dia']) for v in ventas_por_dia]

        # gráfico de métodos de pago (Subtotal, Descuento, Total)
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
        # todas las citas del barbero
        citas_qs = Cita.objects.filter(barbero_id=user_id)

        # todas las ventas asociadas a esas citas
        ventas_qs = Venta.objects.filter(
            cita_id__in=citas_qs.values_list('id', flat=True)
        )

        # total de comprobantes asociados a las ventas del barbero
        total_comprobantes = Comprobante.objects.filter(
            venta_id__in=ventas_qs.values_list('id', flat=True)
        ).count()

        # contar citas de hoy
        mis_citas_hoy = citas_qs.filter(fecha=hoy).count()

        # contar ventas de hoy
        mis_ventas_hoy = ventas_qs.filter(fecha__date=hoy).count()

        # total de ventas del mes
        mi_total_mes = ventas_qs.filter(
            fecha__year=ahora.year,
            fecha__month=ahora.month
        ).aggregate(total=Sum('total'))['total'] or 0

        # asignar totales para dashboard
        ventas_totales = mis_ventas_hoy
        dinero_total = mi_total_mes

        # gráfico de flujo mensual (solo ventas del barbero)
        ventas_por_dia = (
            ventas_qs
            .annotate(dia=TruncDay('fecha'))
            .values('dia')
            .annotate(total_dia=Sum('total'))
            .order_by('dia')
        )
        labels_dia = [v['dia'].strftime("%d %b") for v in ventas_por_dia]
        data_dia = [float(v['total_dia']) for v in ventas_por_dia]

        # gráfico de servicios realizados por el barbero
        servicios_realizados = (
            ventas_qs
            .values('cita__servicio__nombre')
            .annotate(total_servicios=Count('id'))
            .order_by('-total_servicios')
        )
        labels_metodo = [s['cita__servicio__nombre'] for s in servicios_realizados]
        data_metodo = [s['total_servicios'] for s in servicios_realizados]

    # ===================== OTRO ROL =====================
    else:
        ventas_qs = Venta.objects.none()
        citas_qs = Cita.objects.none()
        labels_dia = []
        data_dia = []
        labels_metodo = []
        data_metodo = []

    # enviar todos los datos al template
    return render(request, "administrador/dashboard.html", {
        'total_usuarios': total_usuarios,
        'total_servicios': total_servicios,
        'ventas_totales': ventas_totales,
        'dinero_total': dinero_total,
        'total_comprobantes': total_comprobantes,

        'mis_citas_hoy': mis_citas_hoy,
        'mis_ventas_hoy': mis_ventas_hoy,
        'mi_total_mes': mi_total_mes,

        'labels_dia': labels_dia,
        'data_dia': data_dia,
        'labels_metodo': labels_metodo,
        'data_metodo': data_metodo
    })


@login_required
def perfil(request):
    user_id = int(request.session.get('user_id'))
    usuario = Usuario.objects.get(id=user_id)

    if request.method == 'POST':
        # actualizar datos del usuario
        usuario.nombre = request.POST.get('nombre')
        usuario.email = request.POST.get('email')
        usuario.apellido = request.POST.get('apellido')

        # actualizar contraseña si se ingreso
        nueva_password = request.POST.get('password')
        if nueva_password:
            usuario.password = make_password(nueva_password)

        # actualizar foto si se subió
        if 'foto' in request.FILES:
            usuario.foto = request.FILES['foto']

        usuario.save()
        return redirect('perfil')

    return render(request, 'administrador/perfil.html', {
        'usuario': usuario
    })