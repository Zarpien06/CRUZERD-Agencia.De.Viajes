from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Agente, Reserva, Venta, Cliente, Paquete, Habitacion, Vuelo, Promocion, Pago, Usuario
from app.forms import ClienteForm, ReservaForm  # Importa los formularios necesarios
from app import bcrypt
from app import db
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid


agente = Blueprint('agente', __name__)

# Decorador para verificar si el usuario es un agente
def agente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'agente':
            flash('Acceso no autorizado. Necesita ser un agente para ver esta página.', 'danger')
            return redirect(url_for('index'))  # Redirigiendo al index en lugar de auth.login
        return f(*args, **kwargs)
    return decorated_function

# Función para obtener el inicio y fin del mes actual
def obtener_inicio_fin_mes():
    hoy = datetime.today()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mes = hoy.replace(day=1, hour=23, minute=59, second=59, microsecond=999999)
    fin_mes = fin_mes.replace(day=28) + timedelta(days=4)  # Asegura que el día sea el último del mes
    fin_mes = fin_mes - timedelta(days=fin_mes.day)  # Corrige para que sea el último día del mes
    return inicio_mes, fin_mes

# Dashboard del agente
@agente.route('/dashboard')
@login_required
@agente_required
def dashboard():
    form = ClienteForm() 
    reserva_form = ReservaForm()

    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    
    if not agente_actual:
        flash('No se encontró información del agente.', 'warning')
        return redirect(url_for('index'))

    total_reservas = Reserva.query.filter_by(agente_id=agente_actual.id).count()
    reservas_pendientes = Reserva.query.filter_by(agente_id=agente_actual.id, estado='pendiente').count()
    reservas_confirmadas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='confirmada').count()
    
    ultimas_reservas = Reserva.query.filter_by(agente_id=agente_actual.id).order_by(Reserva.fecha_reserva.desc()).limit(5).all()

    # Obtener el inicio y fin del mes actual
    inicio_mes, fin_mes = obtener_inicio_fin_mes()

    # Realiza la consulta para contar las reservas activas
    reservas_activas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='confirmada').count()
    
    # Consulta para obtener ventas del mes
    ventas_mes = db.session.query(func.sum(Venta.monto)).filter(
        Venta.agente_id == agente_actual.id,
        Venta.fecha >= inicio_mes, 
        Venta.fecha <= fin_mes
    ).scalar()

    # Obtener todos los clientes y paquetes para el modal de nueva reserva
    clientes = Cliente.query.all()
    paquetes = Paquete.query.filter_by(activo=True).all()

    stats = {
        'reservas_activas': reservas_activas or 0,
        'ventas_mes': ventas_mes or 0
    }
    
    return render_template('agente/dashboard.html', 
                          total_reservas=total_reservas,
                          reservas_pendientes=reservas_pendientes,
                          reservas_confirmadas=reservas_confirmadas,
                          ultimas_reservas=ultimas_reservas,
                          agente_actual=agente_actual,
                          stats=stats,
                          form=form,
                          reserva_form=reserva_form,
                          clientes=clientes,
                          paquetes=paquetes)

# Gestión de reservas por estado
@agente.route('/reservas')
@login_required
@agente_required
def reservas():
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if not agente_actual:
        flash('No se encontró información del agente.', 'warning')
        return redirect(url_for('index'))

    estado = request.args.get('estado', 'todas')
    
    if estado == 'pendiente':
        reservas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='pendiente').order_by(Reserva.fecha_reserva.desc()).all()
    elif estado == 'confirmada':
        reservas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='confirmada').order_by(Reserva.fecha_reserva.desc()).all()
    elif estado == 'cancelada':
        reservas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='cancelada').order_by(Reserva.fecha_reserva.desc()).all()
    elif estado == 'pagada':
        reservas = Reserva.query.filter_by(agente_id=agente_actual.id, estado='pagada').order_by(Reserva.fecha_reserva.desc()).all()
    else:
        reservas = Reserva.query.filter_by(agente_id=agente_actual.id).order_by(Reserva.fecha_reserva.desc()).all()
    
    # Obtener todos los clientes y paquetes para el modal de nueva reserva
    clientes = Cliente.query.all()
    paquetes = Paquete.query.filter_by(activo=True).all()
    
    return render_template('agente/gestionar_reservas.html', 
                           reservas=reservas, 
                           estado_actual=estado,
                           clientes=clientes,
                           paquetes=paquetes)

