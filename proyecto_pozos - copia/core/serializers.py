# core/serializers.py
from rest_framework import serializers
from .models import Medicion, Pozo, Alerta

class MedicionSerializer(serializers.ModelSerializer):
    pozo_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Medicion
        fields = ['pozo_id', 'nivel_agua', 'estado_sensor']

    def create(self, validated_data):
        # Lógica para crear una alerta si el nivel es crítico
        nivel = validated_data.get('nivel_agua')
        if nivel <= 5.0: # Ejemplo de nivel crítico: 5 metros o menos
            pozo = Pozo.objects.get(id=validated_data.get('pozo_id'))
            Alerta.objects.create(
                pozo=pozo,
                propietario=pozo.propietario,
                descripcion=f"Nivel de agua crítico detectado: {nivel}m"
            )
        return Medicion.objects.create(**validated_data)