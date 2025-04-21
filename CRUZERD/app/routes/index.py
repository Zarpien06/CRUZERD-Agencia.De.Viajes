from flask import Blueprint, render_template
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify

index = Blueprint('index', __name__)

@index.route('/')
def home():
    if current_user.is_authenticated:
        # Redirigir según el rol
        if current_user.rol == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        elif current_user.rol == 'agente':
            return redirect(url_for('agente.dashboard'))
        elif current_user.rol == 'proveedor':
            return redirect(url_for('proveedor.dashboard'))
    return render_template('index.html')  # Vista donde están los modales
