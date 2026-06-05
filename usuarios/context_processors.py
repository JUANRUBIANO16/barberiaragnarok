# usuarios/context_processors.py
from usuarios.models import Usuario

def usuario_actual(request):
    user_id = request.session.get('user_id')  # asumimos que guardas el id al hacer login
    if user_id:
        try:
            usuario = Usuario.objects.get(id=user_id)
            return {'usuario': usuario}
        except Usuario.DoesNotExist:
            return {}
    return {}