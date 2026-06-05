from django.shortcuts import render
from django.http import JsonResponse
from Servicios.models import Servicio
from notificaciones.models import SolicitudCita


def vista(request):
    servicios = Servicio.objects.all()
    return render(request, "index.html", {
        'servicios': servicios
    })


def crearnoti(request):
    if request.method == 'POST':
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
            estado='pendiente'  # 👈 importante
        )

        return JsonResponse({
            "success": True,
            "message": "Solicitud creada correctamente"
        })

    return JsonResponse({
        "success": False,
        "error": "Método no permitido"
    })