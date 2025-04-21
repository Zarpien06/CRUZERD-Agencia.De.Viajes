-- Crear la base de datos CRUZERD
CREATE DATABASE IF NOT EXISTS CRUZERD;

-- Seleccionar la base de datos para trabajar con ella
USE CRUZERD;

-- Tabla Usuario
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(60) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Cliente
CREATE TABLE IF NOT EXISTS cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Tabla Agente
CREATE TABLE IF NOT EXISTS agente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    codigo_empleado VARCHAR(20) UNIQUE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Tabla Proveedor
CREATE TABLE IF NOT EXISTS proveedor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo VARCHAR(20),
    nombre_empresa VARCHAR(100),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Tabla Hotel
CREATE TABLE IF NOT EXISTS hotel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    estrellas INT,
    proveedor_id INT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedor(id)
);

-- Tabla Habitacion
CREATE TABLE IF NOT EXISTS habitacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    tipo VARCHAR(50),
    capacidad INT,
    precio FLOAT,
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (hotel_id) REFERENCES hotel(id)
);

-- Tabla Aeropuerto
CREATE TABLE IF NOT EXISTS aeropuerto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) UNIQUE,
    ciudad VARCHAR(100),
    pais VARCHAR(100)
);

-- Tabla Aerolinea
CREATE TABLE IF NOT EXISTS aerolinea (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) UNIQUE,
    proveedor_id INT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedor(id)
);

-- Tabla Vuelo
CREATE TABLE IF NOT EXISTS vuelo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aerolinea_id INT NOT NULL,
    origen_id INT NOT NULL,
    destino_id INT NOT NULL,
    fecha_salida DATETIME NOT NULL,
    fecha_llegada DATETIME NOT NULL,
    capacidad INT,
    asientos_disponibles INT,
    precio FLOAT,
    FOREIGN KEY (aerolinea_id) REFERENCES aerolinea(id),
    FOREIGN KEY (origen_id) REFERENCES aeropuerto(id),
    FOREIGN KEY (destino_id) REFERENCES aeropuerto(id)
);

-- Tabla Paquete
CREATE TABLE IF NOT EXISTS paquete (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    duracion INT,
    hotel_id INT,
    vuelo_id INT,
    FOREIGN KEY (hotel_id) REFERENCES hotel(id),
    FOREIGN KEY (vuelo_id) REFERENCES vuelo(id)
);

-- Tabla Promocion
CREATE TABLE IF NOT EXISTS promocion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paquete_id INT NOT NULL,
    nombre VARCHAR(100),
    descripcion TEXT,
    porcentaje_descuento FLOAT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (paquete_id) REFERENCES paquete(id)
);

-- Tabla Reserva
CREATE TABLE IF NOT EXISTS reserva (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    paquete_id INT NOT NULL,
    agente_id INT,
    fecha_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    precio_total FLOAT,
    estado VARCHAR(20),
    codigo_reserva VARCHAR(20) UNIQUE,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (paquete_id) REFERENCES paquete(id),
    FOREIGN KEY (agente_id) REFERENCES agente(id)
);

-- Tabla ReservaHabitacion
CREATE TABLE IF NOT EXISTS reserva_habitacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    habitacion_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    precio FLOAT,
    FOREIGN KEY (reserva_id) REFERENCES reserva(id),
    FOREIGN KEY (habitacion_id) REFERENCES habitacion(id)
);

-- Tabla ReservaVuelo
CREATE TABLE IF NOT EXISTS reserva_vuelo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    vuelo_id INT NOT NULL,
    asientos INT,
    precio FLOAT,
    FOREIGN KEY (reserva_id) REFERENCES reserva(id),
    FOREIGN KEY (vuelo_id) REFERENCES vuelo(id)
);

-- Tabla Pago
CREATE TABLE IF NOT EXISTS pago (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    monto FLOAT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo VARCHAR(50),
    estado VARCHAR(20),
    referencia VARCHAR(50),
    FOREIGN KEY (reserva_id) REFERENCES reserva(id)
);

select * from cliente;
select * from usuario;