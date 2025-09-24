# core/admin.py
from django.contrib import admin
from .models import Pozo, Medicion, Alerta

class MedicionInline(admin.TabularInline):
    model = Medicion
    extra = 0 # No mostrar formularios extra por defecto
    readonly_fields = ('fecha_hora',)

@admin.register(Pozo)
class PozoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'propietario')
    list_filter = ('propietario',)
    search_fields = ('nombre', 'ubicacion')
    inlines = [MedicionInline]

@admin.register(Medicion)
class MedicionAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'fecha_hora', 'nivel_agua', 'estado_sensor')
    list_filter = ('pozo__propietario', 'pozo', 'fecha_hora')
    search_fields = ('pozo__nombre',)

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('pozo', 'descripcion', 'fecha_hora', 'leida', 'propietario')
    list_filter = ('propietario', 'leida')
    list_editable = ('leida',)