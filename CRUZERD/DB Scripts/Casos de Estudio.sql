-- CASO DE ESTUDIO 

-- --------------------------------------------------
-- 1. CONSULTAS DE GESTIÓN DE USUARIOS
-- --------------------------------------------------

-- 1.1 Listado completo de usuarios con sus roles
SELECT 
    u.id, 
    u.nombre, 
    u.email, 
    u.rol, 
    u.fecha_registro
FROM usuario u
ORDER BY u.fecha_registro DESC;

-- 1.2 Detalle completo de clientes
SELECT 
    u.id,
    u.nombre,
    u.email,
    c.telefono,
    c.direccion,
    COUNT(r.id) AS total_reservas,
    SUM(CASE WHEN r.estado = 'confirmada' OR r.estado = 'completada' THEN 1 ELSE 0 END) AS reservas_activas
FROM usuario u
JOIN cliente c ON u.id = c.usuario_id
LEFT JOIN reserva r ON c.id = r.cliente_id
GROUP BY u.id, u.nombre, u.email, c.telefono, c.direccion
ORDER BY total_reservas DESC;

-- 1.3 Listado de agentes con métricas de rendimiento
SELECT 
    u.id,
    u.nombre,
    u.email,
    a.codigo_empleado,
    COUNT(r.id) AS reservas_gestionadas,
    SUM(r.precio_total) AS volumen_ventas,
    ROUND(AVG(r.precio_total), 2) AS valor_promedio_reserva
FROM usuario u
JOIN agente a ON u.id = a.usuario_id
LEFT JOIN reserva r ON a.id = r.agente_id
GROUP BY u.id, u.nombre, u.email, a.codigo_empleado
ORDER BY volumen_ventas DESC;

-- --------------------------------------------------
-- 2. CONSULTAS DE INVENTARIO Y DISPONIBILIDAD
-- --------------------------------------------------

-- 2.1 Disponibilidad de habitaciones por hotel en fechas específicas
CREATE PROCEDURE check_room_availability(IN check_date DATE)

    SELECT 
        h.id AS hotel_id,
        h.nombre AS hotel_nombre,
        h.ciudad,
        h.pais,
        h.estrellas,
        COUNT(hab.id) AS habitaciones_totales,
        SUM(CASE WHEN hab.disponible = TRUE AND hab.id NOT IN (
            SELECT rh.habitacion_id
            FROM reserva_habitacion rh
            WHERE check_date BETWEEN DATE(rh.fecha_inicio) AND DATE(rh.fecha_fin)
        ) THEN 1 ELSE 0 END) AS habitaciones_disponibles
    FROM hotel h
    JOIN habitacion hab ON h.id = hab.hotel_id
    GROUP BY h.id, h.nombre, h.ciudad, h.pais, h.estrellas
    ORDER BY h.estrellas DESC, habitaciones_disponibles DESC;


-- 2.2 Disponibilidad de vuelos entre dos destinos
CREATE PROCEDURE check_flight_availability(IN origen VARCHAR(100), IN destino VARCHAR(100), IN fecha_viaje DATE)

    SELECT 
        v.id,
        al.nombre AS aerolinea,
        a1.codigo AS origen,
        a2.codigo AS destino,
        v.fecha_salida,
        v.fecha_llegada,
        TIMEDIFF(v.fecha_llegada, v.fecha_salida) AS duracion,
        v.asientos_disponibles,
        v.precio
    FROM vuelo v
    JOIN aerolinea al ON v.aerolinea_id = al.id
    JOIN aeropuerto a1 ON v.origen_id = a1.id
    JOIN aeropuerto a2 ON v.destino_id = a2.id
    WHERE a1.ciudad = origen 
    AND a2.ciudad = destino
    AND DATE(v.fecha_salida) = fecha_viaje
    AND v.asientos_disponibles > 0
    ORDER BY v.precio ASC;


-- --------------------------------------------------
-- 3. CONSULTAS DE PAQUETES Y PROMOCIONES
-- --------------------------------------------------

-- 3.1 Detalle completo de paquetes turísticos
SELECT 
    p.id,
    p.nombre,
    p.descripcion,
    p.precio,
    p.duracion,
    h.nombre AS hotel,
    h.ciudad AS destino,
    h.estrellas,
    a1.codigo AS aeropuerto_origen,
    a2.codigo AS aeropuerto_destino,
    al.nombre AS aerolinea,
    v.fecha_salida,
    v.fecha_llegada,
    COALESCE(pr.porcentaje_descuento, 0) AS descuento,
    CASE 
        WHEN pr.id IS NOT NULL AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
        THEN ROUND(p.precio - (p.precio * pr.porcentaje_descuento / 100), 2)
        ELSE p.precio
    END AS precio_final
