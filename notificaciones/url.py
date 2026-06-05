from django.urls import path
from . import views

urlpatterns = [
    path('', views.notificaciones, name='notificaciones'),

    path('editar/<int:id>/', views.editar_notificacion, name='editar_notificacion'),
    path('eliminar/<int:id>/', views.eliminar_notificacion, name='eliminar_notificacion'),

    # 👇 NUEVAS
    path('aceptar/<int:id>/', views.aceptar_cita, name='aceptar_cita'),
    path('cancelar/<int:id>/', views.cancelar_cita, name='cancelar_cita'),
]