-- MODIFICACIONES (5)

-- Usar la base de datos
USE CRUZERD;

-- 1. Actualizar el precio de un paquete
UPDATE paquete
SET precio = 1300.00, descripcion = 'Disfruta de una semana de lujo en las playas de Cancún'
WHERE id = 1;

-- 2. Cambiar el estado de una reserva
UPDATE reserva
SET estado = 'confirmada', precio_total = 850.00
WHERE codigo_reserva = 'RES002';

-- 3. Actualizar la disponibilidad de habitaciones en un hotel
UPDATE habitacion
SET disponible = FALSE
WHERE hotel_id = 1 AND tipo = 'Suite';

-- 4. Modificar los datos de un usuario
UPDATE usuario
SET email = 'juan.perez@example.com', password = '$2a$10$qJhS9HmCp5SzCvJSI8nRz.czGq7m4Yb9ZrQaSJG.WPYxG/iLWHYex'
WHERE id = 1;

-- 5. Actualizar una promoción
UPDATE promocion
SET porcentaje_descuento = 30.00, fecha_fin = '2025-05-31 23:59:59'
WHERE paquete_id = 1;