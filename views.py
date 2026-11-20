import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import date
from .forms import PaqueteTuristicoForm, RegistroEmailForm, EdicionPerfilForm, SolicitudForm
from .models import Solicitud
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SolicitudSerializer


def index(request):
    form = PaqueteTuristicoForm()
    return render(request, 'index.html', {'form': form})


def calcular_porcentaje(monto, porcentaje):
    resultado = (monto * porcentaje) / 100
    return resultado


def formato_ars(monto):
    return f"${monto:,.0f}".replace(",", ".")


def formato_usd(monto, cotizacion):
    return f"USD $ {monto / cotizacion:.2f}"


def formato_dual(monto, cotizacion, es_descuento=False):
    prefijo = "- " if es_descuento else ""
    return f"{prefijo}{formato_ars(monto)} ({prefijo}{formato_usd(monto, cotizacion)})"


def simulador_view(request):
    total_final = 0
    total_usd = 0
    cotizacion_oficial = 0

    if request.method == 'POST':
        form = PaqueteTuristicoForm(request.POST)

        if form.is_valid():
            datos = form.cleaned_data

            # DATOS BÁSICOS
            destino_txt = dict(form.fields['destino'].choices)[datos['destino']]
            vuelo_txt = dict(form.fields['vuelo'].choices)[datos['vuelo']]
            alojamiento_txt = dict(form.fields['alojamiento'].choices)[datos['alojamiento']]
            comida_txt = dict(form.fields['comida'].choices)[datos['comida']]
            equipaje_txt = dict(form.fields['equipaje'].choices)[datos['equipaje']]

            # COSTOS
            dias_viaje = (datos['fecha_fin'] - datos['fecha_inicio']).days
            noches = dias_viaje - 1
            anticipacion = (datos['fecha_inicio'] - date.today()).days

            # CANTIDAD DE ADULTOS Y NIÑOS
            adultos = datos['adultos']
            ninos = datos['ninos']

            # PRECIOS  Y CÁLCULOS DE DESTINO, ALOJAMIENTO, COMIDA Y EQUIPAJE
            precios_destino = {'1': 100000, '2': 85000, '3': 90000, '4': 75000}
            precios_alojamiento = {'1': 35000, '2': 20000, '3': 12000}
            precios_comida = {'1': 0, '2': 6000, '3': 18000, '4': 30000}
            precios_equipaje = {'1': 0, '2': 25000, '3': 40000}

            precio_adulto_vuelo = precios_destino[datos['destino']]
            if datos['vuelo'] == '1':  # Recargo por vuelo directo
                precio_adulto_vuelo *= 1.20

            costo_vuelo = (adultos * precio_adulto_vuelo) + (ninos * (precio_adulto_vuelo * 0.70))

            precio_adulto_aloj = precios_alojamiento[datos['alojamiento']]
            costo_alojamiento = (adultos * precio_adulto_aloj * noches) + (ninos * (precio_adulto_aloj * 0.80) * noches)

            precio_adulto_comida = precios_comida[datos['comida']]
            costo_comida = (adultos * precio_adulto_comida * dias_viaje) + (
                    ninos * (precio_adulto_comida * 0.50) * dias_viaje)

            costo_equipaje = adultos * precios_equipaje[datos['equipaje']]

            subtotal = costo_vuelo + costo_alojamiento + costo_comida + costo_equipaje

            desc_viajeros = 5 if (adultos + ninos) >= 5 else 0
            desc_anticipacion = 5 if anticipacion >= 60 else 0

            if 5 <= noches <= 7:
                desc_noches = 5
            elif 8 <= noches <= 14:
                desc_noches = 10
            elif noches > 14:
                desc_noches = 15
            else:
                desc_noches = 0

            monto_desc_viajeros = calcular_porcentaje(subtotal, desc_viajeros)
            monto_desc_anticipacion = calcular_porcentaje(subtotal, desc_anticipacion)
            monto_desc_noches = calcular_porcentaje(subtotal, desc_noches)

            total_descuentos = monto_desc_viajeros + monto_desc_anticipacion + monto_desc_noches
            total_final = subtotal - total_descuentos

            # DOLAR API
            cotizacion_oficial = 1000  # Valor de respaldo
            try:
                response = requests.get('https://dolarapi.com/v1/dolares/oficial', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    cotizacion_oficial = data['venta']
            except requests.RequestException:
                pass

            # Se realiza el cálculo en dolares redondeando el resultado
            total_usd = round(total_final / cotizacion_oficial, 2)

            lineas_descuentos = []
            if desc_noches > 0:
                lineas_descuentos.append(
                    f"- Descuento por noches ({desc_noches}%): {formato_dual(monto_desc_noches, cotizacion_oficial, True)}"
                )
            if desc_viajeros > 0:
                lineas_descuentos.append(
                    f"- Descuento por viajeros ({desc_viajeros}%): {formato_dual(monto_desc_viajeros, cotizacion_oficial, True)}"
                )
            if desc_anticipacion > 0:
                lineas_descuentos.append(
                    f"- Descuento por reserva ({desc_anticipacion}%): {formato_dual(monto_desc_anticipacion, cotizacion_oficial, True)}"
                )

            bloque_descuentos = ("\n" + "\n".join(lineas_descuentos)) if lineas_descuentos else ""

            # ASUNTO DE EMAIL
            asunto = f"Confirmación de Reserva - TravelZen: Viaje a {destino_txt}"

            # ARMADO DE MENSAJE
            mensaje = (
                f"¡Hola {datos['nombre']}!\n\n"
                f"Recibimos tu solicitud para armar tu paquete turístico. Información cargada:\n\n"
                f"### DETALLE DEL VIAJE ###\n"
                f"- Destino: {destino_txt}\n"
                f"- Fechas: Del {datos['fecha_inicio']} al {datos['fecha_fin']}\n"
                f"- Pasajeros: {datos['adultos']} Adulto(s), {datos['ninos']}Niño(s)\n"
                f"- Vuelo: {vuelo_txt}\n"
                f"- Alojamiento: {alojamiento_txt}\n"
                f"- Comidas: {comida_txt}\n"
                f"- Equipaje: {equipaje_txt}\n"
                f"### DETALLE DE COSTOS ###\n"
                f"- Vuelo: {formato_ars(costo_vuelo)}\n"
                f"- Alojamiento: {formato_ars(costo_alojamiento)}\n"
                f"- Comidas: {formato_ars(costo_comida)}\n"
                f"- Equipaje: {formato_ars(costo_equipaje)}\n"
                f"-----------------------------------\n"
                f"SUBTOTAL: {formato_dual(subtotal, cotizacion_oficial)}"
                f"{bloque_descuentos}\n"
                f"-----------------------------------\n"
                f"TOTAL FINAL (ARS): {formato_ars(total_final)}\n"
                f"TOTAL FINAL (USD): USD $ {total_usd:.2f} (Cotización oficial: ARS ${cotizacion_oficial})\n\n"
                f"A la brevedad será notificado para finalizar el pago y confirmar la reserva.\n\n"
                f"¡Gracias por elegir TravelZen para su próximo destino!"
            )

            #  Guardar en la base de datos
            Solicitud.objects.create(
                nombre=datos['nombre'],
                email=datos['email'],
                destino=destino_txt,
                fecha_inicio=datos['fecha_inicio'],
                fecha_fin=datos['fecha_fin'],
                adultos=adultos,
                ninos=ninos,
                vuelo=vuelo_txt,
                alojamiento=alojamiento_txt,
                comida=comida_txt,
                equipaje=equipaje_txt,
                costo_vuelo=costo_vuelo,
                costo_alojamiento=costo_alojamiento,
                costo_comida=costo_comida,
                costo_equipaje=costo_equipaje,
                total_ars=total_final,
                total_usd=total_usd
            )

            # ENVIO DE EMAIL
            try:
                send_mail(
                    subject=asunto,
                    message=mensaje,
                    from_email='mpalavecino@proyectoweb.website',
                    recipient_list=[datos['email']],
                    fail_silently=False,
                )

                messages.success(request, '¡Tu paquete ha sido enviado! Revisa tu casilla de correo.')
                return redirect('simulador')

            except Exception as e:
                messages.error(request, f'Hubo un problema al enviar el correo: {e}')
    else:
        # Si el usuario está logueado, rellenamos el form con sus datos
        if request.user.is_authenticated:
            nombre_real = f"{request.user.first_name} {request.user.last_name}".strip()
            datos_iniciales = {
                'nombre': nombre_real if nombre_real else '',
                'email': request.user.email
            }
            form = PaqueteTuristicoForm()
        else:
            form = PaqueteTuristicoForm()

    return render(request, 'viajes/index.html', {
        'form': form,
        'total_ars': total_final,
        'total_usd': total_usd,
        'cotizacion': cotizacion_oficial
    })


def registro_view(request):
    if request.method == 'POST':
        form = RegistroEmailForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('panel')
    else:
        form = RegistroEmailForm()
    return render(request, 'viajes/registro.html', {'form': form})


@login_required
def panel_view(request):
    # Solicitudes de las mas recientes a las mas antiguas y solo las del usuario logueado
    solicitudes = Solicitud.objects.all().order_by('-id')
    return render(request, 'viajes/panel.html', {'solicitudes': solicitudes})


@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = EdicionPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.username = form.cleaned_data['email']
            request.user.save()
            return redirect('panel')
    else:
        form = EdicionPerfilForm(instance=request.user)
    return render(request, 'viajes/perfil.html', {'form': form})


@login_required
def editar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == 'POST':
        form = SolicitudForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, f'La solicitud #{solicitud.id} se actualizó correctamente.')
            return redirect('panel')
        else:
            messages.error(request, 'Error al actualizar la solicitud. Revisa los datos enviados.')
    else:
        form = SolicitudForm(instance=solicitud)

    return render(request, 'viajes/editar_solicitud.html', {'form': form, 'solicitud': solicitud})


@login_required
def eliminar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    solicitud.delete()
    messages.success(request, f'La solicitud de #{id} ha sido eliminada correctamente.')
    return redirect('panel')


@api_view(['GET'])
def solicitudes_api(request):
    solicitudes = Solicitud.objects.all().order_by('-id')
    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data)
