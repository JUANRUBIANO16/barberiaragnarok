from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.models import Usuario
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone
import uuid


def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Usuario.objects.get(email=email)

            if check_password(password, user.password):
                user.last_login = timezone.now()
                user.save()

                request.session['user_id'] = user.id
                request.session['user_nombre'] = user.nombre
                request.session['user_rol'] = user.tipo_usuario

                
                return redirect('dashboard')

            messages.error(request, "Contraseña incorrecta")

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    return render(request, "loguin.html")


def logout_view(request):
    request.session.flush()
    
    return redirect('loguin')


def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Usuario.objects.get(email=email)

            # ✅ GENERAR TOKEN ÚNICO
            user.reset_token = uuid.uuid4()
            user.save()

            link = request.build_absolute_uri(
                f"/reset/{user.reset_token}/"
            )

            send_mail(
                subject='Recuperar contraseña - Ragnarok Barber',
                message=(
                    f"Hola {user.nombre},\n\n"
                    f"Usa este enlace para cambiar tu contraseña:\n\n"
                    f"{link}\n\n"
                    f"Si no solicitaste este cambio, ignora este correo."
                ),
                from_email='soporte.rubianobarber@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Te enviamos un enlace al correo para recuperar tu contraseña"
            )
            return redirect('loguin')

        except Usuario.DoesNotExist:
            messages.error(request, "Ese correo no está registrado")

    return render(request, 'recuperar_password.html')


def reset_password(request, token):
    try:
        user = Usuario.objects.get(reset_token=token)

    except Usuario.DoesNotExist:
        messages.error(request, "El enlace es inválido o ya expiró")
        return redirect('loguin')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not password or not confirm:
            messages.error(request, "Todos los campos son obligatorios")

        elif len(password) < 6:
            messages.error(request, "La contraseña debe tener mínimo 6 caracteres")

        elif password != confirm:
            messages.error(request, "Las contraseñas no coinciden")

        else:
            user.password = make_password(password)

            # ✅ INVALIDAR TOKEN
            user.reset_token = None
            user.save()

            messages.success(request, "Contraseña actualizada correctamente")
            return redirect('loguin')

    return render(request, 'reset_password.html')