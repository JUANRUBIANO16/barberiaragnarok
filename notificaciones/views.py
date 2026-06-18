from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from twilio.rest import Client
from django.contrib.auth.hashers import make_password

from notificaciones.models import SolicitudCita
from Servicios.models import Servicio
from citas.models import Cita
from usuarios.models import Usuario



# enviar sms


#// definimos que va recibir nuestra funcion el numero y la funcion
def enviar_sms(numero, mensaje):
    try:
        numero = str(numero).replace(" ", "").replace("-", "")


 #//si numero no contiene el codigo  se agrega el de colombia
        if not numero.startswith("+"):
            numero = "+57" + numero

        print(" Enviando SMS a:", numero)
#//conexio con twilo no autenticamos
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)


#//creacion y envio  del cuerpo sms
        message = client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_NUMBER,
            to=numero
        )

        print(" SMS enviado SID:", message.sid)

    except Exception as e:
        print(" ERROR SMS:", e)


#listar notificaciones
def notificaciones(request):
    return render(request, "notificaciones.html", {
        'notificaciones': SolicitudCita.objects.all(),
        'servicios': Servicio.objects.all(),
        'barberos': Usuario.objects.filter(tipo_usuario='barbero')
    })


#editar notificacion
def editar_notificacion(request, id):
    try:
        n = SolicitudCita.objects.get(id=id)

        if request.method == 'POST':
            n.nombre = request.POST.get('nombre')
            n.telefono = request.POST.get('telefono')
            n.email = request.POST.get('email')
            n.mensaje = request.POST.get('mensaje')

            servicio_id = request.POST.get('servicio')
            n.servicio = Servicio.objects.filter(id=servicio_id).first() if servicio_id else None

            n.save()
            messages.success(request, "Notificación actualizada")

    except SolicitudCita.DoesNotExist:
        messages.error(request, "No existe")

    return redirect('notificaciones')


#eliminar notificacion
def eliminar_notificacion(request, id):
    try:
        SolicitudCita.objects.get(id=id).delete()
        messages.success(request, "Eliminada")
    except:
        messages.error(request, "Error")

    return redirect('notificaciones')


 
# Cancelar cita

def cancelar_cita(request, id):
    try:
        n = SolicitudCita.objects.get(id=id)
        n.estado = 'cancelada'
        n.save()
        messages.warning(request, "Solicitud cancelada")
    except:
        messages.error(request, "Error")

    return redirect('notificaciones')

def aceptar_cita(request, id):
    try:
        n = SolicitudCita.objects.get(id=id)

        if request.method == "POST":

            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            barbero_id = request.POST.get('barbero')
            servicio_id = request.POST.get('servicio')

            if not all([fecha, hora, barbero_id, servicio_id]):
                messages.error(request, "Todos los campos son obligatorios")
                return redirect('notificaciones')

            barbero = Usuario.objects.get(id=barbero_id)
            servicio = Servicio.objects.get(id=servicio_id)

            # validar duplicado
            if Cita.objects.filter(
                fecha=fecha,
                hora=hora,
                barbero=barbero
            ).exists():
                messages.error(request, "Ese horario ya está ocupado")
                return redirect('notificaciones')

            # ==========================
            # SOLO CLIENTE EXISTENTE
            # ==========================
            cliente = Usuario.objects.filter(email=n.email).first()

            if not cliente:
                messages.error(request, "El cliente no existe en el sistema")
                return redirect('notificaciones')

            # ==========================
            # CREAR CITA
            # ==========================
            Cita.objects.create(
                fecha=fecha,
                hora=hora,
                estado='pendiente',
                barbero=barbero,
                cliente=cliente,
                servicio=servicio
            )

            # ==========================
            # SMS
            # ==========================
            mensaje = f"""
Hola {n.nombre}

Tu cita ha sido confirmada ✔️

Fecha: {fecha}
Hora: {hora}
Servicio: {servicio.nombre}

Te esperamos 💈
"""

            if n.telefono:
                enviar_sms(n.telefono, mensaje)

            n.estado = 'aceptada'
            n.save()

            messages.success(request, "Cita creada correctamente")

    except SolicitudCita.DoesNotExist:
        messages.error(request, "Solicitud no existe")

    except Exception as e:
        print("ERROR:", str(e))
        messages.error(request, f"Error: {e}")

    return redirect('notificaciones')