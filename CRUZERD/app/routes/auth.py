from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, Cliente, Agente, Proveedor
from app import db, bcrypt
from werkzeug.urls import url_parse

auth = Blueprint('auth', __name__)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Para solicitudes GET
    if request.method == 'GET':
        return redirect(url_for('index.home'))
        
    # Para solicitudes POST
    if request.method == 'POST':
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Obtener datos del formulario directamente
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validar campos obligatorios
            if not email or not password:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Email y contraseña son requeridos'}), 400
                else:
                    flash('Email y contraseña son requeridos', 'danger')
                    return redirect(url_for('index.home'))
            
            # Buscar al usuario en la base de datos
            user = Usuario.query.filter_by(email=email).first()
            
            # Verificar credenciales
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                
                if not next_page or url_parse(next_page).netloc != '':
                    # Redirigir dependiendo del rol del usuario
                    if user.rol == 'cliente':
                        next_page = url_for('cliente.dashboard')
                    elif user.rol == 'agente':
                        next_page = url_for('agente.dashboard') 
                    elif user.rol == 'proveedor':
                        next_page = url_for('proveedor.dashboard')
                    else:
                        next_page = url_for('index.home')
                
                # Responder según el tipo de solicitud
                if is_ajax:
                    return jsonify({
                        'success': True,
                        'redirect': next_page,
                        'message': '¡Inicio de sesión exitoso!'
                    })
                else:
                    flash('¡Inicio de sesión exitoso!', 'success')
                    return redirect(next_page)
            else:
                # Credenciales inválidas
                if is_ajax:
                    return jsonify({
                        'success': False,
                        'message': 'Credenciales inválidas. Por favor, revise su email y contraseña.'
                    }), 401
                else:
                    flash('Credenciales inválidas. Por favor, revise su email y contraseña.', 'danger')
                    return redirect(url_for('index.home'))
        
        except Exception as e:
            # Capturar cualquier error y devolver una respuesta JSON para AJAX
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500
            else:
                flash(f'Error en el servidor: {str(e)}', 'danger')
                return redirect(url_for('index.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Verificar si estamos en una solicitud AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if current_user.is_authenticated:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Ya ha iniciado sesión', 'redirect': url_for('cliente.dashboard')}), 400
        else:
            return redirect(url_for('cliente.dashboard'))
    
    # Para solicitudes GET
    if request.method == 'GET':
        return render_template('index.html')
    
    # Para solicitudes POST
    if request.method == 'POST':
        try:
            # Obtener datos del formulario directamente
            email = request.form.get('email')
            nombre = request.form.get('nombre')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            rol = request.form.get('rol')
            
            # Validar campos obligatorios
            if not email or not nombre or not password or not confirm_password or not rol:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400
                else:
                    flash('Todos los campos son obligatorios', 'danger')
                    return render_template('index.html')
            
            # Validar contraseñas
            if password != confirm_password:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400
                else:
                    flash('Las contraseñas no coinciden', 'danger')
                    return render_template('index.html')
            
            # Validar email único
            if Usuario.query.filter_by(email=email).first():
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Email ya registrado'}), 400
                else:
                    flash('Email ya registrado', 'danger')
                    return render_template('index.html')
            
            # Validar campos adicionales para proveedores
            if rol == 'proveedor':
                tipo = request.form.get('tipo_proveedor')
                nombre_empresa = request.form.get('nombre_empresa')
                
                if not tipo or not nombre_empresa:
                    if is_ajax:
                        return jsonify({'success': False, 'message': 'Complete los campos de proveedor'}), 400
                    else:
                        flash('Complete los campos de proveedor', 'danger')
                        return render_template('index.html')
            
            # Crear usuario
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = Usuario(email=email, nombre=nombre, password=hashed_password, rol=rol)
            
            db.session.add(user)
            db.session.flush()  # Para obtener el ID generado sin hacer commit
            
            # Crear perfil adicional según el rol
            if rol == 'cliente':
                cliente = Cliente(usuario_id=user.id)
                db.session.add(cliente)
            elif rol == 'agente':
                codigo = f"AG{user.id:04d}"
                agente = Agente(usuario_id=user.id, codigo_empleado=codigo)
                db.session.add(agente)
            elif rol == 'proveedor':
                tipo = request.form.get('tipo_proveedor')
                nombre_empresa = request.form.get('nombre_empresa')
                proveedor = Proveedor(usuario_id=user.id, tipo=tipo, nombre_empresa=nombre_empresa)
                db.session.add(proveedor)
            
            db.session.commit()
            
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': '¡Registro exitoso! Ya puede iniciar sesión.',
                    'redirect': url_for('index.home')
                })
            else:
                flash('¡Registro exitoso! Ya puede iniciar sesión.', 'success')
                return redirect(url_for('index.home'))
        
        except Exception as e:
            db.session.rollback()
            
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error al registrar: {str(e)}'}), 500
            else:
                flash(f'Error al registrar: {str(e)}', 'danger')
                return render_template('index.html') 
            
