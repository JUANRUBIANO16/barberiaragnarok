


from django.urls import path
from.import views


urlpatterns = [
path('', views.vista, name='barberia'),
path('cita/', views.crearnoti, name='cita'),
]