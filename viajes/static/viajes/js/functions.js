let cotizacionOficial = 1000;

fetch('https://dolarapi.com/v1/dolares/oficial')
    .then(response => response.json())
    .then(data => {
        cotizacionOficial = data.venta;
        if (document.getElementById('step-5')?.classList.contains('active')) {
            prepararResumen();
        }
        let labelCotizacion = document.getElementById('cotizacion_label');
        if (labelCotizacion) {
            labelCotizacion.innerText = 'ARS $' + cotizacionOficial;
        }
    })
    .catch(error => {
        console.error("Error haciendo la consulta a dolar api:", error);
        let labelCotizacion = document.getElementById('cotizacion_label');
        if (labelCotizacion) {
            labelCotizacion.innerText = 'ARS $' + cotizacionOficial;
        }
    });

function validateStep(current) {
    if (current === 1) {
        // VALIDACIÓN DE DESTINOS
        if (!document.querySelector('input[name="destino"]:checked')) {
            mostrarAlerta("Por favor, seleccione un destino.");
            return false;
        }

        // VALIDACIÓN DE FECHAS DE VIAJE
        const fechaInicio = document.getElementById('id_fecha_inicio').value;
        const fechaFin = document.getElementById('id_fecha_fin').value;
        if (!fechaInicio || !fechaFin) {
            mostrarAlerta("Complete las fechas de inicio y fin del viaje.");
            return false;
        }

        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        const inicio = new Date(fechaInicio + "T00:00:00");
        const fin = new Date(fechaFin + "T00:00:00");

        if (inicio <= hoy) {
            mostrarAlerta("La fecha de inicio no es valida.");
            return false;
        }

        const diasViaje = (fin - inicio) / (1000 * 60 * 60 * 24);
        if (diasViaje < 2) { // Regla: mínimo 2 días
            mostrarAlerta("El viaje debe tener al menos 2 días.");
            return false;
        }

        // VALIDACIÓN DE CANTIDAD DE ADULTOS Y NIÑOS
        const adultos = parseInt(document.getElementById('id_adultos').value);
        const ninos = parseInt(document.getElementById('id_ninos').value);

        if (isNaN(adultos) || adultos < 1) { // Regla: mínimo 1 adulto
            mostrarAlerta("Ingrese una cantidad válida de adultos (mayor o igual a 1(uno))");
            return false;
        }
        if (isNaN(ninos) || ninos < 0) { // Regla: niños no negativos
            mostrarAlerta("Ingrese una cantidad válida de niños (mayor o igual a 0(cero)).");
            return false;
        }
    } else if (current === 2) {
        if (!document.querySelector('input[name="vuelo"]:checked')) {
            mostrarAlerta("Por favor, seleccione un tipo de vuelo.");
            return false;
        }
    } else if (current === 3) {
        if (!document.querySelector('input[name="alojamiento"]:checked')) {
            mostrarAlerta("Por favor, seleccione un alojamiento.");
            return false;
        }
    } else if (current === 4) {
        if (!document.querySelector('input[name="comida"]:checked')) {
            mostrarAlerta("Por favor, seleccione un régimen de comidas.");
            return false;
        }
        if (!document.querySelector('input[name="equipaje"]:checked')) {
            mostrarAlerta("Por favor, seleccione una opción de equipaje.");
            return false;
        }
    }
    return true;
}