FROM paquete p
LEFT JOIN hotel h ON p.hotel_id = h.id
LEFT JOIN vuelo v ON p.vuelo_id = v.id
LEFT JOIN aerolinea al ON v.aerolinea_id = al.id
LEFT JOIN aeropuerto a1 ON v.origen_id = a1.id
LEFT JOIN aeropuerto a2 ON v.destino_id = a2.id
LEFT JOIN promocion pr ON p.id = pr.paquete_id AND pr.activa = TRUE 
    AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
WHERE p.activo = TRUE
ORDER BY precio_final ASC;

-- 3.2 Ranking de paquetes más vendidos
SELECT 
    p.id,
    p.nombre,
    h.ciudad AS destino,
    p.precio,
    COUNT(r.id) AS total_ventas,
    SUM(r.precio_total) AS ingresos_totales,
    ROUND(AVG(r.precio_total), 2) AS precio_promedio_venta
FROM paquete p
LEFT JOIN hotel h ON p.hotel_id = h.id
LEFT JOIN reserva r ON p.id = r.paquete_id AND (r.estado = 'confirmada' OR r.estado = 'completada')
GROUP BY p.id, p.nombre, h.ciudad, p.precio
ORDER BY total_ventas DESC;

-- --------------------------------------------------
-- 4. CONSULTAS DE RESERVAS Y VENTAS
-- --------------------------------------------------

-- 4.1 Listado detallado de reservas
SELECT 
    r.id,
    r.codigo_reserva,
    r.fecha_reserva,
    u.nombre AS cliente,
    u.email,
    c.telefono,
    ua.nombre AS agente,
    a.codigo_empleado,
    p.nombre AS paquete,
    h.nombre AS hotel,
    h.ciudad AS destino,
    v.fecha_salida,
    v.fecha_llegada,
    r.fecha_inicio,
    r.fecha_fin,
    r.precio_total,
    r.estado
FROM reserva r
JOIN cliente c ON r.cliente_id = c.id
JOIN usuario u ON c.usuario_id = u.id
LEFT JOIN agente a ON r.agente_id = a.id
LEFT JOIN usuario ua ON a.usuario_id = ua.id
JOIN paquete p ON r.paquete_id = p.id
LEFT JOIN hotel h ON p.hotel_id = h.id
LEFT JOIN vuelo v ON p.vuelo_id = v.id
ORDER BY r.fecha_reserva DESC;

-- 4.2 Seguimiento de pagos por reserva
SELECT 
    r.codigo_reserva,
    u.nombre AS cliente,
    p.nombre AS paquete,
    r.precio_total AS monto_reserva,
    SUM(pg.monto) AS monto_pagado,
    r.precio_total - SUM(COALESCE(pg.monto, 0)) AS saldo_pendiente,
    ROUND((SUM(COALESCE(pg.monto, 0)) * 100.0) / r.precio_total, 2) AS porcentaje_pagado,
    MAX(pg.fecha) AS ultimo_pago,
    GROUP_CONCAT(DISTINCT pg.metodo ORDER BY pg.fecha SEPARATOR ', ') AS metodos_pago,
    r.estado
FROM reserva r
JOIN cliente c ON r.cliente_id = c.id
JOIN usuario u ON c.usuario_id = u.id
JOIN paquete p ON r.paquete_id = p.id
LEFT JOIN pago pg ON r.id = pg.reserva_id
GROUP BY r.codigo_reserva, u.nombre, p.nombre, r.precio_total, r.estado
ORDER BY saldo_pendiente DESC;

-- --------------------------------------------------
-- 5. CONSULTAS DE ANÁLISIS Y BUSINESS INTELLIGENCE
-- --------------------------------------------------

-- 5.1 Segmentación de clientes por valor
SELECT 
    'Premium' AS segmento,
    COUNT(c.id) AS clientes,
    ROUND(AVG(total_gastado), 2) AS gasto_promedio,
    ROUND(AVG(num_reservas), 2) AS reservas_promedio
FROM (
    SELECT 
        c.id,
        SUM(r.precio_total) AS total_gastado,
        COUNT(r.id) AS num_reservas
    FROM cliente c
    JOIN reserva r ON c.id = r.cliente_id
    WHERE r.estado IN ('confirmada', 'completada')
    GROUP BY c.id
    HAVING SUM(r.precio_total) > 5000
) AS premium_customers

UNION ALL

