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
    let map; // MAPA: Variable para el objeto de mapa Leaflet
    let currentMarker; // MAPA: Variable para el marcador actual

    // --- Funciones ---

    // MAPA: Función para inicializar el mapa
    function inicializarMapa() {
        // Coordenadas iniciales (ej: centro de Santiago, Chile)
        map = L.map('mapContainer').setView([-33.45, -70.65], 12); 
        
        // Usamos el mapa de CartoDB, que es neutral y de alta calidad
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(map);
    }

    // MAPA: Función para actualizar el marcador y la vista del mapa
    function actualizarMapa(lat, lon, nombrePozo) {
        // Si las coordenadas no son válidas (0 o nulas), no muestra el marcador.
        if (!lat || !lon) {
            if (currentMarker) {
                map.removeLayer(currentMarker);
            }
            // Centra el mapa en una vista general si no hay coordenadas
            map.setView([-33.45, -70.65], 12);
            return;
        }

        const newLatLng = new L.LatLng(lat, lon);
        map.setView(newLatLng, 15); // Centra el mapa en el pozo con zoom

        // Elimina el marcador anterior si existe
        if (currentMarker) {
            map.removeLayer(currentMarker);
        }

        // Añade un nuevo marcador
        currentMarker = L.marker(newLatLng).addTo(map)
            .bindPopup(`<b>${nombrePozo}</b>`)
            .openPopup();
    }

    async function fetchData(pozoId) {
        try {
            const response = await fetch(`/api/data/pozo/${pozoId}/`);
            if (!response.ok) {
                throw new Error('Error al obtener los datos del pozo');
            }
            return await response.json();
        } catch (error) {
            console.error(error);
            return null;
        }
    }

    function renderChart(data) {
        if (chart) {
            chart.destroy();
        }
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Nivel de Agua (m)',
                    data: data.niveles,
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

    async function updateDashboard(pozoId) {
        if (!pozoId) return;
        
        // Obtiene la opción seleccionada para acceder a sus datos
        const selectedOption = pozoSelector.options[pozoSelector.selectedIndex];
        const nombreCompleto = selectedOption.text;
        const nombrePozo = nombreCompleto.split(' - ')[0]; // Extrae solo el nombre
        const ubicacionPozo = nombreCompleto.split(' - ')[1]; // Extrae la ubicación

        // Actualizar la información del pozo en la tarjeta de la izquierda
        pozoTitulo.textContent = `Nivel de Agua: ${nombrePozo}`;
        infoPozoNombre.textContent = nombrePozo;
        infoPozoUbicacion.textContent = `Ubicación: ${ubicacionPozo || ''}`;

        // MAPA: Extraer latitud y longitud y actualizar el mapa
        const lat = parseFloat(selectedOption.getAttribute('data-latitud'));
        const lon = parseFloat(selectedOption.getAttribute('data-longitud'));
        actualizarMapa(lat, lon, nombrePozo);

        console.log(`Leyendo coordenadas -> Latitud: ${lat}, Longitud: ${lon}`);

        // Obtener y renderizar datos de mediciones y gráfico
        const data = await fetchData(pozoId);
        if (!data) return;

        renderChart(data);

        // Limpiar y rellenar la tabla de mediciones
        tablaMedicionesBody.innerHTML = '';
        if (data.labels.length === 0) {
            tablaMedicionesBody.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-3">No hay mediciones para este pozo.</td></tr>`;
        } else {
            for (let i = data.labels.length - 1; i >= 0; i--) {
                const row = `
                    <tr>
                        <td>${data.labels[i]}</td>
                        <td>${data.niveles[i]}</td>
                        <td>Operativo</td>
                    </tr>
                `;
                tablaMedicionesBody.innerHTML += row;
            }
        }
    }

    // --- LÓGICA DE INICIALIZACIÓN ---

    // MAPA: Inicializa el mapa al cargar la página
    inicializarMapa(); 

    // Event listener para cuando el usuario cambia de pozo
    pozoSelector.addEventListener('change', (e) => {
        updateDashboard(e.target.value);
    });

    // Cargar datos del primer pozo seleccionado al iniciar
    if (pozoSelector.value) {
        updateDashboard(pozoSelector.value);
    }
    
    // Opcional: Descomenta la sección de alertas si la vas a usar
    /*
    async function checkAlerts() {
        // ... tu lógica de alertas aquí ...
    }
    checkAlerts();
    setInterval(checkAlerts, 15000);
    */
   
    // Actualizar datos periódicamente
    setInterval(() => {
        if (pozoSelector.value) {
            updateDashboard(pozoSelector.value);
        }
    }, 30000); // Actualizar cada 30 segundos
});