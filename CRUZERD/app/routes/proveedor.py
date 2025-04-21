from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Proveedor, Hotel, Habitacion, Aerolinea, Vuelo, Paquete, Promocion
from datetime import datetime
import json

proveedor = Blueprint('proveedor', __name__)

# Middleware para verificar que sea un proveedor
@proveedor.before_request
def verificar_proveedor():
    if not current_user.is_authenticated or current_user.rol != 'proveedor':
        flash('Acceso denegado. Debe iniciar sesión como proveedor.', 'danger')
        return redirect(url_for('index'))

# Dashboard principal del proveedor
@proveedor.route('/dashboard')
@login_required
def dashboard():
    # Obtener información del proveedor
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Datos para métricas y gráficos
    metricas = {
        'total_reservas': 0,
        'ingresos_totales': 0,
        'ocupacion_promedio': 0,
        'reservas_recientes': []
    }
    
    hoteles = []
    aerolineas = []
    
    # Obtener hoteles del proveedor
    if proveedor.tipo == 'hotel' or proveedor.tipo == 'ambos':
        hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
        
        # Calcular métricas para hoteles
        for hotel in hoteles:
            # Calcular ocupación
            total_habitaciones = Habitacion.query.filter_by(hotel_id=hotel.id).count()
            habitaciones_ocupadas = Habitacion.query.filter_by(hotel_id=hotel.id, disponible=False).count()
            
            if total_habitaciones > 0:
                hotel.ocupacion = (habitaciones_ocupadas / total_habitaciones) * 100
            else:
                hotel.ocupacion = 0
                
            # Paquetes asociados al hotel
            paquetes = Paquete.query.filter_by(hotel_id=hotel.id).all()
            
            # Calcular ingresos y reservas para este hotel
            ingresos_hotel = 0
            reservas_hotel = 0
            
            for paquete in paquetes:
                for reserva in paquete.reservas:
                    if reserva.estado in ['confirmada', 'pendiente']:
                        ingresos_hotel += reserva.precio_total
                        reservas_hotel += 1
                        
                        # Añadir a reservas recientes (máximo 5)
                        if len(metricas['reservas_recientes']) < 5:
                            metricas['reservas_recientes'].append({
                                'id': reserva.id,
                                'codigo': reserva.codigo_reserva,
                                'fecha': reserva.fecha_reserva,
                                'paquete': paquete.nombre,
                                'monto': reserva.precio_total
                            })
            
            hotel.ingresos = ingresos_hotel
            hotel.total_reservas = reservas_hotel
            
            # Actualizar métricas globales
            metricas['total_reservas'] += reservas_hotel
            metricas['ingresos_totales'] += ingresos_hotel
    
    # Obtener aerolíneas del proveedor
    if proveedor.tipo == 'aerolinea' or proveedor.tipo == 'ambos':
        aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
        
        # Calcular métricas para aerolíneas
        for aerolinea in aerolineas:
            # Obtener todos los vuelos de la aerolínea
            vuelos = Vuelo.query.filter_by(aerolinea_id=aerolinea.id).all()
            
            # Calcular ocupación, ingresos y reservas para esta aerolínea
            ingresos_aerolinea = 0
            reservas_aerolinea = 0
            asientos_totales = 0
            asientos_ocupados = 0
            
            for vuelo in vuelos:
                asientos_totales += vuelo.capacidad
                asientos_ocupados += (vuelo.capacidad - vuelo.asientos_disponibles)
                
                # Paquetes asociados al vuelo
                paquetes = Paquete.query.filter_by(vuelo_id=vuelo.id).all()
                
                for paquete in paquetes:
                    for reserva in paquete.reservas:
                        if reserva.estado in ['confirmada', 'pendiente']:
                            ingresos_aerolinea += reserva.precio_total
                            reservas_aerolinea += 1
                            
                            # Añadir a reservas recientes (máximo 5)
                            if len(metricas['reservas_recientes']) < 5:
                                metricas['reservas_recientes'].append({
                                    'id': reserva.id,
                                    'codigo': reserva.codigo_reserva,
                                    'fecha': reserva.fecha_reserva,
                                    'paquete': paquete.nombre,
                                    'monto': reserva.precio_total
                                })
            
            if asientos_totales > 0:
                aerolinea.ocupacion = (asientos_ocupados / asientos_totales) * 100
            else:
                aerolinea.ocupacion = 0
                
            aerolinea.ingresos = ingresos_aerolinea
            aerolinea.total_reservas = reservas_aerolinea
            
            # Actualizar métricas globales
            metricas['total_reservas'] += reservas_aerolinea
            metricas['ingresos_totales'] += ingresos_aerolinea
    
    # Calcular ocupación promedio global
    total_ocupacion = 0
    total_servicios = len(hoteles) + len(aerolineas)
    
    for hotel in hoteles:
        total_ocupacion += hotel.ocupacion
        
    for aerolinea in aerolineas:
        total_ocupacion += aerolinea.ocupacion
        
    if total_servicios > 0:
        metricas['ocupacion_promedio'] = total_ocupacion / total_servicios
    
    # Ordenar reservas recientes por fecha (más reciente primero)
    metricas['reservas_recientes'] = sorted(
        metricas['reservas_recientes'], 
        key=lambda x: x['fecha'], 
        reverse=True
    )
    
    return render_template('proveedor/dashboard.html', 
                           proveedor=proveedor, 
                           hoteles=hoteles, 
                           aerolineas=aerolineas, 
                           metricas=metricas)
