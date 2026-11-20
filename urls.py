from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path('', views.simulador_view, name='simulador'),
    path('login/', auth_views.LoginView.as_view(
        template_name='viajes/login.html',
        authentication_form=EmailLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='simulador'), name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('panel/', views.panel_view, name='panel'),
    path('panel/editar/<int:id>/', views.editar_solicitud, name='editar_solicitud'),
    path('panel/eliminar/<int:id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('api/solicitudes/', views.solicitudes_api, name='solicitudes_api'),
]