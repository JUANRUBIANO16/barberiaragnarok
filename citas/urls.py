

from django.urls import path
from .import views
urlpatterns = [

    path('',views.citas, name="citas"),
    path('crear/',views.crearCita,name='crear_Cita') ,
    path('edit/<int:id>',views.cita_edit,name='cita_edit') ,  
    path('delete/<int:id>',views.cita_delete,name='cita_delete') ,
    path('obtener-horas/', views.obtener_horas_disponibles, name='obtener_horas'),
    path('reportes/', views.reporte_citas, name='reporte_citas'),
    path('reporte/pdf/', views.reporte_citas_pdf, name='reporte_pdf'),
    path('agendar/', views.agendar_cita, name='agendar_cita'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('historial/', views.historial_citas, name='historial_citas'),
]