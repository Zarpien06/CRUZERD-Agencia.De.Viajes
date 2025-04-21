
document.addEventListener('DOMContentLoaded', function () {
    var editModal = document.getElementById('editClienteModal');
    editModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;

        // Obtener valores del botón
        var id = button.getAttribute('data-id');
        var nombre = button.getAttribute('data-nombre');
        var email = button.getAttribute('data-email');
        var telefono = button.getAttribute('data-telefono');
        var direccion = button.getAttribute('data-direccion');

        // Insertar en los inputs del formulario
        editModal.querySelector('#edit_cliente_id').value = id;
        editModal.querySelector('#edit_nombre').value = nombre;
        editModal.querySelector('#edit_email').value = email;
        editModal.querySelector('#edit_telefono').value = telefono;
        editModal.querySelector('#edit_direccion').value = direccion;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Suponiendo que cada botón para ver cliente tenga una clase "view-cliente-btn" y un data-id
    document.querySelectorAll('.view-cliente-btn').forEach(button => {
        button.addEventListener('click', function () {
            const clienteId = this.getAttribute('data-id');

            fetch(`/cliente/detalles/${clienteId}`)
                .then(response => response.json())
                .then(data => {
                    // Rellenar los detalles del cliente
                    const details = `
                        <p><strong>Nombre:</strong> ${data.nombre}</p>
                        <p><strong>Email:</strong> ${data.email}</p>
                        <p><strong>Teléfono:</strong> ${data.telefono}</p>
                        <p><strong>Documento:</strong> ${data.documento}</p>
                    `;
                    document.getElementById('cliente-details').innerHTML = details;

                    // Rellenar la tabla de reservas
                    const reservas = data.reservas.map(r => `
                        <tr>
                            <td>${r.codigo}</td>
                            <td>${r.paquete}</td>
                            <td>${r.fecha_inicio} - ${r.fecha_fin}</td>
                            <td>$${r.total}</td>
                            <td>${r.estado}</td>
                        </tr>
                    `).join('');
                    document.getElementById('cliente-reservas-body').innerHTML = reservas;

                    // Asignar acciones a los botones
                    document.getElementById('edit-cliente-btn').onclick = function () {
                        window.location.href = `/cliente/editar/${clienteId}`;
                    };

                    document.getElementById('nueva-reserva-cliente-btn').onclick = function () {
                        window.location.href = `/reserva/nueva/${clienteId}`;
                    };

                    // Mostrar el modal
                    const modal = new bootstrap.Modal(document.getElementById('viewClienteModal'));
                    modal.show();
                });
        });
    });
});



