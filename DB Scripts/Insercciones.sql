-- INSERCIONES (20)

-- Usar la base de datos
USE CRUZERD;

-- Inserción de usuarios (5)
INSERT INTO usuario (nombre, email, password, rol) VALUES
('Juan Pérez', 'juan@example.com', '$2a$10$xJhS9HmCp5SzCvJSI8nRz.czGq7m4Yb9ZrQaSJG.WPYxG/iLWHYey', 'cliente'),
('Maria García', 'maria@example.com', '$2a$10$nOP4rWr5JzLYDOrh1wFUse8gJqz5rhrV5t.p9jtCM9H7A6wPwEOmK', 'cliente'),
('Carlos Rodríguez', 'carlos@example.com', '$2a$10$5Jt9Pq6JqY9g7l3Gc6rV7ORzDq5U6lLrYG5j2j6YCEfEz7bGgGyYa', 'agente'),
('Travel Supply Inc', 'travel@supply.com', '$2a$10$YtQOv9rw4HZ3QXwP9XmxDeIHvJ5G4QzHn.vZmEHzQ8.QlnW2BAWV2', 'proveedor'),
('Sky Airways', 'info@skyairways.com', '$2a$10$hLt9G4nKrO9LGcRdT4xdE.vwT5nQUAljOqkzO8qHs1AYQLjbJ0fHe', 'proveedor');

-- Inserción de clientes (2)
INSERT INTO cliente (usuario_id, telefono, direccion) VALUES
(1, '+34612345678', 'Calle Principal 123, Madrid, España'),
(2, '+34698765432', 'Avenida Central 45, Barcelona, España');

-- Inserción de agentes (1)
INSERT INTO agente (usuario_id, codigo_empleado) VALUES
(3, 'AG001');

-- Inserción de proveedores (2)
INSERT INTO proveedor (usuario_id, tipo, nombre_empresa) VALUES
(4, 'hotelero', 'Travel Supply Inc'),
(5, 'aerolínea', 'Sky Airways');

-- Inserción de hoteles (2)
INSERT INTO hotel (nombre, direccion, ciudad, pais, estrellas, proveedor_id) VALUES
('Grand Plaza', 'Paseo de la Castellana 200', 'Madrid', 'España', 5, 1),
('Seaside Resort', 'Playa Bonita 45', 'Cancún', 'México', 4, 1);

-- Inserción de habitaciones (3)
INSERT INTO habitacion (hotel_id, tipo, capacidad, precio, disponible) VALUES
(1, 'Suite', 2, 200.00, TRUE),
(1, 'Doble', 2, 150.00, TRUE),
(2, 'Familiar', 4, 250.00, TRUE);

-- Inserción de aeropuertos (3)
INSERT INTO aeropuerto (nombre, codigo, ciudad, pais) VALUES
('Adolfo Suárez Madrid-Barajas', 'MAD', 'Madrid', 'España'),
('Cancún International', 'CUN', 'Cancún', 'México'),
('Barcelona-El Prat', 'BCN', 'Barcelona', 'España');

-- Inserción de aerolíneas (1)
INSERT INTO aerolinea (nombre, codigo, proveedor_id) VALUES
('Sky Airways', 'SKY', 2);

-- Inserción de vuelos (2)
INSERT INTO vuelo (aerolinea_id, origen_id, destino_id, fecha_salida, fecha_llegada, capacidad, asientos_disponibles, precio) VALUES
(1, 1, 2, '2025-05-15 08:00:00', '2025-05-15 12:30:00', 180, 120, 350.00),
(1, 2, 1, '2025-05-22 14:00:00', '2025-05-22 18:30:00', 180, 150, 320.00);

-- Inserción de paquetes (2)
INSERT INTO paquete (nombre, descripcion, precio, activo, duracion, hotel_id, vuelo_id) VALUES
('Escapada a Cancún', 'Disfruta de una semana en las playas de Cancún', 1200.00, TRUE, 7, 2, 1),
('Madrid Cultural', 'Descubre la capital española', 800.00, TRUE, 4, 1, 2);

-- Inserción de promociones (1)
INSERT INTO promocion (paquete_id, nombre, descripcion, porcentaje_descuento, fecha_inicio, fecha_fin, activa) VALUES
(1, 'Verano Anticipado', 'Reserva con antelación y ahorra', 25.00, '2025-01-01 00:00:00', '2025-04-30 23:59:59', TRUE);

-- Inserción de reservas (2)
INSERT INTO reserva (cliente_id, paquete_id, agente_id, fecha_inicio, fecha_fin, precio_total, estado, codigo_reserva) VALUES
(1, 1, 1, '2025-05-15 00:00:00', '2025-05-22 00:00:00', 900.00, 'confirmada', 'RES001'),
(2, 2, 1, '2025-06-10 00:00:00', '2025-06-14 00:00:00', 800.00, 'pendiente', 'RES002');

-- Inserción de reservas de habitaciones (2)
INSERT INTO reserva_habitacion (reserva_id, habitacion_id, fecha_inicio, fecha_fin, precio) VALUES
(1, 3, '2025-05-15 14:00:00', '2025-05-22 12:00:00', 250.00),
(2, 1, '2025-06-10 14:00:00', '2025-06-14 12:00:00', 200.00);

-- Inserción de reservas de vuelos (2)
INSERT INTO reserva_vuelo (reserva_id, vuelo_id, asientos, precio) VALUES
(1, 1, 2, 700.00),
(2, 2, 1, 320.00);

-- Inserción de pagos (2)
INSERT INTO pago (reserva_id, monto, metodo, estado, referencia) VALUES
(1, 900.00, 'tarjeta', 'completado', 'PAY001'),
(2, 400.00, 'transferencia', 'parcial', 'PAY002');