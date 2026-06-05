from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_servicios, name='listar_servicios'),
   
    path('crear/', views.Crear_servicio, name='crear_servicios'),
    path('edit/<int:id>/', views.servicio_edit, name='editar_servicios'),
    path('delete/<int:id>/', views.servicio_delete, name='eliminar_servicios'),
]