# Detalle de una reserva
@agente.route('/reserva/<int:reserva_id>')
@login_required
@agente_required
def detalle_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        flash("No tienes permiso para ver esta reserva.", "danger")
        return redirect(url_for('agente.reservas'))

    return render_template('agente/detalle_reserva.html', reserva=reserva)

# Obtener detalles de reserva para el modal
@agente.route('/get_reserva_details/<int:reserva_id>')
@login_required
@agente_required
def get_reserva_details(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403

    # Obtener información de pagos asociados
    pagos = Pago.query.filter_by(reserva_id=reserva.id).all()
    pagos_data = []
    for pago in pagos:
        pagos_data.append({
            'id': pago.id,
            'monto': str(pago.monto),
            'fecha': pago.fecha.strftime('%Y-%m-%d %H:%M'),
            'metodo': pago.metodo,
            'referencia': pago.referencia
        })

    # Formatear fechas para JSON
    fecha_reserva = reserva.fecha_reserva.strftime('%Y-%m-%d %H:%M')
    fecha_inicio = reserva.fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin = reserva.fecha_fin.strftime('%Y-%m-%d')

    # Crear respuesta JSON con los detalles de la reserva
    response = {
        'id': reserva.id,
        'codigo': reserva.codigo,
        'cliente': {
            'id': reserva.cliente.id,
            'nombre': reserva.cliente.nombre,
            'email': reserva.cliente.email,
            'telefono': reserva.cliente.telefono
        },
        'paquete': {
            'id': reserva.paquete.id,
            'nombre': reserva.paquete.nombre,
            'descripcion': reserva.paquete.descripcion,
            'precio': str(reserva.paquete.precio)
        },
        'fecha_reserva': fecha_reserva,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': reserva.estado,
        'total': str(reserva.total),
        'pagos': pagos_data
    }

    # Añadir detalles de habitación si existe
    if hasattr(reserva, 'habitacion') and reserva.habitacion:
        response['habitacion'] = {
            'id': reserva.habitacion.id,
            'nombre': reserva.habitacion.nombre,
            'tipo': reserva.habitacion.tipo,
            'precio': str(reserva.habitacion.precio)
        }

    # Añadir detalles de vuelo si existe
    if hasattr(reserva, 'vuelo') and reserva.vuelo:
        response['vuelo'] = {
            'id': reserva.vuelo.id,
            'numero': reserva.vuelo.numero,
            'origen': reserva.vuelo.origen,
            'destino': reserva.vuelo.destino,
            'fecha_salida': reserva.vuelo.fecha_salida.strftime('%Y-%m-%d %H:%M'),
            'fecha_llegada': reserva.vuelo.fecha_llegada.strftime('%Y-%m-%d %H:%M'),
            'precio': str(reserva.vuelo.precio)
        }

    return jsonify(response)

# Actualizar el estado de la reserva
@agente.route('/actualizar-reserva/<int:reserva_id>', methods=['POST'])
@login_required
@agente_required
def actualizar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        flash("No tienes permiso para modificar esta reserva.", "danger")
        return redirect(url_for('agente.reservas'))

    nuevo_estado = request.form.get('estado')
    if nuevo_estado in ['pendiente', 'confirmada', 'cancelada', 'pagada']:
        reserva.estado = nuevo_estado
        db.session.commit()
        flash(f'Reserva actualizada a estado: {nuevo_estado}', 'success')
    else:
        flash('Estado no válido.', 'warning')
    
    return redirect(url_for('agente.detalle_reserva', reserva_id=reserva.id))

# Editar reserva (para el modal)
@agente.route('/edit_reserva', methods=['POST'])
@login_required
@agente_required
def edit_reserva():
    reserva_id = request.form.get('reserva_id')
    estado = request.form.get('estado')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        flash("No tienes permiso para modificar esta reserva.", "danger")
        return redirect(url_for('agente.reservas'))

    # Actualizar los campos
    if estado in ['pendiente', 'confirmada', 'cancelada', 'pagada']:
        reserva.estado = estado
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        reserva.fecha_inicio = fecha_inicio_dt
        reserva.fecha_fin = fecha_fin_dt
    except ValueError:
        flash('Formato de fecha incorrecto.', 'danger')
        return redirect(url_for('agente.reservas'))
    
    try:
        db.session.commit()
        flash('Reserva actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la reserva: {str(e)}', 'danger')
    
    return redirect(url_for('agente.reservas'))

# Registrar pago para una reserva
@agente.route('/registrar_pago', methods=['POST'])
@login_required
@agente_required
def registrar_pago():
    reserva_id = request.form.get('reserva_id')
    monto = request.form.get('monto')
    metodo = request.form.get('metodo')
    referencia = request.form.get('referencia')

    # Validaciones básicas
    if not reserva_id or not monto or not metodo:
        flash('Todos los campos obligatorios deben estar completos.', 'warning')
        return redirect(url_for('agente.reservas'))

    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        flash("No tienes permiso para registrar pagos en esta reserva.", "danger")
        return redirect(url_for('agente.reservas'))

    # Crear el nuevo pago
    nuevo_pago = Pago(
        reserva_id=reserva_id,
        monto=float(monto),
        metodo=metodo,
        referencia=referencia,
        fecha=datetime.now()
    )

    try:
        db.session.add(nuevo_pago)
        
        # Actualizar estado de la reserva si el pago es completo
        pagos_totales = db.session.query(func.sum(Pago.monto)).filter(Pago.reserva_id == reserva_id).scalar() or 0
        pagos_totales += float(monto)
        
        if pagos_totales >= reserva.total:
            reserva.estado = 'pagada'
            
        db.session.commit()
        flash('Pago registrado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar el pago: {str(e)}', 'danger')

    return redirect(url_for('agente.detalle_reserva', reserva_id=reserva_id))

# Crear nueva reserva
@agente.route('/create_reserva', methods=['POST'])
@login_required
@agente_required
def create_reserva():
    # Obtener datos del formulario
    cliente_id = request.form.get('cliente_id')
    paquete_id = request.form.get('paquete_id')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    habitacion_id = request.form.get('habitacion_id')
    vuelo_id = request.form.get('vuelo_id')
    promocion_id = request.form.get('promocion_id')
    precio_total = request.form.get('precio_total')
    metodo_pago = request.form.get('metodo_pago')
    
    # Validar datos obligatorios
    if not cliente_id or not paquete_id or not fecha_inicio or not fecha_fin or not precio_total:
        flash('Todos los campos obligatorios deben estar completos.', 'warning')
        return redirect(url_for('agente.dashboard'))
    
    try:
        # Convertir fechas
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Obtener el agente actual
        agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
        
        # Generar código único para la reserva
        codigo_reserva = f"RES-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear nueva reserva
        nueva_reserva = Reserva(
            codigo=codigo_reserva,
            cliente_id=cliente_id,
            paquete_id=paquete_id,
            agente_id=agente_actual.id,
            fecha_reserva=datetime.now(),
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            total=float(precio_total),
            estado='pendiente'
        )
        
        # Añadir habitación si se seleccionó
        if habitacion_id:
            nueva_reserva.habitacion_id = habitacion_id
            
        # Añadir vuelo si se seleccionó
        if vuelo_id:
            nueva_reserva.vuelo_id = vuelo_id
            
        # Añadir promoción si se seleccionó
        if promocion_id:
            nueva_reserva.promocion_id = promocion_id
        
        db.session.add(nueva_reserva)
        db.session.commit()
        
        # Si se realizó pago inicial, registrarlo
        if metodo_pago != '':
            # Obtener datos de pago adicionales
            num_tarjeta = request.form.get('num_tarjeta')
            referencia = num_tarjeta[-4:] if num_tarjeta else "Pago inicial"
            
            nuevo_pago = Pago(
                reserva_id=nueva_reserva.id,
                monto=float(precio_total),  # Se podría ajustar si es un pago parcial
                metodo=metodo_pago,
                referencia=referencia,
                fecha=datetime.now()
            )
            
            db.session.add(nuevo_pago)
            nueva_reserva.estado = 'pagada'
            db.session.commit()
        
        flash(f'Reserva creada exitosamente. Código: {codigo_reserva}', 'success')
        return redirect(url_for('agente.detalle_reserva', reserva_id=nueva_reserva.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la reserva: {str(e)}', 'danger')
        return redirect(url_for('agente.dashboard'))

# Buscar habitaciones disponibles
@agente.route('/buscar_habitaciones', methods=['GET'])
@login_required
@agente_required
def buscar_habitaciones():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Se requieren fechas de inicio y fin"}), 400
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Obtener habitaciones ocupadas en ese rango de fechas
        ocupadas = db.session.query(Reserva.habitacion_id).filter(
            Reserva.fecha_inicio <= fecha_fin_dt,
            Reserva.fecha_fin >= fecha_inicio_dt,
            Reserva.estado.in_(['pendiente', 'confirmada', 'pagada'])
        ).all()
        
        habitaciones_ocupadas = [item[0] for item in ocupadas if item[0] is not None]
        
        # Obtener habitaciones disponibles
        habitaciones = Habitacion.query.filter(
            Habitacion.id.notin_(habitaciones_ocupadas) if habitaciones_ocupadas else True,
            Habitacion.disponible == True
        ).all()
        
        # Formatear respuesta
        habitaciones_data = []
        for hab in habitaciones:
            habitaciones_data.append({
                'id': hab.id,
                'nombre': hab.nombre,
                'tipo': hab.tipo,
                'capacidad': hab.capacidad,
                'precio': str(hab.precio),
                'descripcion': hab.descripcion
            })
        
        return jsonify(habitaciones_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Buscar vuelos disponibles
@agente.route('/buscar_vuelos', methods=['GET'])
@login_required
@agente_required
def buscar_vuelos():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Se requieren fechas de inicio y fin"}), 400
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Obtener vuelos disponibles en esas fechas
        vuelos = Vuelo.query.filter(
            Vuelo.fecha_salida >= fecha_inicio_dt,
            Vuelo.fecha_llegada <= fecha_fin_dt.replace(hour=23, minute=59, second=59),
            Vuelo.disponible == True
        ).all()
        
        # Formatear respuesta
        vuelos_data = []
        for vuelo in vuelos:
            vuelos_data.append({
                'id': vuelo.id,
                'numero': vuelo.numero,
                'origen': vuelo.origen,
                'destino': vuelo.destino,
                'fecha_salida': vuelo.fecha_salida.strftime('%Y-%m-%d %H:%M'),
                'fecha_llegada': vuelo.fecha_llegada.strftime('%Y-%m-%d %H:%M'),
                'precio': str(vuelo.precio),
                'aerolinea': vuelo.aerolinea
            })
        
        return jsonify(vuelos_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener detalles de un paquete
@agente.route('/get_paquete_details/<int:paquete_id>')
@login_required
@agente_required
def get_paquete_details(paquete_id):
    paquete = Paquete.query.get_or_404(paquete_id)
    
    # Formatear respuesta
    response = {
        'id': paquete.id,
        'nombre': paquete.nombre,
        'descripcion': paquete.descripcion,
        'precio': str(paquete.precio),
        'duracion': paquete.duracion,
        'incluye': paquete.incluye.split('\n') if paquete.incluye else [],
        'no_incluye': paquete.no_incluye.split('\n') if paquete.no_incluye else []
    }
    
    return jsonify(response)

# Generar voucher para una reserva
@agente.route('/generar_voucher/<int:reserva_id>')
@login_required
@agente_required
def generar_voucher(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Verifica si la reserva pertenece al agente
    agente_actual = Agente.query.filter_by(usuario_id=current_user.id).first()
    if reserva.agente_id != agente_actual.id:
        flash("No tienes permiso para generar un voucher para esta reserva.", "danger")
        return redirect(url_for('agente.reservas'))
    
    return render_template('agente/voucher.html', reserva=reserva)

@agente.route('/agregar_cliente', methods=['POST'])
@login_required
def add_cliente_post():
    nombre = request.form.get('nombre')
    correo = request.form.get('email')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')

    # Validación de campos
    if not nombre or not correo:
        flash('Nombre y correo son obligatorios.', 'warning')
        return redirect(url_for('agente.dashboard'))

    # Verifica si ya existe el cliente
    existente = Cliente.query.filter_by(correo=correo).first()
    if existente:
        flash('Ya existe un cliente con ese correo.', 'danger')
        return redirect(url_for('agente.dashboard'))

    # Crea y guarda el nuevo cliente
    nuevo_cliente = Cliente(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        direccion=direccion
    )

    try:
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Cliente agregado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al guardar: ' + str(e), 'danger')

    return redirect(url_for('agente.dashboard'))

@agente.route('/editar_cliente', methods=['POST'])
@login_required
def edit_cliente():
    cliente_id = request.form.get('cliente_id')
    nombre = request.form.get('nombre')
    correo = request.form.get('email')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')

    if not cliente_id or not nombre or not correo:
        flash('Todos los campos obligatorios deben estar completos.', 'warning')
        return redirect(url_for('agente.dashboard'))

    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('agente.dashboard'))

    # Validar si se está intentando actualizar con un correo ya existente
    existente = Cliente.query.filter(Cliente.correo == correo, Cliente.id != cliente_id).first()
    if existente:
        flash('Ya existe otro cliente con ese correo.', 'danger')
        return redirect(url_for('agente.dashboard'))

    # Actualiza los campos
    cliente.nombre = nombre
    cliente.correo = correo
    cliente.telefono = telefono
    cliente.direccion = direccion

    try:
        db.session.commit()
        flash('Cliente actualizado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el cliente: ' + str(e), 'danger')

    return redirect(url_for('agente.dashboard'))

@agente.route('/cliente/detalles/<int:cliente_id>')
@login_required
@agente_required
def detalles_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    reservas = Reserva.query.filter_by(cliente_id=cliente.id).all()

    reservas_data = []
    for r in reservas:
        reservas_data.append({
            'codigo': r.codigo,
            'paquete': r.paquete.nombre,
            'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d'),
            'total': str(r.total),
            'estado': r.estado
        })

    return jsonify({
        'nombre': cliente.nombre,
        'email': cliente.correo,
        'telefono': cliente.telefono,
        'direccion': cliente.direccion,
        'reservas': reservas_data
    })

# Ruta para agregar un cliente
@agente.route('/add_cliente', methods=['GET', 'POST'])
@login_required
@agente_required
def add_cliente():
    form = ClienteForm()

    if form.validate_on_submit():   
    # Hasheamos la contraseña (puedes adaptarlo si ya la tienes lista)   
           hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    # 1. Crear el Usuario
    nuevo_usuario = Usuario(
        nombre=form.nombre.data,
        email=form.email.data,
        password=hashed_password,
        rol='cliente'
    )
    db.session.add(nuevo_usuario)
    db.session.commit()  # Necesario para que se genere el ID

    # 2. Crear el Cliente asociado
    nuevo_cliente = Cliente(
        usuario_id=nuevo_usuario.id,
        telefono=form.telefono.data,
        direccion=form.direccion.data
    )
    db.session.add(nuevo_cliente)
    db.session.commit()
        
    flash('Cliente creado correctamente', 'success')
    return redirect(url_for('agente.dashboard'))  # Redirige al dashboard

    return render_template('agente/dashboard.html', form=form)