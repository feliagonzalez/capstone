# core/views.py

# --- Imports de Django y DRF ---
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# --- Imports de tu aplicación ---
from .models import Pozo, Medicion, Alerta 
from .forms import PozoForm
from .serializers import MedicionSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

#===============================================================
# VISTAS DE PÁGINAS Y AUTENTICACIÓN
#===============================================================

def login_view(request):
    if request.method == 'POST':
        # Crea una instancia del formulario con los datos enviados
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Si el formulario es válido, autentica y loguea al usuario
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Django redirigirá automáticamente a la URL definida en LOGIN_REDIRECT_URL (ver Paso 3)
                return redirect('menu') 
    else:
        # Si la petición es GET, simplemente muestra el formulario vacío
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

# También necesitarás la vista para el nuevo menú
@login_required
def menu_view(request):
    return render(request, 'core/menu.html')





def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login') # O la URL de tu vista de login

@login_required
def dashboard_view(request):
    # 1. Obtener los pozos que pertenecen al usuario actual.
    pozos_usuario = Pozo.objects.filter(propietario=request.user)

    # 2. Preparar la lista de pozos para convertirla a JSON.
    #    Esto es lo que usará tu JavaScript para funcionar.
    pozos_list_json = list(pozos_usuario.values('id', 'nombre', 'ubicacion', 'latitud', 'longitud'))

    # 3. Crear el diccionario de contexto para la plantilla.
    context = {
        # 'pozos' es para que Django construya el <select> en el HTML.
        'pozos': pozos_usuario,
        # 'pozos_json' es para que JavaScript sepa los datos de los pozos y pueda funcionar.
        'pozos_json': json.dumps(pozos_list_json, cls=DjangoJSONEncoder)
    }
    
    # 4. Enviar los datos a la plantilla.
    return render(request, 'core/dashboard.html', context)

@login_required
def reportes_view(request):
    pozos_usuario = Pozo.objects.filter(propietario=request.user)
    mediciones = Medicion.objects.filter(pozo__in=pozos_usuario)

    # Filtros
    pozo_id = request.GET.get('pozo')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if pozo_id:
        mediciones = mediciones.filter(pozo_id=pozo_id)
    if fecha_inicio:
        mediciones = mediciones.filter(fecha_hora__gte=fecha_inicio)
    if fecha_fin:
        fecha_fin_dt = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d') + datetime.timedelta(days=1)
        mediciones = mediciones.filter(fecha_hora__lte=fecha_fin_dt)

    context = {
        'pozos': pozos_usuario,
        'mediciones': mediciones.order_by('-fecha_hora')
    }
    return render(request, 'core/reportes.html', context)


def registro_view(request):
    # Si el usuario ya está autenticado, lo redirigimos al menú
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        # Usamos nuestro formulario personalizado
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Si el formulario es válido, guardamos el nuevo usuario
            user = form.save()
            # Iniciamos sesión automáticamente para el nuevo usuario
            login(request, user) 
            # Redirigimos al menú principal
            return redirect('menu')
    else:
        # Si la petición es GET, mostramos un formulario vacío
        form = CustomUserCreationForm()
        
    return render(request, 'core/registro.html', {'form': form})

@login_required
def crear_pozo_view(request):
    if request.method == 'POST':
        form = PozoForm(request.POST)
        if form.is_valid():
            pozo = form.save(commit=False)
            pozo.propietario = request.user
            pozo.save()
            return redirect('dashboard')
    else:
        form = PozoForm()
    return render(request, 'core/crear_pozo.html', {'form': form})

#===============================================================
# VISTAS DE API (PARA JAVASCRIPT Y SENSORES)
#===============================================================

@login_required
def get_pozo_data(request, pozo_id):
    try:
        pozo = Pozo.objects.get(id=pozo_id, propietario=request.user)
        mediciones = pozo.mediciones.order_by('fecha_hora').all()[:50]
        data = {
            'labels': [m.fecha_hora.strftime('%H:%M') for m in mediciones],
            'niveles': [m.nivel_agua for m in mediciones],
        }
        return JsonResponse(data)
    except Pozo.DoesNotExist:
        return JsonResponse({'error': 'Pozo no encontrado'}, status=404)

@login_required
def get_alertas(request):
    alertas = Alerta.objects.filter(propietario=request.user, leida=False).order_by('-fecha_hora')
    data = {
        'alertas': list(alertas.values('id', 'descripcion', 'fecha_hora'))
    }
    return JsonResponse(data)

class SensorDataView(APIView):
    def post(self, request, format=None):
        serializer = MedicionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)