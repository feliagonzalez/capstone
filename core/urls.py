# core/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Ruta raíz
    path('', views.home_view, name='home'),

    # Vistas de la aplicación
    path('menu/', views.menu_view, name='menu'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('pozo/crear/', views.crear_pozo_view, name='crear_pozo'),

    # Autenticación (¡Corregido y sin duplicados!)
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Rutas de API
    path('api/sensor-data/', views.SensorDataView.as_view(), name='sensor_data'),
    path('api/data/pozo/<int:pozo_id>/', views.get_pozo_data, name='get_pozo_data'),
    path('api/data/alertas/', views.get_alertas, name='get_alertas'),
    path('api/data/pozo/<int:pozo_id>/', views.get_pozo_data, name='get_pozo_data'),
]