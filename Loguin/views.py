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

        if not email or not password:
            messages.error(request, "Completa todos los campos")
            return render(request, "loguin.html")

        try:
            user = Usuario.objects.get(email=email)

            if check_password(password, user.password):

                if hasattr(user, "last_login"):
                    user.last_login = timezone.now()
                    user.save()

                request.session['user_id'] = user.id
                request.session['user_nombre'] = user.nombre
                request.session['user_rol'] = getattr(user, 'tipo_usuario', 'usuario')

                return redirect('dashboard')

            else:
                messages.error(request, "Contraseña incorrecta")

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

        except Exception as e:
            print("LOGIN ERROR:", e)
            messages.error(request, "Error interno del servidor")

    return render(request, "loguin.html")


def logout_view(request):
    request.session.flush()
    return redirect('loguin')


def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Ingresa un correo")
            return render(request, 'recuperar_password.html')

        try:
            user = Usuario.objects.get(email=email)

            user.reset_token = uuid.uuid4()
            user.save()

            link = request.build_absolute_uri(f"/reset/{user.reset_token}/")

            send_mail(
                subject='Recuperar contraseña - Ragnarok Barber',
                message=(
                    f"Hola {user.nombre},\n\n"
                    f"Entra aquí para cambiar tu contraseña:\n{link}\n\n"
                    f"Si no fuiste tú, ignora este mensaje."
                ),
                from_email='soporte.rubianobarber@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Correo enviado")
            return redirect('loguin')

        except Usuario.DoesNotExist:
            messages.error(request, "Correo no registrado")

        except Exception as e:
            print("RESET ERROR:", e)
            messages.error(request, "Error enviando correo")

    return render(request, 'recuperar_password.html')


def reset_password(request, token):
    try:
        user = Usuario.objects.get(reset_token=token)

    except Usuario.DoesNotExist:
        messages.error(request, "Link inválido o expirado")
        return redirect('loguin')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not password or not confirm:
            messages.error(request, "Completa todos los campos")

        elif len(password) < 6:
            messages.error(request, "Mínimo 6 caracteres")

        elif password != confirm:
            messages.error(request, "No coinciden")

        else:
            user.password = make_password(password)
            user.reset_token = None
            user.save()

            messages.success(request, "Contraseña actualizada")
            return redirect('loguin')

    return render(request, 'reset_password.html')