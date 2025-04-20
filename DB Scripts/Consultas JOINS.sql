-- CONSULTAS JOINS 

-- Usar la base de datos
USE CRUZERD;

-- Paquetes con su hotel y vuelo incluido
SELECT 
    p.id AS paquete_id,
    p.nombre AS paquete_nombre,
    p.precio AS paquete_precio,
    h.nombre AS hotel_nombre,
    h.ciudad AS hotel_ciudad,
    h.estrellas AS hotel_estrellas,
    a1.nombre AS aeropuerto_origen,
    a2.nombre AS aeropuerto_destino,
    v.fecha_salida,
    v.fecha_llegada,
    al.nombre AS aerolinea
FROM paquete p
LEFT JOIN hotel h ON p.hotel_id = h.id
LEFT JOIN vuelo v ON p.vuelo_id = v.id
LEFT JOIN aerolinea al ON v.aerolinea_id = al.id
LEFT JOIN aeropuerto a1 ON v.origen_id = a1.id
LEFT JOIN aeropuerto a2 ON v.destino_id = a2.id;

-- Reservas completas con información de cliente y paquete
SELECT 
    r.id AS reserva_id,
    r.codigo_reserva,
    r.fecha_reserva,
    r.estado,
    u.nombre AS cliente_nombre,
    u.email AS cliente_email,
    c.telefono AS cliente_telefono,
    p.nombre AS paquete_nombre,
    p.precio AS paquete_precio,
    r.precio_total,
    r.fecha_inicio,
    r.fecha_fin
FROM reserva r
JOIN cliente c ON r.cliente_id = c.id
JOIN usuario u ON c.usuario_id = u.id
JOIN paquete p ON r.paquete_id = p.id;

-- Vuelos con información de aerolínea y aeropuertos
SELECT 
    v.id AS vuelo_id,
    v.fecha_salida,
    v.fecha_llegada,
    v.asientos_disponibles,
    v.precio,
    al.nombre AS aerolinea,
    al.codigo AS codigo_aerolinea,
    a1.nombre AS aeropuerto_origen,
    a1.codigo AS codigo_origen,
    a1.ciudad AS ciudad_origen,
    a2.nombre AS aeropuerto_destino,
    a2.codigo AS codigo_destino,
    a2.ciudad AS ciudad_destino
FROM vuelo v
JOIN aerolinea al ON v.aerolinea_id = al.id
JOIN aeropuerto a1 ON v.origen_id = a1.id
JOIN aeropuerto a2 ON v.destino_id = a2.id;

-- Promociones aplicables a paquetes específicos
SELECT 
    pr.id AS promocion_id,
    pr.nombre AS promocion_nombre,
    pr.porcentaje_descuento,
    pr.fecha_inicio,
    pr.fecha_fin,
    p.id AS paquete_id,
    p.nombre AS paquete_nombre,
    p.precio AS precio_original,
    (p.precio - (p.precio * pr.porcentaje_descuento / 100)) AS precio_con_descuento
FROM promocion pr
JOIN paquete p ON pr.paquete_id = p.id
WHERE pr.activa = TRUE AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin;

-- Habitaciones reservadas con información de hotel y cliente
SELECT 
    rh.id AS reserva_habitacion_id,
    rh.fecha_inicio,
    rh.fecha_fin,
    hab.tipo AS tipo_habitacion,
    hab.capacidad,
    hab.precio AS precio_habitacion,
    h.nombre AS hotel_nombre,
    h.ciudad AS hotel_ciudad,
    u.nombre AS cliente_nombre,
    u.email AS cliente_email,
    c.telefono AS cliente_telefono,
    r.codigo_reserva
FROM reserva_habitacion rh
JOIN habitacion hab ON rh.habitacion_id = hab.id
JOIN hotel h ON hab.hotel_id = h.id
JOIN reserva r ON rh.reserva_id = r.id
JOIN cliente c ON r.cliente_id = c.id
JOIN usuario u ON c.usuario_id = u.id;