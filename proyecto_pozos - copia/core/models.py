# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Pozo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=255)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # --- CAMPOS AÑADIDOS ---
    # Usamos FloatField, que es ideal para coordenadas geográficas.
    # null=True permite que el valor en la base de datos sea nulo.
    # blank=True permite que el campo esté vacío en los formularios (ej. el admin de Django).
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    # -----------------------

    def __str__(self):
        return self.nombre

class Medicion(models.Model):
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE, related_name='mediciones')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    nivel_agua = models.DecimalField(max_digits=6, decimal_places=2) # En metros
    estado_sensor = models.CharField(max_length=50, default='Operativo')

    def __str__(self):
        return f"Medición de {self.pozo.nombre} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"

class Alerta(models.Model):
    pozo = models.ForeignKey(Pozo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    leida = models.BooleanField(default=False)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alerta para {self.pozo.nombre} - {self.descripcion}"