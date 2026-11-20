from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Solicitud

class PaqueteTuristicoForm(forms.Form):
    # DESTINOS Y FECHAS
    DESTINOS_CHOICES = [
        ('1', 'Bariloche'),
        ('2', 'Mendoza'),
        ('3', 'Iguazú'),
        ('4', 'Salta'),
    ]

    destino = forms.ChoiceField(choices=DESTINOS_CHOICES, widget=forms.RadioSelect, required=True)

    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True
    )

    adultos = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    ninos = forms.IntegerField(
        min_value=0, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # VUELOS
    VUELO_CHOICES = [
        ('1', 'Vuelo directo'),
        ('2', 'Vuelo con escala'),
    ]
    vuelo = forms.ChoiceField(
        choices=VUELO_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    # ALOJAMIENTOS
    ALOJAMIENTO_CHOICES = [
        ('1', 'Hotel 4 estrellas'),
        ('2', 'Hostel privado'),
        ('3', 'Hostel compartido'),
    ]
    alojamiento = forms.ChoiceField(
        choices=ALOJAMIENTO_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    # COMIDAS Y EQUIPAJES
    COMIDA_CHOICES = [
        ('1', 'Solo alojamiento'),
        ('2', 'Desayuno'),
        ('3', 'Media pensión'),
        ('4', 'Pensión completa'),
    ]
    comida = forms.ChoiceField(
        choices=COMIDA_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    EQUIPAJE_CHOICES = [
        ('1', 'Mochila / Equipaje de mano'),
        ('2', 'Valija 15 kg'),
        ('3', 'Valija 23 kg'),
    ]
    equipaje = forms.ChoiceField(
        choices=EQUIPAJE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    # DATOS DEL USUARIO QUE ESTA GESTIONANDO EL PAQUETE
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control bg-light'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control bg-light', 'placeholder': 'tu@gmail.com'})
    )

    costo_vuelo = forms.FloatField(widget=forms.HiddenInput(), required=False)
    costo_alojamiento = forms.FloatField(widget=forms.HiddenInput(), required=False)
    costo_comida = forms.FloatField(widget=forms.HiddenInput(), required=False)
    costo_equipaje = forms.FloatField(widget=forms.HiddenInput(), required=False)
    total_ars = forms.FloatField(widget=forms.HiddenInput(), required=False)
    total_usd = forms.FloatField(widget=forms.HiddenInput(), required=False)


class RegistroEmailForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class EdicionPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo'}

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lista de los campos numéricos o de texto que queremos bloquear.
        # IMPORTANTE: Reemplaza estos nombres por los exactos de tu models.py
        campos_bloqueados = [
            'destino', 'fecha_inicio', 'fecha_fin',
            'adultos', 'ninos', 'vuelo',
            'alojamiento', 'comida', 'equipaje',
            'costo_vuelo', 'costo_alojamiento', 'costo_comida','costo_equipaje',
            'total_ars', 'total_usd'
        ]

        for campo in campos_bloqueados:
            if campo in self.fields:
                self.fields[campo].widget.attrs['readonly'] = True
                self.fields[campo].widget.attrs['class'] = 'bg-light text-muted'
                self.fields[campo].widget.attrs['style'] = 'pointer-events: none;'