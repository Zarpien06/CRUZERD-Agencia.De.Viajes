-- ELIMINACIONES (5)

-- Usar la base de datos
USE CRUZERD;

-- 1. Eliminar un pago
DELETE FROM pago 
WHERE referencia = 'PAY002';

-- 2. Eliminar una promoción expirada
DELETE FROM promocion
WHERE fecha_fin < CURRENT_TIMESTAMP AND activa = FALSE;

-- 3. Eliminar habitaciones no disponibles de un hotel específico
DELETE FROM habitacion
WHERE hotel_id = 2 AND disponible = FALSE;

-- 4. Eliminar reservas canceladas antiguas
DELETE FROM reserva
WHERE estado = 'cancelada' AND fecha_reserva < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 YEAR);

-- 5. Eliminar vuelos pasados sin reservas
DELETE FROM vuelo
WHERE fecha_llegada < CURRENT_TIMESTAMP 
AND id NOT IN (SELECT vuelo_id FROM reserva_vuelo);