@auth.route('/logout')
def logout():
    # Aquí deberías hacer logout real si usaras flask_login
    # logout_user()
    return redirect(url_for('index.home'))  # O donde quieras redirigir al salir



'''
 from flask import Blueprint, render_template, session, redirect, url_for, abort
 from flask_login import login_required, current_user
from app.models import Reserva, Cliente  # Ajusta las importaciones según tus modelos

# Definición del blueprint con prefijo /auth

@auth.route('/demo/<role>')
def demo_role(role):
    """
    Guarda en sesión el rol 'cliente', 'agente' o 'proveedor'
    y redirige a /auth/dashboard
    """
    if role not in ('cliente', 'agente', 'proveedor'):
        abort(404)
    session['demo_role'] = role
    return redirect(url_for('auth.dashboard'))

@auth.route('/dashboard')
def dashboard():
    """
    /auth/dashboard:
      - Si hay demo_role en sesión, crea un DummyUser
      - Si no, usa current_user
    Luego renderiza según user.tipo, pasando stats.
    """
    # 1) Selección de usuario: demo o real
    demo = session.pop('demo_role', None)
    if demo:
        tipo = 'hotel' if demo == 'proveedor' else demo
        class DummyUser:
            def __init__(self, nombre, tipo):
                self.nombre = nombre
                self.tipo = tipo
                self.id = None
        user = DummyUser(f"Demo {tipo.capitalize()}", tipo)
    else:
        user = current_user
     
    # 2) Renderizado según tipo y cálculo de stats
    if user.tipo == 'cliente':
        stats = {
            'total_reservas': Reserva.query.filter_by(cliente_id=user.id).count()
        }
        return render_template('cliente/dashboard.html', cliente=user, stats=stats)

    elif user.tipo == 'agente':
        reservas_activas = Reserva.query.filter_by(agente_id=user.id, estado='activa').count()
        total_clientes = Cliente.query.filter_by(agente_id=user.id).count()
        ventas_mes = 0  # Aquí deberías calcular las ventas del mes (ajusta según tu lógica)
        
        # Asegúrate de que ventas_mes tenga un valor adecuado
        if ventas_mes is None:
            ventas_mes = 0
        
        stats = {
            'reservas_activas': reservas_activas,
            'total_clientes': total_clientes,
            'ventas_mes': ventas_mes  # Asegúrate de pasar ventas_mes aquí
        }
        return render_template('agente/dashboard.html', agente_actual=user, stats=stats)

    elif user.tipo in ('hotel', 'ambos'):
        stats = {
            'total_habitaciones': 0  # Ajusta según tu modelo de habitaciones
        }
        return render_template('proveedor/dashboard.html', proveedor=user, stats=stats)

    else:
        abort(403)
'''