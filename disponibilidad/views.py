from datetime import datetime, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from barberia.decorators import role_required
from usuarios.models import Usuario
from .models import Disponibilidad


#  RANGO PERMITIDO
HORA_MIN = time(8, 0)
HORA_MAX = time(12, 0)


# =========================
# LISTAR DISPONIBILIDAD
# =========================
@role_required('barbero')
def disponibilidad(request):
    user_id = request.session.get('user_id')

    disponibilidades = Disponibilidad.objects.filter(barbero_id=user_id)

    return render(request, "disponibilidad.html", {
        "disponibilidades": disponibilidades
    })


# =========================
# CREAR DISPONIBILIDAD
# =========================
@role_required('barbero')
def crear_disponibilidad(request):
    if request.method == "POST":

        user_id = request.session.get('user_id')
        barbero = get_object_or_404(Usuario, id=user_id)

        dia = request.POST.get("dia_semana")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # ❌ campos obligatorios
        if not dia or not hora_inicio or not hora_fin:
            messages.error(request, "Todos los campos son obligatorios")
            return redirect('disponibilidad')

        #  convertir a time
        hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin = datetime.strptime(hora_fin, "%H:%M").time()

        #  validación horario permitido
        if hora_inicio < HORA_MIN or hora_fin > HORA_MAX:
            messages.error(request, "Solo puedes definir horarios entre 8:00 AM y 12:00 PM")
            return redirect('disponibilidad')

        # ❌ orden incorrecto
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora inicio debe ser menor a la hora fin")
            return redirect('disponibilidad')

        # ❌ duplicados
        if Disponibilidad.objects.filter(
            barbero=barbero,
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        ).exists():
            messages.error(request, "Ese horario ya existe")
            return redirect('disponibilidad')

        #  crear
        Disponibilidad.objects.create(
            barbero=barbero,
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )

        messages.success(request, "Horario agregado correctamente")

    return redirect('disponibilidad')


# =========================
# EDITAR DISPONIBILIDAD
# =========================
@role_required('barbero')
def editar_disponibilidad(request, id):
    disp = get_object_or_404(Disponibilidad, id=id)

    # seguridad
    if disp.barbero_id != request.session.get('user_id'):
        messages.error(request, "No puedes editar este horario")
        return redirect('disponibilidad')

    if request.method == "POST":

        dia = request.POST.get("dia_semana")
        hora_inicio = datetime.strptime(request.POST.get("hora_inicio"), "%H:%M").time()
        hora_fin = datetime.strptime(request.POST.get("hora_fin"), "%H:%M").time()

        #  validación horario permitido
        if hora_inicio < HORA_MIN or hora_fin > HORA_MAX:
            messages.error(request, "Solo puedes usar horario entre 8:00 AM y 12:00 PM")
            return redirect('disponibilidad')

        # ❌ orden incorrecto
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora inicio debe ser menor a la hora fin")
            return redirect('disponibilidad')

        # ❌ duplicados
        if Disponibilidad.objects.filter(
            barbero=disp.barbero,
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        ).exclude(id=id).exists():
            messages.error(request, "Ese horario ya existe")
            return redirect('disponibilidad')

        #  guardar cambios
        disp.dia_semana = dia
        disp.hora_inicio = hora_inicio
        disp.hora_fin = hora_fin
        disp.save()

        messages.success(request, "Horario actualizado correctamente")

    return redirect('disponibilidad')


# =========================
# ELIMINAR DISPONIBILIDAD
# =========================
@role_required('barbero')
def eliminar_disponibilidad(request, id):
    disp = get_object_or_404(Disponibilidad, id=id)

    # seguridad
    if disp.barbero_id != request.session.get('user_id'):
        messages.error(request, "No puedes eliminar este horario")
        return redirect('disponibilidad')

    disp.delete()
    messages.success(request, "Horario eliminado correctamente")

    return redirect('disponibilidad')