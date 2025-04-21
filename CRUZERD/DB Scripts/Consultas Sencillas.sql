-- CONSULTAS SENCILLAS 

-- Usar la base de datos
USE CRUZERD;

-- Paquetes con descuento mayor al 20%
SELECT 
    p.nombre AS paquete,
    p.precio AS precio_original,
    pr.porcentaje_descuento,
    (p.precio - (p.precio * pr.porcentaje_descuento / 100)) AS precio_con_descuento
FROM paquete p
JOIN promocion pr ON p.id = pr.paquete_id
WHERE pr.porcentaje_descuento > 20 AND pr.activa = TRUE;

-- Reservas realizadas en el último mes
SELECT 
    r.id,
    r.codigo_reserva,
    u.nombre AS cliente,
    p.nombre AS paquete,
    r.fecha_reserva,
    r.precio_total,
    r.estado
FROM reserva r
JOIN cliente c ON r.cliente_id = c.id
JOIN usuario u ON c.usuario_id = u.id
JOIN paquete p ON r.paquete_id = p.id
WHERE r.fecha_reserva >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 MONTH);

-- Vuelos con asientos disponibles
SELECT 
    v.id,
    al.nombre AS aerolinea,
    a1.ciudad AS origen,
    a2.ciudad AS destino,
    v.fecha_salida,
    v.fecha_llegada,
    v.capacidad,
    v.asientos_disponibles,
    v.precio
FROM vuelo v
JOIN aerolinea al ON v.aerolinea_id = al.id
JOIN aeropuerto a1 ON v.origen_id = a1.id
JOIN aeropuerto a2 ON v.destino_id = a2.id
WHERE v.asientos_disponibles > 0
ORDER BY v.fecha_salida;

-- Hoteles con valoración mayor a 4 estrellas
SELECT 
    h.id,
    h.nombre,
    h.ciudad,
    h.pais,
    h.estrellas,
    p.nombre_empresa AS proveedor
FROM hotel h
JOIN proveedor p ON h.proveedor_id = p.id
WHERE h.estrellas > 4;

-- Clientes con más de 5 reservas
SELECT 
    u.nombre AS cliente,
    u.email,
    c.telefono,
    COUNT(r.id) AS total_reservas
FROM cliente c
JOIN usuario u ON c.usuario_id = u.id
JOIN reserva r ON c.id = r.cliente_id
GROUP BY c.id, u.nombre, u.email, c.telefono
HAVING COUNT(r.id) > 5;