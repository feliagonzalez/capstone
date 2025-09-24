# core/forms.py
from django import forms
from .models import Pozo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PozoForm(forms.ModelForm):
    class Meta:
        model = Pozo
        # AÑADE 'latitud' Y 'longitud' aquí
        fields = ['nombre', 'ubicacion', 'latitud', 'longitud']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pozo Principal'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sector Norte, Campo 1'}),
            # AÑADE los widgets para los nuevos campos
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: -33.45678'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: -70.64827'}),
        }

class CustomUserCreationForm(UserCreationForm):
    # Añadimos campos extra que queremos en el registro
    email = forms.EmailField(required=True, help_text="Requerido. Se usará para notificaciones.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Requerido.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Requerido.")

    class Meta(UserCreationForm.Meta):
        model = User
        # Definimos los campos que aparecerán en el formulario, en el orden que queramos
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Hacemos que todos los campos usen la clase de Bootstrap para un mejor estilo
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'