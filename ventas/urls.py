from django.urls import path

from .import views




urlpatterns = [

    path('',views.ventas, name="ventas"),
    path('crear/',views.crearVenta,name='crear_ventas') ,
    path('edit/<int:id>',views.venta_edit,name='editar_ventas'),
    path('delete/<int:id>',views.venta_delete,name='eliminar_ventas')
    
]

