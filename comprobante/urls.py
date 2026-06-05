from django.urls import path
from . import views

urlpatterns = [
    path('', views.comprobante, name="comprobantes"),
    path('crear/', views.crearComprobante, name='crear_comprobantes'),
    path('edit/<int:id>', views.comprobante_edit, name='editar_comprobantes'),
    path('delete/<int:id>', views.comprobante_delete, name='eliminar_comprobantes'),
    path('pdf/<int:id>/', views.generar_pdf_comprobantes, name='comprobante_pdf'),  # PDF individual
]