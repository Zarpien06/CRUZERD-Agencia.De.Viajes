# 🌐 Sistema de Agencia de Viajes

Bienvenido al **Sistema de Agencia de Viajes**, una plataforma web para gestionar **reservas de paquetes turísticos, vuelos y hoteles**, con autenticación por roles y actualización de disponibilidad por parte de proveedores externos.

---

## 🚀 Características Principales

- 🔍 Búsqueda con filtros personalizados (destino, precio, fecha).
- 🛫 Reservas en 3 pasos con cálculo automático y pago integrado.
- 💰 Gestión de promociones por temporada o paquete.
- 📊 Dashboard para métricas de ventas, ocupación y disponibilidad.
- 👥 Control de acceso por roles (Cliente, Agente, Proveedor).
- 🔄 API para que proveedores actualicen la disponibilidad de vuelos y hoteles.

---

## 👨‍💻 Roles del Sistema

- **🧳 Cliente**: Busca, cotiza y reserva paquetes turísticos.
- **📞 Agente**: Asiste a clientes, gestiona reservas y revisa estadísticas.
- **🏨 Proveedor**: Administra disponibilidad de hoteles o vuelos mediante la API.

---

## ✅ Requerimientos Funcionales

| ID   | Requerimiento                          | Criterios de Validación                                   |
|------|----------------------------------------|-----------------------------------------------------------|
| RF1  | Búsqueda                               | Filtros combinados por destino, fecha y precio.           |
| RF2  | Reservas                               | Flujo guiado en 3 pasos con resumen y pago.               |
| RF3  | Promociones                            | Descuentos automáticos según condiciones.                 |
| RF4  | Dashboard                              | Gráficos de ocupación y reportes de ventas.               |
| RF5  | Autenticación                          | Inicio de sesión con roles diferenciados.                 |

---

## 📚 Casos de Uso Destacados

### 📦 CU1: Reservar Paquete Turístico

1. El **Cliente** selecciona destino y fechas.
2. El **Sistema** muestra opciones de hotel y vuelo.
3. El **Cliente** elige y revisa el precio total con impuestos.
4. Llena el formulario y realiza el **pago**.
5. El sistema genera y envía el **voucher electrónico**.

🔁 *Flujo alternativo*: Si el pago es rechazado, la reserva se libera automáticamente y se notifica al usuario.

---

### 🔄 CU2: Actualizar Disponibilidad (Proveedor vía API)

1. El **Proveedor** se autentica correctamente en la API.
2. Envía un archivo JSON con la nueva disponibilidad.
3. El **Sistema** procesa y valida los datos.
4. Se retorna un mensaje de éxito o errores encontrados.

---

## 🧪 Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript
- **ORM**: SQLAlchemy
- **Autenticación**: Flask-Login + JWT
- **Formularios**: Flask-WTF + WTForms
- **Base de Datos**: MySQL (Workbench)
- **Hash de contraseñas**: Flask-Bcrypt

---

## ⚙️ Instalación del Proyecto

### 📦 Clona el repositorio

```bash
git clone https://github.com/tuusuario/sistema-agencia-viajes.git
cd sistema-agencia-viajes
```

### 🧰 Crea y activa el entorno virtual

```bash
# En Windows
python -m venv venv
py -m venv venv
source venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 📥 Instala las dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecutar el Proyecto

Una vez configurado el entorno, puedes iniciar el sistema con:

```bash
python run.py
```

ó

```bash
py run.py
```

---

## 📄 Archivo `requirements.txt`

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.2
Flask-WTF==1.2.1
WTForms==3.0.1
Werkzeug==2.3.7
SQLAlchemy==2.0.20
python-dotenv==1.0.0
email-validator==2.0.0
Flask-Bcrypt==1.0.1
pymysql==1.1.1
```

---

## 👤 Autor

Este proyecto fue desarrollado por:

> **Oscar Mauricio Cruz Figueroa**  
> Proyecto académico con entorno `venv`, editor **Visual Studio Code** y base de datos en **MySQL Workbench**.
> Contacto: [oscarcruzsena2006@gmail.com]     