SELECT 
    'Regular' AS segmento,
    COUNT(c.id) AS clientes,
    ROUND(AVG(total_gastado), 2) AS gasto_promedio,
    ROUND(AVG(num_reservas), 2) AS reservas_promedio
FROM (
    SELECT 
        c.id,
        SUM(r.precio_total) AS total_gastado,
        COUNT(r.id) AS num_reservas
    FROM cliente c
    JOIN reserva r ON c.id = r.cliente_id
    WHERE r.estado IN ('confirmada', 'completada')
    GROUP BY c.id
    HAVING SUM(r.precio_total) BETWEEN 2000 AND 5000
) AS regular_customers

UNION ALL

SELECT 
    'Básico' AS segmento,
    COUNT(c.id) AS clientes,
    ROUND(AVG(total_gastado), 2) AS gasto_promedio,
    ROUND(AVG(num_reservas), 2) AS reservas_promedio
FROM (
    SELECT 
        c.id,
        SUM(r.precio_total) AS total_gastado,
        COUNT(r.id) AS num_reservas
    FROM cliente c
    JOIN reserva r ON c.id = r.cliente_id
    WHERE r.estado IN ('confirmada', 'completada')
    GROUP BY c.id
    HAVING SUM(r.precio_total) < 2000
) AS basic_customers;

-- --------------------------------------------------
-- 6. VISTAS ÚTILES PARA EL SISTEMA
-- --------------------------------------------------

-- 6.1 Vista de paquetes disponibles con descuentos aplicados
CREATE OR REPLACE VIEW v_paquetes_disponibles AS
SELECT 
    p.id,
    p.nombre,
    p.descripcion,
    p.duracion,
    h.nombre AS hotel,
    h.ciudad AS destino,
    h.pais,
    h.estrellas,
    al.nombre AS aerolinea,
    a1.ciudad AS origen,
    a2.ciudad AS destino_ciudad,
    v.fecha_salida,
    v.fecha_llegada,
    p.precio AS precio_original,
    COALESCE(pr.porcentaje_descuento, 0) AS descuento,
    CASE 
        WHEN pr.id IS NOT NULL AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
        THEN p.precio - (p.precio * pr.porcentaje_descuento / 100)
        ELSE p.precio
    END AS precio_final
FROM paquete p
LEFT JOIN hotel h ON p.hotel_id = h.id
LEFT JOIN vuelo v ON p.vuelo_id = v.id
LEFT JOIN aerolinea al ON v.aerolinea_id = al.id
LEFT JOIN aeropuerto a1 ON v.origen_id = a1.id
LEFT JOIN aeropuerto a2 ON v.destino_id = a2.id
LEFT JOIN promocion pr ON p.id = pr.paquete_id 
    AND pr.activa = TRUE 
    AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
WHERE p.activo = TRUE
AND v.fecha_salida > CURRENT_TIMESTAMP
AND v.asientos_disponibles > 0;

-- --------------------------------------------------
-- 7. PROCEDIMIENTOS ALMACENADOS PARA OPERACIONES COMUNES
-- --------------------------------------------------

-- 7.1 Procedimiento para buscar paquetes disponibles según criterios
DELIMITER //
CREATE PROCEDURE buscar_paquetes_disponibles(
    IN p_ciudad_destino VARCHAR(100),
    IN p_fecha_inicio DATE,
    IN p_duracion INT,
    IN p_presupuesto_max FLOAT
)
BEGIN
    SELECT 
        p.id,
        p.nombre,
        p.descripcion,
        p.duracion,
        h.nombre AS hotel,
        h.ciudad AS destino,
        h.estrellas,
        v.fecha_salida,
        v.fecha_llegada,
        CASE 
            WHEN pr.id IS NOT NULL AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
            THEN p.precio - (p.precio * pr.porcentaje_descuento / 100)
            ELSE p.precio
        END AS precio_final,
        COALESCE(pr.porcentaje_descuento, 0) AS descuento
    FROM paquete p
    JOIN hotel h ON p.hotel_id = h.id
    JOIN vuelo v ON p.vuelo_id = v.id
    LEFT JOIN promocion pr ON p.id = pr.paquete_id 
        AND pr.activa = TRUE 
        AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
    WHERE h.ciudad = p_ciudad_destino
    AND DATE(v.fecha_salida) >= p_fecha_inicio
    AND (p_duracion IS NULL OR p.duracion = p_duracion)
    AND (
        p_presupuesto_max IS NULL OR 
        CASE 
            WHEN pr.id IS NOT NULL AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
            THEN p.precio - (p.precio * pr.porcentaje_descuento / 100)
            ELSE p.precio
        END <= p_presupuesto_max
    )
    AND p.activo = TRUE
    AND v.asientos_disponibles > 0
    ORDER BY precio_final ASC;
