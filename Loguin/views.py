from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from usuarios.models import Usuario
import uuid

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# =========================
# LOGIN
# =========================
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
            messages.error(request, "Error interno")

    return render(request, "loguin.html")


# =========================
# LOGOUT
# =========================
def logout_view(request):
    request.session.flush()
    return redirect('loguin')


# =========================
# RECUPERAR CONTRASEÑA
# =========================
def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Ingresa un correo")
            return render(request, 'recuperar_password.html')

        try:
            user = Usuario.objects.get(email=email)

            user.reset_token = str(uuid.uuid4())
            user.save()

            link = request.build_absolute_uri(
                f"/reset/{user.reset_token}/"
            )

            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject='Recuperar contraseña - Ragnarok Barber',
                html_content=f"""
                    <h3>Hola {user.nombre}</h3>
                    <p>Haz clic para resetear contraseña</p>
                    <a href="{link}">Resetear contraseña</a>
                """
            )

            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))  # ✔️ CORRECTO
            sg.send(message)

            messages.success(request, "Correo enviado correctamente")
            return redirect('loguin')

        except Usuario.DoesNotExist:
            messages.error(request, "Correo no registrado")

        except Exception as e:
            print("RESET ERROR:", e)
            messages.error(request, "Error enviando correo")

    return render(request, 'recuperar_password.html')
# =========================
# RESET PASSWORD
# =========================
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

# =========================
# REGISTER
# =========================
def register_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')

    if request.method == "POST":

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not all([nombre, apellido, email, password, confirm]):
            messages.error(request, "Completa todos los campos")
            return redirect('registro')

        if password != confirm:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado")
            return redirect('registro')

        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=make_password(password),
            tipo_usuario='cliente'
        )

        messages.success(request, "Registro exitoso, ya puedes iniciar sesión")
        return redirect('loguin')

    return render(request, "registro.html")