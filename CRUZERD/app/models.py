from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'cliente', 'agente', 'proveedor'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('Cliente', backref='usuario', uselist=False)
    agente = db.relationship('Agente', backref='usuario', uselist=False)
    proveedor = db.relationship('Proveedor', backref='usuario', uselist=False)
    ventas = db.relationship('Venta', backref='cliente_usuario', foreign_keys='Venta.cliente_id')

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
   
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'), nullable=True)  # Agregado el campo agente_id
    agente = db.relationship('Agente', backref='clientes', lazy=True)  # Relación con Agente

    reservas = db.relationship('Reserva', backref='cliente', lazy=True)

class Agente(db.Model):
    __tablename__ = 'agentes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    codigo_empleado = db.Column(db.String(20), unique=True)

    reservas_gestionadas = db.relationship('Reserva', backref='agente', lazy=True)
    ventas = db.relationship('Venta', backref='agente', foreign_keys='Venta.agente_id')

class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(20))  # 'hotel', 'aerolinea'
    nombre_empresa = db.Column(db.String(100))

    hoteles = db.relationship('Hotel', backref='proveedor', lazy=True)
    aerolineas = db.relationship('Aerolinea', backref='proveedor', lazy=True)

class Hotel(db.Model):
    __tablename__ = 'hoteles'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    estrellas = db.Column(db.Integer)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))

    habitaciones = db.relationship('Habitacion', backref='hotel', lazy=True)
    paquetes = db.relationship('Paquete', backref='hotel', lazy=True)

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hoteles.id'), nullable=False)
    tipo = db.Column(db.String(50))
    capacidad = db.Column(db.Integer)
    precio = db.Column(db.Float)
    disponible = db.Column(db.Boolean, default=True)

    reservas = db.relationship('ReservaHabitacion', backref='habitacion', lazy=True)

class Aerolinea(db.Model):
    __tablename__ = 'aerolineas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(10), unique=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))

    vuelos = db.relationship('Vuelo', backref='aerolinea', lazy=True)

class Aeropuerto(db.Model):
    __tablename__ = 'aeropuertos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(10), unique=True)
    ciudad = db.Column(db.String(100))
    pais = db.Column(db.String(100))

    vuelos_salida = db.relationship('Vuelo', foreign_keys='Vuelo.origen_id', backref='origen', lazy=True)
    vuelos_llegada = db.relationship('Vuelo', foreign_keys='Vuelo.destino_id', backref='destino', lazy=True)

class Vuelo(db.Model):
    __tablename__ = 'vuelos'

    id = db.Column(db.Integer, primary_key=True)
    aerolinea_id = db.Column(db.Integer, db.ForeignKey('aerolineas.id'), nullable=False)
    origen_id = db.Column(db.Integer, db.ForeignKey('aeropuertos.id'), nullable=False)
    destino_id = db.Column(db.Integer, db.ForeignKey('aeropuertos.id'), nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=False)
    fecha_llegada = db.Column(db.DateTime, nullable=False)
    capacidad = db.Column(db.Integer)
    asientos_disponibles = db.Column(db.Integer)
    precio = db.Column(db.Float)

    paquetes = db.relationship('Paquete', backref='vuelo', lazy=True)
    reservas = db.relationship('ReservaVuelo', backref='vuelo', lazy=True)

class Paquete(db.Model):
    __tablename__ = 'paquetes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    duracion = db.Column(db.Integer)
    activo = db.Column(db.Boolean, default=True) 
    hotel_id = db.Column(db.Integer, db.ForeignKey('hoteles.id'))
    vuelo_id = db.Column(db.Integer, db.ForeignKey('vuelos.id'))

    promociones = db.relationship('Promocion', backref='paquete', lazy=True)
    reservas = db.relationship('Reserva', backref='paquete', lazy=True)

class Promocion(db.Model):
    __tablename__ = 'promociones'

    id = db.Column(db.Integer, primary_key=True)
    paquete_id = db.Column(db.Integer, db.ForeignKey('paquetes.id'), nullable=False)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    porcentaje_descuento = db.Column(db.Float)
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    activa = db.Column(db.Boolean, default=True)

class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    paquete_id = db.Column(db.Integer, db.ForeignKey('paquetes.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'))
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    precio_total = db.Column(db.Float)
    estado = db.Column(db.String(20))  # 'pendiente', 'confirmada', 'cancelada'
    codigo_reserva = db.Column(db.String(20), unique=True)

    habitaciones = db.relationship('ReservaHabitacion', backref='reserva', lazy=True)
    vuelos = db.relationship('ReservaVuelo', backref='reserva', lazy=True)
    pagos = db.relationship('Pago', backref='reserva', lazy=True)
    venta = db.relationship('Venta', backref='reserva', uselist=False)

class ReservaHabitacion(db.Model):
    __tablename__ = 'reservas_habitaciones'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    precio = db.Column(db.Float)

class ReservaVuelo(db.Model):
    __tablename__ = 'reservas_vuelos'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    vuelo_id = db.Column(db.Integer, db.ForeignKey('vuelos.id'), nullable=False)
    asientos = db.Column(db.Integer)
    precio = db.Column(db.Float)

class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50))
    estado = db.Column(db.String(20))  # 'procesado', 'rechazado', 'pendiente'
    referencia = db.Column(db.String(50))

class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'), nullable=True)

    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    estado_pago = db.Column(db.String(20), nullable=False, default='pendiente')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Venta {self.id} - Cliente {self.cliente_id} - Monto ${self.monto}>'
