from django.urls import path
from . import views

urlpatterns = [
    path('', views.tipoPago, name='tipoPago'),
    path('crear/', views.crearTipoPago, name='crear_tipoPago'),
    path('editar/<int:id>/', views.editarTipoPago, name='editar_tipoPago'),
    path('eliminar/<int:id>/', views.eliminarTipoPago, name='eliminar_tipoPago'),
]