function prepararResumen() {
    // DATOS BÁSICOS Y CÁCULO DE CANTIDAD DE DIAS/NOCHES
    const fInicio = document.getElementById('id_fecha_inicio').value;
    const fFin = document.getElementById('id_fecha_fin').value;
    const inicio = new Date(fInicio + "T00:00:00");
    const fin = new Date(fFin + "T00:00:00");
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    const diasViaje = (fin - inicio) / (1000 * 60 * 60 * 24);
    const noches = diasViaje - 1;
    const anticipacion = Math.floor((inicio - hoy) / (1000 * 60 * 60 * 24));

    const adultos = parseInt(document.getElementById('id_adultos').value);
    const ninos = parseInt(document.getElementById('id_ninos').value);

    // OPCIONES SELECCIONADAS DE DESTINO, VUELO, ALOJAMIENTO, COMIDA Y EQUIPAJE
    const valDestino = document.querySelector('input[name="destino"]:checked').value;
    const valVuelo = document.querySelector('input[name="vuelo"]:checked').value;
    const valAloj = document.querySelector('input[name="alojamiento"]:checked').value;
    const valComida = document.querySelector('input[name="comida"]:checked').value;
    const valEquipaje = document.querySelector('input[name="equipaje"]:checked').value;

    // PRECIOS DE LOS DESTINOS, ALOJAMIENTOS, COMIDAS Y EQUIPAJES
    const preciosDestino = {'1': 100000, '2': 85000, '3': 90000, '4': 75000};
    const preciosAlojamiento = {'1': 35000, '2': 20000, '3': 12000};
    const preciosComida = {'1': 0, '2': 6000, '3': 18000, '4': 30000};
    const preciosEquipaje = {'1': 0, '2': 25000, '3': 40000};

    // CÁLCULOS PARA VUELOS
    let precioAdultoVuelo = preciosDestino[valDestino];
    if (valVuelo === '1') { // Si es directo, recargo del 20%
        precioAdultoVuelo = precioAdultoVuelo * 1.20;
    }
    const precioNinoVuelo = precioAdultoVuelo * 0.70;
    const costoVuelo = (adultos * precioAdultoVuelo) + (ninos * precioNinoVuelo);

    // CÁLCULOS PARA ALOJAMIENTO
    const precioAdultoAloj = preciosAlojamiento[valAloj];
    const precioNinoAloj = precioAdultoAloj * 0.80; // 20% descuento = 80% del valor
    const costoAlojamiento = (adultos * precioAdultoAloj * noches) + (ninos * precioNinoAloj * noches);

    // CÁLCULOS PARA COMIDAS
    const precioAdultoComida = preciosComida[valComida];
    const precioNinoComida = precioAdultoComida * 0.50;
    const costoComida = (adultos * precioAdultoComida * diasViaje) + (ninos * precioNinoComida * diasViaje);

    // CÁLCULOS PARA EQUIPAJES
    const costoEquipaje = adultos * preciosEquipaje[valEquipaje];

    // SUBTOTAL
    const subtotal = costoVuelo + costoAlojamiento + costoComida + costoEquipaje;

    // DESCUENTOS
    let descViajeros = 0;
    if ((adultos + ninos) >= 5) {
        descViajeros = 5;
    }

    let descAnticipacion = 0;
    if (anticipacion >= 60) {
        descAnticipacion = 5;
    }

    let descNoches = 0;
    if (noches >= 5 && noches <= 7) {
        descNoches = 5;
    } else if (noches >= 8 && noches <= 14) {
        descNoches = 10;
    } else if (noches > 14) {
        descNoches = 15;
    }

    const montoDescViajeros = (subtotal * descViajeros) / 100;
    const montoDescAnticipacion = (subtotal * descAnticipacion) / 100;
    const montoDescNoches = (subtotal * descNoches) / 100;

    const totalDescuentos = montoDescViajeros + montoDescAnticipacion + montoDescNoches;
    const totalFinal = subtotal - totalDescuentos;

    // INFORMACIÓN GENERAL ---
    document.getElementById('res_destino').innerText = document.querySelector('input[name="destino"]:checked').nextElementSibling.querySelector('h6').innerText;
    document.getElementById('res_fechas').innerText = fInicio.split('-').reverse().join('-') + ' al ' + fFin.split('-').reverse().join('-');
    document.getElementById('res_viajeros').innerText = `${adultos} Adulto(s), ${ninos} Niño(s)`;
    document.getElementById('res_vuelo').innerText = document.querySelector('input[name="vuelo"]:checked').nextElementSibling.querySelector('strong').innerText;
    document.getElementById('res_alojamiento').innerText = document.querySelector('input[name="alojamiento"]:checked').nextElementSibling.querySelector('h6').innerText;
    document.getElementById('res_comidas').innerText = document.querySelector('input[name="comida"]:checked').nextElementSibling.querySelector('.servicio-title').innerText;
    document.getElementById('res_equipaje').innerText = document.querySelector('input[name="equipaje"]:checked').nextElementSibling.querySelector('.servicio-title').innerText;
    document.getElementById('res_anticipacion').innerText = `${anticipacion} días`;

    // DETALLE DE COSTOS
    // Funcion recomendable para que se visualicen correctamente en pesos los valores
    const formatMoney = (num) => '$ ' + num.toLocaleString('es-AR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
    const formatUsd = (num) => 'USD $ ' + (num / cotizacionOficial).toFixed(2);
    const formatDual = (num, esDescuento = false) => {
        const prefijo = esDescuento ? '- ' : '';
        const claseUsd = esDescuento ? 'fw-normal opacity-75' : 'text-muted fw-normal';
        return `${prefijo}${formatMoney(num)} <small class="${claseUsd}">(${prefijo}${formatUsd(num)})</small>`;
    };
    document.getElementById('costo_vuelo').innerHTML = formatDual(costoVuelo);
    document.getElementById('label_costo_alojamiento').innerHTML = `Alojamiento (${noches} noches)`;
    document.getElementById('costo_alojamiento').innerHTML = formatDual(costoAlojamiento);
    document.getElementById('costo_comidas').innerHTML = formatDual(costoComida);
    document.getElementById('costo_equipaje').innerHTML = formatDual(costoEquipaje);
    document.getElementById('costo_subtotal').innerHTML = formatDual(subtotal);

    // Se incorporan los datos de los diferentes descuentos
    if (descNoches > 0) {
        document.getElementById('row_desc_noches').style.display = 'flex';
        document.getElementById('label_desc_noches').innerText = `Descuento por noches (${descNoches}%)`;
        document.getElementById('val_desc_noches').innerHTML = formatDual(montoDescNoches, true);
    } else {
        document.getElementById('row_desc_noches').style.display = 'none';
    }

    if (descViajeros > 0) {
        document.getElementById('row_desc_viajeros').style.display = 'flex';
        document.getElementById('label_desc_viajeros').innerText = `Descuento por viajeros (${descViajeros}%)`;
        document.getElementById('val_desc_viajeros').innerHTML = formatDual(montoDescViajeros, true);
    } else {
        document.getElementById('row_desc_viajeros').style.display = 'none';
    }

    if (descAnticipacion > 0) {
        document.getElementById('row_desc_anticipacion').style.display = 'flex';
        document.getElementById('label_desc_anticipacion').innerText = `Descuento por reserva (${descAnticipacion}%)`;
        document.getElementById('val_desc_anticipacion').innerHTML = formatDual(montoDescAnticipacion, true);
    } else {
        document.getElementById('row_desc_anticipacion').style.display = 'none';
    }

    document.getElementById('costo_total').innerText = formatMoney(totalFinal);
    let totalUsd = (totalFinal / cotizacionOficial).toFixed(2);
    document.getElementById('costo_total_usd').innerText = "USD $ " + totalUsd;

    // Buscamos los inputs
    const inputVuelo = document.getElementById('id_costo_vuelo');
    const inputAlojamiento = document.getElementById('id_costo_alojamiento');
    const inputComida = document.getElementById('id_costo_comida');
    const inputEquipaje = document.getElementById('id_costo_equipaje');
    const inputTotalArs = document.getElementById('id_total_ars');
    const inputTotalUsd = document.getElementById('id_total_usd');

    if (inputVuelo) inputVuelo.value = costoVuelo;
    if (inputAlojamiento) inputAlojamiento.value = costoAlojamiento;
    if (inputComida) inputComida.value = costoComida;
    if (inputEquipaje) inputEquipaje.value = costoEquipaje;
    if (inputTotalArs) inputTotalArs.value = totalFinal;
    if (inputTotalUsd) inputTotalUsd.value = totalUsd;
}

function updateStepperVisuals(targetStep) {
    for (let i = 1; i <= 5; i++) {
        let indicator = document.getElementById('indicator-' + i);

        if (i < targetStep) {
            // COMPLETADO (Color:verde)
            indicator.classList.remove('active');
            indicator.classList.add('completed');
        } else if (i === targetStep) {
            // EN PROGRESO (Color:violeta)
            indicator.classList.remove('completed');
            indicator.classList.add('active');
        } else {
            // A COMPLETAR (Color:gris)
            indicator.classList.remove('active', 'completed');
        }
    }
}

function nextStep(current) {
    // Se validan los datos antes de pasar de sección
    if (!validateStep(current)) {
        return;
    }

    // Al momento de pasar del paso 4 al 5 se recolecta la información para mostrar
    if (current === 4) {
        prepararResumen();
    }

    // Cambio de pantalla
    document.getElementById('step-' + current).classList.remove('active');
    let next = current + 1;
    document.getElementById('step-' + next).classList.add('active');

    // Actualización colores de la barra de progreso
    updateStepperVisuals(next);
    document.getElementById('simulador').scrollIntoView({behavior: 'smooth'});
}

function prevStep(current) {
    document.getElementById('step-' + current).classList.remove('active');
    let prev = current - 1;
    document.getElementById('step-' + prev).classList.add('active');

    updateStepperVisuals(prev);
    document.getElementById('simulador').scrollIntoView({behavior: 'smooth'});
}

function goToStep(target) {
    document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
    document.getElementById('step-' + target).classList.add('active');

    updateStepperVisuals(target);
    document.getElementById('simulador').scrollIntoView({behavior: 'smooth'});
}

function mostrarAlerta(mensaje, tipo = 'danger') {
    const container = document.getElementById('alert-container');
    const icono = tipo === 'danger' ? '⚠️ ERROR' : '✅ ÉXITO';

    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm border-0 mt-2`;
    alerta.innerHTML = `
                <strong>${icono}:</strong> ${mensaje}
            `;

    container.appendChild(alerta);

    // Luego de 3 segundos desaparece
    setTimeout(() => {
        alerta.classList.remove('show');
        setTimeout(() => alerta.remove(), 150);
    }, 3000);
}

document.addEventListener("DOMContentLoaded", function () {
    const alertas = document.querySelectorAll('#alert-container .alert');

    alertas.forEach(alerta => {
        setTimeout(() => {
            alerta.classList.remove('show');
            setTimeout(() => alerta.remove(), 150);
        }, 3000);
    });
});

// VALIDACIÓN DEL NOMBRE Y EMAIL ANTES DE CONFIRMAR EL PAQUETE
document.getElementById('paqueteForm').addEventListener('submit', function (e) {
    const nombre = document.getElementById('id_nombre').value.trim();
    const email = document.getElementById('id_email').value.trim();

    if (!nombre) {
        e.preventDefault(); // Frena el envío a Django
        mostrarAlerta("Por favor, ingresá tu Nombre y Apellido.");
        document.getElementById('id_nombre').focus();
        return;
    }

    if (!email || !email.includes('@') || !email.includes('.')) {
        e.preventDefault();
        mostrarAlerta("Por favor, ingresá un email válido.");
        document.getElementById('id_email').focus();
        return;
    }
});