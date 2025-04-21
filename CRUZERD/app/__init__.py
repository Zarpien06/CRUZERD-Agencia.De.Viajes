from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask_wtf import CSRFProtect
import locale

# Inicialización de las extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Vista de login por defecto
bcrypt = Bcrypt()
csrf = CSRFProtect()


# Establecer la localización para que el formato de la moneda sea adecuado (dependiendo de tu país)
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajustar la localización a tu preferencia (por ejemplo, España)

# Definir el filtro personalizado
def format_currency(value):
    """ Formatear un valor como una moneda. """
    if value is None:
        return "$0.00"
    return locale.currency(value, grouping=True)

def create_app(config_class=Config):
    app = Flask(__name__)  # Crea la aplicación Flask
    app.config.from_object(config_class)  # Carga la configuración desde el archivo Config

    # Inicializa las extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    # Registra el filtro de moneda
    app.jinja_env.filters['format_currency'] = format_currency

    # Configuración adicional de respuestas JSON
    app.config['JSON_AS_ASCII'] = False  # Soporte para caracteres especiales (utf-8)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Respuestas JSON más legibles

    # Cargar el modelo Usuario para el LoginManager
    from app.models import Usuario  # Es necesario importar después de la inicialización de db

    @login_manager.user_loader
    def load_user(id):
        return Usuario.query.get(int(id))  # Devuelve el usuario desde la base de datos

    # Registrar los blueprints
    from app.routes.auth import auth as auth_bp
    from app.routes.cliente import cliente as cliente_bp
    from app.routes.agente import agente  # Se importa el blueprint de 'agente' directamente
    from app.routes.proveedor import proveedor as proveedor_bp
    from .routes.index import index  # Importa el blueprint de la página de inicio
    

    # Registrar los blueprints con sus URL prefix (si es necesario)
    app.register_blueprint(index)  # Página principal
    app.register_blueprint(auth_bp,  url_prefix='/auth')  # Autenticación (login, registro, etc.)
    app.register_blueprint(cliente_bp)  # Cliente
    app.register_blueprint(agente, url_prefix='/agente')  # Agente, con prefijo /agente
    app.register_blueprint(proveedor_bp)  # Proveedor

    # Crear las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    return app  # Devuelve la app configurada
