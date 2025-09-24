// core/static/core/js/dashboard.js

document.addEventListener('DOMContentLoaded', function () {
    const pozoSelector = document.getElementById('pozoSelector');
    
    // Si no hay selector de pozo, no hacemos nada más.
    if (!pozoSelector) {
        console.log("No se encontraron pozos para este usuario.");
        return;
    }

    // --- Elementos del DOM ---
    const pozoTitulo = document.getElementById('pozo-seleccionado-titulo');
    const infoPozoNombre = document.getElementById('pozo-seleccionado-nombre');
    const infoPozoUbicacion = document.getElementById('pozo-seleccionado-ubicacion');
    const tablaMedicionesBody = document.getElementById('tablaMediciones');
    const ctx = document.getElementById('nivelAguaChart').getContext('2d');
    
    // --- Estado Global ---
    let chart;
    let map;
    let currentMarker;

    // --- Funciones ---

    function inicializarMapa() {
        map = L.map('mapContainer').setView([-33.45, -70.65], 12); 
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
    }

    function actualizarMapa(lat, lon, nombrePozo) {
        if (!lat || !lon) {
            if (currentMarker) map.removeLayer(currentMarker);
            map.setView([-33.45, -70.65], 12);
            return;
        }
        const newLatLng = new L.LatLng(lat, lon);
        map.setView(newLatLng, 15);
        if (currentMarker) map.removeLayer(currentMarker);
        currentMarker = L.marker(newLatLng).addTo(map)
            .bindPopup(`<b>${nombrePozo}</b>`)
            .openPopup();
    }

    async function fetchData(pozoId) {
        try {
            const response = await fetch(`/api/data/pozo/${pozoId}/`);
            if (!response.ok) throw new Error('Error al obtener los datos del pozo');
            return await response.json();
        } catch (error) {
            console.error(error);
            return null;
        }
    }

    function renderChart(data) {
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels.reverse(), // Invertimos para orden cronológico
                datasets: [{
                    label: 'Nivel de Agua (m)',
                    data: data.niveles.reverse(), // Invertimos para orden cronológico
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.1,
                    fill: true,
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: false,
                        title: { display: true, text: 'Nivel (metros)' }
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }
    
    // --- LÓGICA DE ALERTAS (AHORA DENTRO DEL BLOQUE PRINCIPAL) ---
    async function checkAlerts() {
        try {
            const response = await fetch('/api/data/alertas/');
            const data = await response.json();
            const container = document.getElementById('alertas-container');
            container.innerHTML = ''; 

            if (data.alertas && data.alertas.length > 0) {
                const alerta = data.alertas[0];
                const fecha = new Date(alerta.fecha_hora).toLocaleString('es-CL');
                
                const alertaDiv = document.createElement('div');
                alertaDiv.className = 'alert alert-danger';
                alertaDiv.setAttribute('role', 'alert');
                alertaDiv.innerHTML = `
                    <h4 class="alert-heading">¡Alerta Crítica!</h4>
                    <p>${alerta.descripcion}</p>
                    <hr>
                    <p class="mb-0"><small>Fecha: ${fecha}</small></p>
                `;
                container.appendChild(alertaDiv);
            }
        } catch (error) {
            console.error('Error al verificar alertas:', error);
        }
    }

    async function updateDashboard(pozoId) {
        if (!pozoId) return;
        
        const selectedOption = pozoSelector.options[pozoSelector.selectedIndex];
        const nombreCompleto = selectedOption.text;
        const nombrePozo = nombreCompleto.split(' - ')[0];
        const ubicacionPozo = nombreCompleto.split(' - ')[1];

        pozoTitulo.textContent = `Nivel de Agua: ${nombrePozo}`;
        infoPozoNombre.textContent = nombrePozo;
        infoPozoUbicacion.textContent = `Ubicación: ${ubicacionPozo || ''}`;

        const lat = parseFloat(selectedOption.getAttribute('data-latitud'));
        const lon = parseFloat(selectedOption.getAttribute('data-longitud'));
        actualizarMapa(lat, lon, nombrePozo);
        
        const data = await fetchData(pozoId);
        if (!data) return;

        renderChart(data);

        tablaMedicionesBody.innerHTML = '';
        if (!data.labels || data.labels.length === 0) {
            tablaMedicionesBody.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-3">No hay mediciones para este pozo.</td></tr>`;
        } else {
            // Recorremos los datos en el orden que llegan (más reciente primero)
            for (let i = 0; i < data.labels.length; i++) {
                const estado = data.estados[i];
                let estadoBadgeClass = 'bg-secondary';

                if (estado === 'Operativo') estadoBadgeClass = 'bg-success';
                else if (estado === 'Alerta') estadoBadgeClass = 'bg-warning text-dark';
                else if (estado === 'Crítico') estadoBadgeClass = 'bg-danger';

                const row = `
                    <tr>
                        <td>${data.labels[i]}</td>
                        <td>${data.niveles[i].toFixed(2)}</td>
                        <td><span class="badge ${estadoBadgeClass}">${estado}</span></td>
                    </tr>
                `;
                tablaMedicionesBody.innerHTML += row;
            }
        }
    }

    // --- LÓGICA DE INICIALIZACIÓN (ÚNICA Y CORRECTA) ---
    inicializarMapa(); 

    pozoSelector.addEventListener('change', (e) => {
        updateDashboard(e.target.value);
    });

    if (pozoSelector.value) {
        updateDashboard(pozoSelector.value);
    }
    
    checkAlerts(); // Primera revisión de alertas al cargar
    
    // Actualizar datos y alertas periódicamente
    setInterval(() => {
        if (pozoSelector.value) {
            updateDashboard(pozoSelector.value);
        }
        checkAlerts();
    }, 120000); // Actualizar cada 2 minutos
});