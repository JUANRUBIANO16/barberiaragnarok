from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from usuarios.models import Usuario
from django.contrib.auth.hashers import make_password
from barberia.decorators import login_required, role_required
from django.db.models import ProtectedError, Count, Sum
import openpyxl

# 🔥 IMPORTANTE (para reportes)
from citas.models import Cita
from Servicios.models import Servicio


# ==============================
# USUARIOS
# ==============================

@role_required('admin')
def usuario_list(request):
    usuarios = Usuario.objects.all()
    total_usuarios = Usuario.objects.count()
    return render(request, 'usuarios.html', {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios
    })


def usuario_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo_usuario')
        foto = request.FILES.get('foto')

        if not password or len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return redirect('usuarios')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado')
            return redirect('usuarios')

        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=make_password(password),
            tipo_usuario=tipo_usuario,
            foto=foto
        )

        messages.success(request, 'Usuario creado correctamente')
        return redirect('usuarios')


def usuario_edit(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo_usuario')
        foto = request.FILES.get('foto')

        if Usuario.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, 'Este correo ya está en uso')
            return redirect('usuarios')

        if password and len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return redirect('usuarios')

        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.email = email
        usuario.tipo_usuario = tipo_usuario

        if password:
            usuario.password = make_password(password)

        if foto:
            usuario.foto = foto

        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('usuarios')


def usuario_delete(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        try:
            usuario.delete()
            messages.success(request, 'Usuario eliminado correctamente')
        except ProtectedError:
            messages.error(
                request,
                'No puedes eliminar este usuario porque tiene citas asociadas'
            )

    return redirect('usuarios')


# ==============================
# CARGA MASIVA
# ==============================

def carga_masiva_usuarios(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if not archivo:
            messages.error(request, 'No se seleccionó ningún archivo')
            return redirect('usuarios')

        try:
            wb = openpyxl.load_workbook(archivo)
            hoja = wb.active

            creados = 0
            errores = 0

            for fila in hoja.iter_rows(min_row=2, values_only=True):
                nombre, apellido, email, password, tipo_usuario = fila

                if not email or not password:
                    errores += 1
                    continue

                if len(str(password)) < 6:
                    errores += 1
                    continue

                if tipo_usuario not in ['admin', 'barbero', 'cliente']:
                    errores += 1
                    continue

                if Usuario.objects.filter(email=email).exists():
                    errores += 1
                    continue

                try:
                    Usuario.objects.create(
                        nombre=nombre,
                        apellido=apellido,
                        email=email,
                        password=make_password(password),
                        tipo_usuario=tipo_usuario
                    )
                    creados += 1
                except Exception:
                    errores += 1

            messages.success(
                request,
                f'Se crearon {creados} usuarios correctamente y {errores} fallaron'
            )

        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')

    return redirect('usuarios')

