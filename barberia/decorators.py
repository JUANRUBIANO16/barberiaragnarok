from django.shortcuts import redirect
from django.contrib import messages


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "Debes iniciar sesión")
            return redirect('loguin')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                messages.error(request, "Debes iniciar sesión")
                return redirect('loguin')

            if request.session.get('user_rol') != role:
                messages.error(request, "No tienes permisos")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator