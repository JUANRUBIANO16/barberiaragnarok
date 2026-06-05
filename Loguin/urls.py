from django.urls import path
from .views import login_view, logout_view, recuperar_password, reset_password

urlpatterns = [
    path('', login_view, name='loguin'),
    path('logout/', logout_view, name='logout'),
    path('recuperar-password/', recuperar_password, name='recuperar_password'),
    
    path('reset/<uuid:token>/', reset_password, name='reset_password'),
]