END //
DELIMITER ;

-- 7.2 Procedimiento para crear una nueva reserva
DELIMITER //
CREATE PROCEDURE crear_reserva(
    IN p_cliente_id INT,
    IN p_paquete_id INT,
    IN p_agente_id INT,
    IN p_fecha_inicio DATETIME,
    IN p_fecha_fin DATETIME,
    OUT p_reserva_id INT,
    OUT p_codigo_reserva VARCHAR(20)
)
BEGIN
    DECLARE v_precio_paquete FLOAT;
    DECLARE v_descuento FLOAT DEFAULT 0;
    DECLARE v_precio_final FLOAT;
    DECLARE v_codigo VARCHAR(20);
    
    -- Obtener precio del paquete y posible descuento
    SELECT 
        p.precio, 
        COALESCE(pr.porcentaje_descuento, 0)
    INTO v_precio_paquete, v_descuento
    FROM paquete p
    LEFT JOIN promocion pr ON p.id = pr.paquete_id 
        AND pr.activa = TRUE 
        AND CURRENT_TIMESTAMP BETWEEN pr.fecha_inicio AND pr.fecha_fin
    WHERE p.id = p_paquete_id;
    
    -- Calcular precio final
    SET v_precio_final = v_precio_paquete - (v_precio_paquete * v_descuento / 100);
    
    -- Generar código de reserva
    SET v_codigo = CONCAT('R', LPAD(FLOOR(RAND() * 1000000), 6, '0'));
    
    -- Insertar la reserva
    INSERT INTO reserva (
        cliente_id, paquete_id, agente_id, 
        fecha_inicio, fecha_fin, 
        precio_total, estado, codigo_reserva
    ) VALUES (
        p_cliente_id, p_paquete_id, p_agente_id,
        p_fecha_inicio, p_fecha_fin,
        v_precio_final, 'confirmada', v_codigo
    );
    
    -- Obtener el ID de la reserva insertada
    SET p_reserva_id = LAST_INSERT_ID();
    SET p_codigo_reserva = v_codigo;
    
    -- Actualizar disponibilidad de asientos en vuelo
    UPDATE vuelo v
    JOIN paquete p ON v.id = p.vuelo_id
    SET v.asientos_disponibles = v.asientos_disponibles - 1
    WHERE p.id = p_paquete_id;
END //
DELIMITER ;

-- 7.3 Procedimiento para generar reporte de ventas por período
DELIMITER //
CREATE PROCEDURE generar_reporte_ventas(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    SELECT 
        DATE_FORMAT(r.fecha_reserva, '%Y-%m-%d') AS fecha,
        COUNT(r.id) AS total_reservas,
        SUM(r.precio_total) AS ingresos_totales,
        ROUND(AVG(r.precio_total), 2) AS ticket_promedio,
        COUNT(DISTINCT r.cliente_id) AS clientes_unicos,
        COUNT(DISTINCT r.paquete_id) AS paquetes_vendidos,
        GROUP_CONCAT(DISTINCT h.ciudad ORDER BY COUNT(r.id) DESC SEPARATOR ', ') AS destinos_populares
    FROM reserva r
    JOIN paquete p ON r.paquete_id = p.id
    LEFT JOIN hotel h ON p.hotel_id = h.id
    WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
    GROUP BY DATE_FORMAT(r.fecha_reserva, '%Y-%m-%d')
    ORDER BY fecha ASC;
END //
DELIMITER ;

-- 7.4 Función para calcular disponibilidad de un hotel en fechas específicas
DELIMITER //
CREATE FUNCTION calcular_disponibilidad_hotel(
    p_hotel_id INT,
    p_fecha_inicio DATE,
    p_fecha_fin DATE
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_habitaciones_disponibles INT;
    
    SELECT COUNT(hab.id) INTO v_habitaciones_disponibles
    FROM habitacion hab
    WHERE hab.hotel_id = p_hotel_id
    AND hab.disponible = TRUE
    AND hab.id NOT IN (
        SELECT rh.habitacion_id
        FROM reserva_habitacion rh
        WHERE (
            (p_fecha_inicio BETWEEN DATE(rh.fecha_inicio) AND DATE(rh.fecha_fin))
            OR (p_fecha_fin BETWEEN DATE(rh.fecha_inicio) AND DATE(rh.fecha_fin))
            OR (DATE(rh.fecha_inicio) BETWEEN p_fecha_inicio AND p_fecha_fin)
        )
    );
    
    RETURN v_habitaciones_disponibles;
END //
DELIMITER ;