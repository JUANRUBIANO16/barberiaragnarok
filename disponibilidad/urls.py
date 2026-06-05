from django.urls import path
from . import views

urlpatterns = [
    path('', views.disponibilidad, name='disponibilidad'),
    path('crear/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('editar/<int:id>/', views.editar_disponibilidad, name='editar_disponibilidad'),
    path('eliminar/<int:id>/', views.eliminar_disponibilidad, name='eliminar_disponibilidad'),
]