# GESTIÓN DE HOTELES
@proveedor.route('/hoteles')
@login_required
def hoteles():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
    return render_template('proveedor/hoteles.html', hoteles=hoteles)

@proveedor.route('/hotel/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_hotel():
    if request.method == 'POST':
        proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
        
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        ciudad = request.form.get('ciudad')
        pais = request.form.get('pais')
        estrellas = request.form.get('estrellas')
        
        nuevo_hotel = Hotel(
            nombre=nombre,
            direccion=direccion,
            ciudad=ciudad,
            pais=pais,
            estrellas=estrellas,
            proveedor_id=proveedor.id
        )
        
        db.session.add(nuevo_hotel)
        db.session.commit()
        
        flash('Hotel creado con éxito', 'success')
        return redirect(url_for('proveedor.hoteles'))
    
    return render_template('proveedor/hotel_form.html')

@proveedor.route('/hotel/<int:hotel_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar que el hotel pertenezca al proveedor
    if hotel.proveedor_id != proveedor.id:
        flash('No tiene permiso para editar este hotel', 'danger')
        return redirect(url_for('proveedor.hoteles'))
    
    if request.method == 'POST':
        hotel.nombre = request.form.get('nombre')
        hotel.direccion = request.form.get('direccion')
        hotel.ciudad = request.form.get('ciudad')
        hotel.pais = request.form.get('pais')
        hotel.estrellas = request.form.get('estrellas')
        
        db.session.commit()
        flash('Hotel actualizado con éxito', 'success')
        return redirect(url_for('proveedor.hoteles'))
    
    return render_template('proveedor/hotel_form.html', hotel=hotel)

# GESTIÓN DE HABITACIONES
@proveedor.route('/hotel/<int:hotel_id>/habitaciones')
@login_required
def habitaciones(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar que el hotel pertenezca al proveedor
    if hotel.proveedor_id != proveedor.id:
        flash('No tiene permiso para ver estas habitaciones', 'danger')
        return redirect(url_for('proveedor.hoteles'))
    
    habitaciones = Habitacion.query.filter_by(hotel_id=hotel_id).all()
    return render_template('proveedor/habitaciones.html', hotel=hotel, habitaciones=habitaciones)

@proveedor.route('/hotel/<int:hotel_id>/habitacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_habitacion(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar que el hotel pertenezca al proveedor
    if hotel.proveedor_id != proveedor.id:
        flash('No tiene permiso para añadir habitaciones a este hotel', 'danger')
        return redirect(url_for('proveedor.hoteles'))
    
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        capacidad = request.form.get('capacidad')
        precio = request.form.get('precio')
        disponible = True if request.form.get('disponible') == 'on' else False
        
        nueva_habitacion = Habitacion(
            hotel_id=hotel_id,
            tipo=tipo,
            capacidad=capacidad,
            precio=precio,
            disponible=disponible
        )
        
        db.session.add(nueva_habitacion)
        db.session.commit()
        
        flash('Habitación creada con éxito', 'success')
        return redirect(url_for('proveedor.habitaciones', hotel_id=hotel_id))
    
    return render_template('proveedor/habitacion_form.html', hotel=hotel)

@proveedor.route('/habitacion/<int:habitacion_id>/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar_habitacion(habitacion_id):
    habitacion = Habitacion.query.get_or_404(habitacion_id)
    hotel = Hotel.query.get(habitacion.hotel_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar permisos
    if hotel.proveedor_id != proveedor.id:
        flash('No tiene permiso para editar esta habitación', 'danger')
        return redirect(url_for('proveedor.hoteles'))
    
    if request.method == 'POST':
        habitacion.tipo = request.form.get('tipo')
        habitacion.capacidad = int(request.form.get('capacidad'))
        habitacion.precio = float(request.form.get('precio'))
        habitacion.disponible = True if request.form.get('disponible') == 'on' else False
        
        db.session.commit()
        flash('Habitación actualizada con éxito', 'success')
        return redirect(url_for('proveedor.habitaciones', hotel_id=hotel.id))
    
    return render_template('proveedor/habitacion_form.html', hotel=hotel, habitacion=habitacion)

# GESTIÓN DE AEROLÍNEAS
@proveedor.route('/aerolineas')
@login_required
def aerolineas():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
    return render_template('proveedor/aerolineas.html', aerolineas=aerolineas)

@proveedor.route('/aerolinea/nueva', methods=['GET', 'POST'])
@login_required
def nueva_aerolinea():
    if request.method == 'POST':
        proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
        
        nombre = request.form.get('nombre')
        codigo = request.form.get('codigo')
        
        nueva_aerolinea = Aerolinea(
            nombre=nombre,
            codigo=codigo,
            proveedor_id=proveedor.id
        )
        
        db.session.add(nueva_aerolinea)
        db.session.commit()
        
        flash('Aerolínea creada con éxito', 'success')
        return redirect(url_for('proveedor.aerolineas'))
    
    return render_template('proveedor/aerolinea_form.html')

# GESTIÓN DE VUELOS
@proveedor.route('/aerolinea/<int:aerolinea_id>/vuelos')
@login_required
def vuelos(aerolinea_id):
    aerolinea = Aerolinea.query.get_or_404(aerolinea_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar que la aerolínea pertenezca al proveedor
    if aerolinea.proveedor_id != proveedor.id:
        flash('No tiene permiso para ver estos vuelos', 'danger')
        return redirect(url_for('proveedor.aerolineas'))
    
    vuelos = Vuelo.query.filter_by(aerolinea_id=aerolinea_id).all()
    return render_template('proveedor/vuelos.html', aerolinea=aerolinea, vuelos=vuelos)

@proveedor.route('/aerolinea/<int:aerolinea_id>/vuelo/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_vuelo(aerolinea_id):
    from models import Aeropuerto
    
    aerolinea = Aerolinea.query.get_or_404(aerolinea_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar que la aerolínea pertenezca al proveedor
    if aerolinea.proveedor_id != proveedor.id:
        flash('No tiene permiso para añadir vuelos a esta aerolínea', 'danger')
        return redirect(url_for('proveedor.aerolineas'))
    
    # Obtener todos los aeropuertos para el formulario
    aeropuertos = Aeropuerto.query.all()
    
    if request.method == 'POST':
        origen_id = request.form.get('origen_id')
        destino_id = request.form.get('destino_id')
        fecha_salida = datetime.strptime(request.form.get('fecha_salida'), '%Y-%m-%dT%H:%M')
        fecha_llegada = datetime.strptime(request.form.get('fecha_llegada'), '%Y-%m-%dT%H:%M')
        capacidad = int(request.form.get('capacidad'))
        precio = float(request.form.get('precio'))
        
        # Validar que origen y destino sean diferentes
        if origen_id == destino_id:
            flash('El origen y destino no pueden ser el mismo aeropuerto', 'danger')
            return render_template('proveedor/vuelo_form.html', 
                                  aerolinea=aerolinea, 
                                  aeropuertos=aeropuertos)
        
        # Validar fechas
        if fecha_llegada <= fecha_salida:
            flash('La fecha de llegada debe ser posterior a la fecha de salida', 'danger')
            return render_template('proveedor/vuelo_form.html', 
                                  aerolinea=aerolinea, 
                                  aeropuertos=aeropuertos)
        
        nuevo_vuelo = Vuelo(
            aerolinea_id=aerolinea_id,
            origen_id=origen_id,
            destino_id=destino_id,
            fecha_salida=fecha_salida,
            fecha_llegada=fecha_llegada,
            capacidad=capacidad,
            asientos_disponibles=capacidad,  # Inicialmente, todos los asientos están disponibles
            precio=precio
        )
        
        db.session.add(nuevo_vuelo)
        db.session.commit()
        
        flash('Vuelo creado con éxito', 'success')
        return redirect(url_for('proveedor.vuelos', aerolinea_id=aerolinea_id))
    
    return render_template('proveedor/vuelo_form.html', 
                          aerolinea=aerolinea, 
                          aeropuertos=aeropuertos)

@proveedor.route('/vuelo/<int:vuelo_id>/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar_vuelo(vuelo_id):
    from models import Aeropuerto
    
    vuelo = Vuelo.query.get_or_404(vuelo_id)
    aerolinea = Aerolinea.query.get(vuelo.aerolinea_id)
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar permisos
    if aerolinea.proveedor_id != proveedor.id:
        flash('No tiene permiso para editar este vuelo', 'danger')
        return redirect(url_for('proveedor.aerolineas'))
    
    # Obtener todos los aeropuertos para el formulario
    aeropuertos = Aeropuerto.query.all()
    
    if request.method == 'POST':
        asientos_disponibles = int(request.form.get('asientos_disponibles'))
        
        # Validar que los asientos disponibles no sean más que la capacidad
        if asientos_disponibles > vuelo.capacidad:
            flash('Los asientos disponibles no pueden ser más que la capacidad total', 'danger')
            return render_template('proveedor/vuelo_update_form.html', 
                                  vuelo=vuelo, 
                                  aerolinea=aerolinea)
        
        vuelo.asientos_disponibles = asientos_disponibles
        vuelo.precio = float(request.form.get('precio'))
        
        db.session.commit()
        flash('Vuelo actualizado con éxito', 'success')
        return redirect(url_for('proveedor.vuelos', aerolinea_id=aerolinea.id))
    
    return render_template('proveedor/vuelo_update_form.html', 
                          vuelo=vuelo, 
                          aerolinea=aerolinea)

# GESTIÓN DE PAQUETES TURÍSTICOS
@proveedor.route('/paquetes')
@login_required
def paquetes():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
    aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
    
    hotel_ids = [hotel.id for hotel in hoteles]
    aerolinea_ids = [aerolinea.id for aerolinea in aerolineas]
    vuelo_ids = []
    
    for aerolinea_id in aerolinea_ids:
        vuelos = Vuelo.query.filter_by(aerolinea_id=aerolinea_id).all()
        vuelo_ids.extend([vuelo.id for vuelo in vuelos])
    
    # Obtener paquetes que contengan hoteles o vuelos del proveedor
    paquetes = Paquete.query.filter(
        (Paquete.hotel_id.in_(hotel_ids)) | 
        (Paquete.vuelo_id.in_(vuelo_ids))
    ).all()
    
    return render_template('proveedor/paquetes.html', paquetes=paquetes)

@proveedor.route('/paquete/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_paquete():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Obtener hoteles del proveedor
    hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
    
    # Obtener vuelos de las aerolíneas del proveedor
    aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
    vuelos = []
    
    for aerolinea in aerolineas:
        vuelos_aerolinea = Vuelo.query.filter_by(aerolinea_id=aerolinea.id).all()
        vuelos.extend(vuelos_aerolinea)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        duracion = int(request.form.get('duracion'))
        hotel_id = request.form.get('hotel_id')
        vuelo_id = request.form.get('vuelo_id')
        
        # Validar que al menos haya un hotel o un vuelo
        if not hotel_id and not vuelo_id:
            flash('Debe seleccionar al menos un hotel o un vuelo', 'danger')
            return render_template('proveedor/paquete_form.html', 
                                  hoteles=hoteles, 
                                  vuelos=vuelos)
        
        nuevo_paquete = Paquete(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            duracion=duracion,
            activo=True,
            hotel_id=hotel_id if hotel_id else None,
            vuelo_id=vuelo_id if vuelo_id else None
        )
        
        db.session.add(nuevo_paquete)
        db.session.commit()
        
        flash('Paquete turístico creado con éxito', 'success')
        return redirect(url_for('proveedor.paquetes'))
    
    return render_template('proveedor/paquete_form.html', 
                          hoteles=hoteles, 
                          vuelos=vuelos)

# GESTIÓN DE PROMOCIONES
@proveedor.route('/promociones')
@login_required
def promociones():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Obtener todos los paquetes asociados a los servicios del proveedor
    hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
    aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
    
    hotel_ids = [hotel.id for hotel in hoteles]
    aerolinea_ids = [aerolinea.id for aerolinea in aerolineas]
    vuelo_ids = []
    
    for aerolinea_id in aerolinea_ids:
        vuelos = Vuelo.query.filter_by(aerolinea_id=aerolinea_id).all()
        vuelo_ids.extend([vuelo.id for vuelo in vuelos])
    
    # Obtener paquetes que contengan hoteles o vuelos del proveedor
    paquetes = Paquete.query.filter(
        (Paquete.hotel_id.in_(hotel_ids)) | 
        (Paquete.vuelo_id.in_(vuelo_ids))
    ).all()
    
    paquete_ids = [paquete.id for paquete in paquetes]
    
    # Obtener las promociones asociadas a estos paquetes
    promociones = Promocion.query.filter(Promocion.paquete_id.in_(paquete_ids)).all()
    
    return render_template('proveedor/promociones.html', promociones=promociones, paquetes=paquetes)

@proveedor.route('/promocion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_promocion():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    # Obtener paquetes asociados al proveedor
    hoteles = Hotel.query.filter_by(proveedor_id=proveedor.id).all()
    aerolineas = Aerolinea.query.filter_by(proveedor_id=proveedor.id).all()
    
    hotel_ids = [hotel.id for hotel in hoteles]
    aerolinea_ids = [aerolinea.id for aerolinea in aerolineas]
    vuelo_ids = []
    
    for aerolinea_id in aerolinea_ids:
        vuelos = Vuelo.query.filter_by(aerolinea_id=aerolinea_id).all()
        vuelo_ids.extend([vuelo.id for vuelo in vuelos])
    
    # Obtener paquetes que contengan hoteles o vuelos del proveedor
    paquetes = Paquete.query.filter(
        (Paquete.hotel_id.in_(hotel_ids)) | 
        (Paquete.vuelo_id.in_(vuelo_ids))
    ).all()
    
    if request.method == 'POST':
        paquete_id = request.form.get('paquete_id')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        porcentaje_descuento = float(request.form.get('porcentaje_descuento'))
        fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d')
        fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d')
        
        # Validar fechas
        if fecha_fin <= fecha_inicio:
            flash('La fecha de fin debe ser posterior a la fecha de inicio', 'danger')
            return render_template('proveedor/promocion_form.html', paquetes=paquetes)
        
        # Validar porcentaje
        if porcentaje_descuento <= 0 or porcentaje_descuento >= 100:
            flash('El porcentaje de descuento debe estar entre 0 y 100', 'danger')
            return render_template('proveedor/promocion_form.html', paquetes=paquetes)
        
        nueva_promocion = Promocion(
            paquete_id=paquete_id,
            nombre=nombre,
            descripcion=descripcion,
            porcentaje_descuento=porcentaje_descuento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activa=True
        )
        
        db.session.add(nueva_promocion)
        db.session.commit()
        
        flash('Promoción creada con éxito', 'success')
        return redirect(url_for('proveedor.promociones'))
    
    return render_template('proveedor/promocion_form.html', paquetes=paquetes)

# API para actualizar disponibilidad (API JSON para el caso de uso CU2)
@proveedor.route('/api/actualizar-disponibilidad', methods=['POST'])
@login_required
def actualizar_disponibilidad_api():
    proveedor = Proveedor.query.filter_by(usuario_id=current_user.id).first()
    
    try:
        data = request.get_json()
        
        # Validar el formato de los datos
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'message': 'Formato de datos inválido'
            }), 400
        
        # Procesar actualización de disponibilidad de habitaciones
        if 'habitaciones' in data:
            for hab_data in data['habitaciones']:
                # Validar que la habitación pertenezca a un hotel del proveedor
                habitacion = Habitacion.query.get(hab_data.get('id'))
                if not habitacion:
                    continue
                
                hotel = Hotel.query.get(habitacion.hotel_id)
                if not hotel or hotel.proveedor_id != proveedor.id:
                    continue
                
                # Actualizar disponibilidad
                if 'disponible' in hab_data:
                    habitacion.disponible = hab_data['disponible']
                
                # Actualizar precio si está presente
                if 'precio' in hab_data:
                    habitacion.precio = hab_data['precio']
        
        # Procesar actualización de disponibilidad de vuelos
        if 'vuelos' in data:
            for vuelo_data in data['vuelos']:
                # Validar que el vuelo pertenezca a una aerolínea del proveedor
                vuelo = Vuelo.query.get(vuelo_data.get('id'))
                if not vuelo:
                    continue
                
                aerolinea = Aerolinea.query.get(vuelo.aerolinea_id)
                if not aerolinea or aerolinea.proveedor_id != proveedor.id:
                    continue
                
                # Actualizar asientos disponibles
                if 'asientos_disponibles' in vuelo_data:
                    asientos = vuelo_data['asientos_disponibles']
                    # Asegurarse de que no exceda la capacidad
                    if asientos <= vuelo.capacidad:
                        vuelo.asientos_disponibles = asientos
                
                # Actualizar precio si está presente
                if 'precio' in vuelo_data:
                    vuelo.precio = vuelo_data['precio']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Disponibilidad actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar disponibilidad: {str(e)}'
        }), 500