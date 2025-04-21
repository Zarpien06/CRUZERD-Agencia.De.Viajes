// Configuración de la gráfica de ocupación
document.addEventListener('DOMContentLoaded', function() {
    // Datos para el gráfico de ocupación (usando datos pasados desde el backend)
    var ocupacionData = {{ ocupacion_mensual|tojson }};
    
    var ctx = document.getElementById('ocupacionChart').getContext('2d');
    var ocupacionChart = new Chart(ctx, {
    type: 'line',
    data: {
    labels: ocupacionData.map(item => item.mes),
    datasets: [{
        label: 'Ocupación (%)',
        data: ocupacionData.map(item => item.ocupacion),
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        tension: 0.4
    }]
    },
    options: {
    responsive: true,
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
            ticks: {
                callback: function(value) {
                    return value + '%';
                }
            }
        }
    },
    plugins: {
        legend: {
            display: true,
            position: 'top'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    return context.dataset.label + ': ' + context.parsed.y + '%';
                }
            }
        }
    }
    }
    });
    });
    
    // JavaScript para gestionar modales de hoteles 
     
        // Para editar hotel
        function editarHotel(hotelId, nombre, direccion, ciudad, pais, estrellas) {
          document.getElementById('edit_nombre').value = nombre;
          document.getElementById('edit_direccion').value = direccion;
          document.getElementById('edit_ciudad').value = ciudad;
          document.getElementById('edit_pais').value = pais;
          document.getElementById('edit_estrellas').value = estrellas;
          
          const formEditarHotel = document.getElementById('formEditarHotel');
          formEditarHotel.action = `/proveedor/hotel/${hotelId}/editar`;
          
          const modal = new bootstrap.Modal(document.getElementById('editarHotelModal'));
          modal.show();
        }
        
        // Para eliminar hotel
        function eliminarHotel(hotelId, nombre) {
          document.getElementById('hotel_nombre_eliminar').textContent = nombre;
          document.getElementById('formEliminarHotel').action = `/proveedor/hotel/${hotelId}/eliminar`;
          
          const modal = new bootstrap.Modal(document.getElementById('eliminarHotelModal'));
          modal.show();
        }
        
        // Para gestionar habitaciones
        function gestionarHabitaciones(hotelId, nombreHotel) {
          document.getElementById('hotel_nombre_habitaciones').textContent = nombreHotel;
          
          // Cargar habitaciones via AJAX
          fetch(`/proveedor/hotel/${hotelId}/habitaciones-json`)
            .then(response => response.json())
            .then(data => {
              const tabla = document.getElementById('tablaHabitaciones').getElementsByTagName('tbody')[0];
              tabla.innerHTML = '';
              
              if (data.habitaciones.length === 0) {
                const fila = tabla.insertRow();
                const celda = fila.insertCell(0);
                celda.colSpan = 5;
                celda.className = 'text-center text-muted py-3';
                celda.innerHTML = 'No hay habitaciones registradas para este hotel';
              } else {
                data.habitaciones.forEach(hab => {
                  const fila = tabla.insertRow();
                  
                  fila.insertCell(0).textContent = hab.tipo;
                  fila.insertCell(1).textContent = hab.capacidad;
                  fila.insertCell(2).textContent = `$${parseFloat(hab.precio).toFixed(2)}`;
                  
                  const celdaDisponible = fila.insertCell(3);
                  if (hab.disponible) {
                    celdaDisponible.innerHTML = '<span class="badge bg-success">Disponible</span>';
                  } else {
                    celdaDisponible.innerHTML = '<span class="badge bg-danger">No disponible</span>';
                  }
                  
                  const celdaAcciones = fila.insertCell(4);
                  celdaAcciones.innerHTML = `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editarHabitacion(${hab.id}, '${hab.tipo}', ${hab.capacidad}, ${hab.precio}, ${hab.disponible})">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarHabitacion(${hab.id}, '${hab.tipo}')">
                      <i class="fas fa-trash"></i>
                    </button>
                  `;
                });
              }
            });
          
          // Configurar formulario para nuevas habitaciones
          document.getElementById('btnNuevaHabitacion').onclick = function() {
            mostrarFormularioHabitacion('nueva', hotelId);
          };
          
          const modal = new bootstrap.Modal(document.getElementById('gestionHabitacionesModal'));
          modal.show();
        }
        
        // Mostrar formulario de habitación para crear o editar
        function mostrarFormularioHabitacion(modo, hotelId, habitacionId = null) {
          const container = document.getElementById('formHabitacionContainer');
          const form = document.getElementById('formHabitacion');
          const titulo = document.getElementById('tituloFormHabitacion');
          
          // Resetear formulario
          form.reset();
          
          if (modo === 'nueva') {
            titulo.textContent = 'Nueva Habitación';
            form.action = `/proveedor/hotel/${hotelId}/habitacion/nueva`;
          } else {
            titulo.textContent = 'Editar Habitación';
            form.action = `/proveedor/habitacion/${habitacionId}/actualizar`;
          }
          
          container.style.display = 'block';
          
          // Configurar botón cancelar
          document.getElementById('btnCancelarHabitacion').onclick = function() {
            container.style.display = 'none';
          };
        }
        
        // Editar habitación
        function editarHabitacion(habitacionId, tipo, capacidad, precio, disponible) {
          document.getElementById('tipo_habitacion').value = tipo;
          document.getElementById('capacidad_habitacion').value = capacidad;
          document.getElementById('precio_habitacion').value = precio;
          document.getElementById('disponible_habitacion').checked = disponible;
          
          mostrarFormularioHabitacion('editar', null, habitacionId);
        }
        
        // Eliminar habitación
        function eliminarHabitacion(habitacionId, tipo) {
          if (confirm(`¿Está seguro que desea eliminar la habitación ${tipo}?`)) {
            fetch(`/proveedor/habitacion/${habitacionId}/eliminar`, {
              method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                alert('Habitación eliminada con éxito');
                // Recargar tabla de habitaciones
                const hotelId = document.getElementById('formHabitacion').action.split('/')[3];
                gestionarHabitaciones(hotelId, document.getElementById('hotel_nombre_habitaciones').textContent);
              } else {
                alert('Error al eliminar la habitación: ' + data.message);
              }
            });
          }
        }
    
    
        // JavaScript para gestionar modales de aerolíneas
     
    
        // Para editar aerolínea
        function editarAerolinea(aerolineaId, nombre, codigo) {
          document.getElementById('edit_nombre_aerolinea').value = nombre;
          document.getElementById('edit_codigo_aerolinea').value = codigo;
          
          const formEditarAerolinea = document.getElementById('formEditarAerolinea');
          formEditarAerolinea.action = `/proveedor/aerolinea/${aerolineaId}/editar`;
          
          const modal = new bootstrap.Modal(document.getElementById('editarAerolineaModal'));
          modal.show();
        }
        
        // Para eliminar aerolínea
        function eliminarAerolinea(aerolineaId, nombre) {
          document.getElementById('aerolinea_nombre_eliminar').textContent = nombre;
          document.getElementById('formEliminarAerolinea').action = `/proveedor/aerolinea/${aerolineaId}/eliminar`;
          
          const modal = new bootstrap.Modal(document.getElementById('eliminarAerolineaModal'));
          modal.show();
        }
        
        // Para gestionar vuelos
        function gestionarVuelos(aerolineaId, nombreAerolinea) {
          document.getElementById('aerolinea_nombre_vuelos').textContent = nombreAerolinea;
          
          // Cargar vuelos via AJAX
          fetch(`/proveedor/aerolinea/${aerolineaId}/vuelos-json`)
            .then(response => response.json())
            .then(data => {
              const tabla = document.getElementById('tablaVuelos').getElementsByTagName('tbody')[0];
              tabla.innerHTML = '';
              
              if (data.vuelos.length === 0) {
                const fila = tabla.insertRow();
                const celda = fila.insertCell(0);
                celda.colSpan = 8;
                celda.className = 'text-center text-muted py-3';
                celda.innerHTML = 'No hay vuelos registrados para esta aerolínea';
              } else {
                data.vuelos.forEach(vuelo => {
                  const fila = tabla.insertRow();
                  
                  fila.insertCell(0).textContent = vuelo.origen_nombre;
                  fila.insertCell(1).textContent = vuelo.destino_nombre;
                  
                  // Formatear fechas
                  const fechaSalida = new Date(vuelo.fecha_salida);
                  const fechaLlegada = new Date(vuelo.fecha_llegada);
                  
                  fila.insertCell(2).textContent = fechaSalida.toLocaleString();
                  fila.insertCell(3).textContent = fechaLlegada.toLocaleString();
                  
                  fila.insertCell(4).textContent = vuelo.capacidad;
                  
                  // Colorear asientos disponibles según disponibilidad
                  const celdaDisponibles = fila.insertCell(5);
                  const porcentajeDisponible = (vuelo.asientos_disponibles / vuelo.capacidad) * 100;
                  
                  if (porcentajeDisponible > 50) {
                    celdaDisponibles.innerHTML = `<span class="badge bg-success">${vuelo.asientos_disponibles}</span>`;
                  } else if (porcentajeDisponible > 10) {
                    celdaDisponibles.innerHTML = `<span class="badge bg-warning text-dark">${vuelo.asientos_disponibles}</span>`;
                  } else {
                    celdaDisponibles.innerHTML = `<span class="badge bg-danger">${vuelo.asientos_disponibles}</span>`;
                  }
                  
                  fila.insertCell(6).textContent = `$${parseFloat(vuelo.precio).toFixed(2)}`;
                  
                  const celdaAcciones = fila.insertCell(7);
                  celdaAcciones.innerHTML = `
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="actualizarVuelo(${vuelo.id}, ${vuelo.asientos_disponibles}, ${vuelo.capacidad}, ${vuelo.precio})">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarVuelo(${vuelo.id}, '${vuelo.origen_nombre} - ${vuelo.destino_nombre}')">
                      <i class="fas fa-trash"></i>
                    </button>
                  `;
                });
              }
            });
          
          // Configurar formulario para nuevos vuelos
          document.getElementById('btnNuevoVuelo').onclick = function() {
            mostrarFormularioVuelo(aerolineaId);
          };
          
          const modal = new bootstrap.Modal(document.getElementById('gestionVuelosModal'));
          modal.show();
        }
        
        // Mostrar formulario de vuelo para crear
        function mostrarFormularioVuelo(aerolineaId) {
          const container = document.getElementById('formVueloContainer');
          const form = document.getElementById('formVuelo');
          
          // Ocultar formulario de actualización si está visible
          document.getElementById('formActualizarVueloContainer').style.display = 'none';
          
          // Resetear formulario
          form.reset();
          form.action = `/proveedor/aerolinea/${aerolineaId}/vuelo/nuevo`;
          
          container.style.display = 'block';
          
          // Configurar botón cancelar
          document.getElementById('btnCancelarVuelo').onclick = function() {
            container.style.display = 'none';
          };
        }
        
        // Mostrar formulario para actualizar vuelo
        function actualizarVuelo(vueloId, asientosDisponibles, capacidad, precio) {
          const container = document.getElementById('formActualizarVueloContainer');
          const form = document.getElementById('formActualizarVuelo');
          
          // Ocultar formulario de creación si está visible
          document.getElementById('formVueloContainer').style.display = 'none';
          
          // Establecer valores
          document.getElementById('asientos_disponibles').value = asientosDisponibles;
          document.getElementById('asientos_disponibles').max = capacidad;
          document.getElementById('max_capacidad').textContent = capacidad;
          document.getElementById('precio_actualizar').value = precio;
          
          // Configurar acción del formulario
          form.action = `/proveedor/vuelo/${vueloId}/actualizar`;
          
          container.style.display = 'block';
          
          // Configurar botón cancelar
          document.getElementById('btnCancelarActualizarVuelo').onclick = function() {
            container.style.display = 'none';
          };
        }
        
        // Eliminar vuelo
        function eliminarVuelo(vueloId, rutaVuelo) {
          if (confirm(`¿Está seguro que desea eliminar el vuelo ${rutaVuelo}?`)) {
            fetch(`/proveedor/vuelo/${vueloId}/eliminar`, {
              method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                alert('Vuelo eliminado con éxito');
                // Recargar tabla de vuelos
                const aerolineaId = document.getElementById('formVuelo').action.split('/')[3];
                gestionarVuelos(aerolineaId, document.getElementById('aerolinea_nombre_vuelos').textContent);
              } else {
                alert('Error al eliminar el vuelo: ' + data.message);
              }
            });
          }
        }
      

        // JavaScript para gestionar modales de paquetes turísticos
       
          // Para editar paquete
          function editarPaquete(paqueteId, paquete) {
            document.getElementById('edit_nombre_paquete').value = paquete.nombre;
            document.getElementById('edit_descripcion_paquete').value = paquete.descripcion;
            document.getElementById('edit_destino_id').value = paquete.destino_id;
            document.getElementById('edit_duracion').value = paquete.duracion;
            document.getElementById('edit_fecha_inicio').value = paquete.fecha_inicio;
            document.getElementById('edit_fecha_fin').value = paquete.fecha_fin;
            document.getElementById('edit_precio_base').value = paquete.precio_base;
            document.getElementById('edit_capacidad').value = paquete.capacidad;
            document.getElementById('edit_disponibles').value = paquete.disponibles;
            
            // Checkboxes
            document.getElementById('edit_incluye_vuelo').checked = paquete.incluye_vuelo;
            document.getElementById('edit_incluye_hotel').checked = paquete.incluye_hotel;
            document.getElementById('edit_incluye_traslados').checked = paquete.incluye_traslados;
            document.getElementById('edit_incluye_comidas').checked = paquete.incluye_comidas;
            document.getElementById('edit_incluye_excursiones').checked = paquete.incluye_excursiones;
            document.getElementById('edit_incluye_guia').checked = paquete.incluye_guia;
            
            const formEditarPaquete = document.getElementById('formEditarPaquete');
            formEditarPaquete.action = `/proveedor/paquete/${paqueteId}/editar`;
            
            const modal = new bootstrap.Modal(document.getElementById('editarPaqueteModal'));
            modal.show();
          }
          
          // Para eliminar paquete
          function eliminarPaquete(paqueteId, nombre) {
            document.getElementById('paquete_nombre_eliminar').textContent = nombre;
            document.getElementById('formEliminarPaquete').action = `/proveedor/paquete/${paqueteId}/eliminar`;
            
            const modal = new bootstrap.Modal(document.getElementById('eliminarPaqueteModal'));
            modal.show();
          }
          
          // Para ver detalle del paquete
          function verDetallePaquete(paqueteId) {
            // Cargar detalles via AJAX
            fetch(`/proveedor/paquete/${paqueteId}/detalle-json`)
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  const paquete = data.paquete;
                  
                  // Información general
                  document.getElementById('detalle_nombre').textContent = paquete.nombre;
                  document.getElementById('detalle_destino').textContent = paquete.destino_nombre;
                  document.getElementById('detalle_duracion').textContent = `${paquete.duracion} días`;
                  
                  // Formatear fechas
                  const fechaInicio = new Date(paquete.fecha_inicio).toLocaleDateString();
                  const fechaFin = new Date(paquete.fecha_fin).toLocaleDateString();
                  document.getElementById('detalle_fechas').textContent = `${fechaInicio} al ${fechaFin}`;
                  
                  document.getElementById('detalle_precio').textContent = `$${parseFloat(paquete.precio_base).toFixed(2)}`;
                  document.getElementById('detalle_descripcion').textContent = paquete.descripcion;
                  
                  // Disponibilidad
                  document.getElementById('detalle_capacidad').textContent = paquete.capacidad;
                  const vendidas = paquete.capacidad - paquete.disponibles;
                  document.getElementById('detalle_vendidas').textContent = vendidas;
                  document.getElementById('detalle_disponibles').textContent = paquete.disponibles;
                  
                  // Calcular porcentaje de ocupación
                  const porcentajeOcupacion = (vendidas / paquete.capacidad) * 100;
                  let badgeClass = 'bg-success';
                  if (porcentajeOcupacion > 80) badgeClass = 'bg-danger';
                  else if (porcentajeOcupacion > 50) badgeClass = 'bg-warning text-dark';
                  
                  document.getElementById('detalle_ocupacion').innerHTML = 
                    `<div class="progress" style="height: 20px;">
                      <div class="progress-bar ${badgeClass}" role="progressbar" 
                        style="width: ${porcentajeOcupacion}%;" 
                        aria-valuenow="${porcentajeOcupacion}" 
                        aria-valuemin="0" 
                        aria-valuemax="100">${porcentajeOcupacion.toFixed(0)}%</div>
                    </div>`;
                  
                  // Actualizar incluye
                  function updateIncluye(id, incluye) {
                    const elemento = document.getElementById(id);
                    const badge = elemento.querySelector('.badge');
                    
                    if (incluye) {
                      elemento.classList.add('list-group-item-success');
                      badge.textContent = '✓';
                      badge.className = 'badge bg-success ms-1';
                    } else {
                      elemento.classList.remove('list-group-item-success');
                      badge.textContent = '✗';
                      badge.className = 'badge bg-secondary ms-1';
                    }
                  }
                  
                  updateIncluye('detalle_vuelo', paquete.incluye_vuelo);
                  updateIncluye('detalle_hotel', paquete.incluye_hotel);
                  updateIncluye('detalle_traslados', paquete.incluye_traslados);
                  updateIncluye('detalle_comidas', paquete.incluye_comidas);
                  updateIncluye('detalle_excursiones', paquete.incluye_excursiones);
                  updateIncluye('detalle_guia', paquete.incluye_guia);
                  
                  // Reservas
                  if (data.reservas && data.reservas.length > 0) {
                    document.getElementById('sin_reservas').style.display = 'none';
                    const tablaReservas = document.getElementById('tabla_reservas');
                    tablaReservas.style.display = 'table';
                    
                    const tbody = tablaReservas.querySelector('tbody');
                    tbody.innerHTML = '';
                    
                    data.reservas.forEach(reserva => {
                      const fila = tbody.insertRow();
                      
                      fila.insertCell(0).textContent = reserva.cliente_nombre;
                      
                      const fechaReserva = new Date(reserva.fecha_reserva).toLocaleDateString();
                      fila.insertCell(1).textContent = fechaReserva;
                      
                      fila.insertCell(2).textContent = reserva.cantidad_personas;
                      
                      // Estado con badge
                      const celdaEstado = fila.insertCell(3);
                      let estadoBadge = 'bg-warning text-dark';
                      if (reserva.estado === 'Confirmada') estadoBadge = 'bg-success';
                      else if (reserva.estado === 'Cancelada') estadoBadge = 'bg-danger';
                      
                      celdaEstado.innerHTML = `<span class="badge ${estadoBadge}">${reserva.estado}</span>`;
                      
                      fila.insertCell(4).textContent = `$${parseFloat(reserva.total).toFixed(2)}`;
                    });
                  } else {
                    document.getElementById('sin_reservas').style.display = 'block';
                    document.getElementById('tabla_reservas').style.display = 'none';
                  }
                }
              });
            
            const modal = new bootstrap.Modal(document.getElementById('detallePaqueteModal'));
            modal.show();
          }
        
          // Validación dinámica de fechas para no tener fechas de fin anteriores a las de inicio
          document.addEventListener('DOMContentLoaded', function() {
            // Para formulario de creación
            const fechaInicio = document.getElementById('fecha_inicio');
            const fechaFin = document.getElementById('fecha_fin');
            const duracion = document.getElementById('duracion');
            
            if (fechaInicio && fechaFin && duracion) {
              fechaInicio.addEventListener('change', function() {
                if (fechaInicio.value) {
                  // Establecer fecha mínima para fecha_fin
                  fechaFin.min = fechaInicio.value;
                  
                  // Actualizar fecha_fin según duración
                  if (duracion.value) {
                    const inicio = new Date(fechaInicio.value);
                    inicio.setDate(inicio.getDate() + parseInt(duracion.value));
                    const finFormatted = inicio.toISOString().split('T')[0];
                    fechaFin.value = finFormatted;
                  }
                }
              });
              
              duracion.addEventListener('change', function() {
                if (fechaInicio.value && duracion.value) {
                  const inicio = new Date(fechaInicio.value);
                  inicio.setDate(inicio.getDate() + parseInt(duracion.value));
                  const finFormatted = inicio.toISOString().split('T')[0];
                  fechaFin.value = finFormatted;
                }
              });
            }
            
            // Para formulario de edición (mismo comportamiento)
            const editFechaInicio = document.getElementById('edit_fecha_inicio');
            const editFechaFin = document.getElementById('edit_fecha_fin');
            const editDuracion = document.getElementById('edit_duracion');
            
            if (editFechaInicio && editFechaFin && editDuracion) {
              editFechaInicio.addEventListener('change', function() {
                if (editFechaInicio.value) {
                  editFechaFin.min = editFechaInicio.value;
                  
                  if (editDuracion.value) {
                    const inicio = new Date(editFechaInicio.value);
                    inicio.setDate(inicio.getDate() + parseInt(editDuracion.value));
                    const finFormatted = inicio.toISOString().split('T')[0];
                    editFechaFin.value = finFormatted;
                  }
                }
              });
              
              editDuracion.addEventListener('change', function() {
                if (editFechaInicio.value && editDuracion.value) {
                  const inicio = new Date(editFechaInicio.value);
                  inicio.setDate(inicio.getDate() + parseInt(editDuracion.value));
                  const finFormatted = inicio.toISOString().split('T')[0];
                  editFechaFin.value = finFormatted;
                }
              });
            }
          });
    