-- SUBCONSULTAS 

-- Usar la base de datos
USE CRUZERD;

-- Paquetes con precio superior al promedio
SELECT 
    id,
    nombre,
    precio,
    duracion
FROM paquete
WHERE precio > (SELECT AVG(precio) FROM paquete)
ORDER BY precio DESC;

-- Clientes que no han viajado en el último año
SELECT 
    u.id,
    u.nombre,
    u.email,
    c.telefono
FROM usuario u
JOIN cliente c ON u.id = c.usuario_id
WHERE c.id NOT IN (
    SELECT cliente_id
    FROM reserva
    WHERE fecha_fin >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 YEAR)
    AND estado IN ('completada', 'confirmada')
);

-- Vuelos con ocupación superior al 80%
SELECT 
    v.id,
    a1.codigo AS origen,
    a2.codigo AS destino,
    v.fecha_salida,
    v.capacidad,
    v.asientos_disponibles,
    ((v.capacidad - v.asientos_disponibles) * 100.0 / v.capacidad) AS porcentaje_ocupacion
FROM vuelo v
JOIN aeropuerto a1 ON v.origen_id = a1.id
JOIN aeropuerto a2 ON v.destino_id = a2.id
WHERE ((v.capacidad - v.asientos_disponibles) * 100.0 / v.capacidad) > 80;

-- Hoteles con todas sus habitaciones reservadas en una fecha específica
SELECT 
    h.id,
    h.nombre,
    h.ciudad
FROM hotel h
WHERE NOT EXISTS (
    SELECT 1
    FROM habitacion hab
    WHERE hab.hotel_id = h.id
    AND hab.disponible = TRUE
    AND hab.id NOT IN (
        SELECT rh.habitacion_id
        FROM reserva_habitacion rh
        WHERE '2025-05-20' BETWEEN DATE(rh.fecha_inicio) AND DATE(rh.fecha_fin)
    )
);

-- Promociones que no han sido aplicadas (no hay reservas de paquetes con estas promociones)
SELECT 
    pr.id,
    pr.nombre,
    pr.porcentaje_descuento,
    p.nombre AS paquete
FROM promocion pr
JOIN paquete p ON pr.paquete_id = p.id
WHERE pr.activa = TRUE 
AND NOT EXISTS (
    SELECT 1
    FROM reserva r
    WHERE r.paquete_id = p.id
    AND r.fecha_reserva BETWEEN pr.fecha_inicio AND pr.fecha_fin
);