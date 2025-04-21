from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.models import Paquete, Hotel, Vuelo, Reserva, Promocion, Cliente, Pago
from app import db
import random
import string
from datetime import datetime

cliente = Blueprint('cliente', __name__)
@cliente.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.rol == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        elif current_user.rol == 'agente':
            return redirect(url_for('agente.dashboard'))
        elif current_user.rol == 'proveedor':
            return redirect(url_for('proveedor.dashboard'))

    return render_template('index.html')  # Solo si NO ha iniciado sesión

@cliente.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'cliente':
        if current_user.rol == 'agente':
            return redirect(url_for('agente.dashboard'))
        elif current_user.rol == 'proveedor':
            return redirect(url_for('proveedor.dashboard'))

    try:
        promociones = Promocion.query.filter_by(activa=True).order_by(Promocion.porcentaje_descuento.desc()).limit(4).all()
    except Exception as e:
        print(f"Error al obtener promociones: {e}")
        promociones = []

    return render_template('cliente/dashboard.html', promociones=promociones)

@cliente.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    if request.method == 'POST':
        destino = request.form.get('destino')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        precio_min = request.form.get('precio_min')
        precio_max = request.form.get('precio_max')
        
        query = Paquete.query
        
        # Aplicar filtros
        if destino:
            query = query.join(Vuelo).join(Vuelo.destino).filter(Vuelo.destino.has(ciudad=destino))
        
        if precio_min:
            query = query.filter(Paquete.precio >= float(precio_min))
        
        if precio_max:
            query = query.filter(Paquete.precio <= float(precio_max))
        
        # Obtener resultados
        paquetes = query.all()
        
        return render_template('cliente/paquetes.html', paquetes=paquetes, busqueda=True)
    
    return render_template('cliente/busqueda.html')

@cliente.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.home'))  # Redirige al index principal
