from django.db import models

class Solicitud(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    destino = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    adultos = models.IntegerField()
    ninos = models.IntegerField()
    vuelo = models.CharField(max_length=100)
    alojamiento = models.CharField(max_length=100)
    comida = models.CharField(max_length=100)
    equipaje = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    costo_vuelo = models.FloatField(default=0)
    costo_alojamiento = models.FloatField(default=0)
    costo_comida = models.FloatField(default=0)
    costo_equipaje = models.FloatField(default=0)
    total_ars = models.FloatField(default=0)
    total_usd = models.FloatField(default=0)

    def __str__(self):
        return f"{self.nombre} - {self.destino} ({self.fecha_registro.strftime('%d/%m/%Y')})"