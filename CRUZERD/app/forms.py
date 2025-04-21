# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, DateField, TextAreaField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    telefono = StringField('Teléfono')
    direccion = TextAreaField('Dirección')
    submit = SubmitField('Guardar Cliente')

class ReservaForm(FlaskForm):
    cliente_id = SelectField('Cliente', validators=[DataRequired()], coerce=int)
    paquete_id = SelectField('Paquete', validators=[DataRequired()], coerce=int)
    fecha_inicio = DateField('Fecha de Inicio', validators=[DataRequired()], format='%Y-%m-%d')
    fecha_fin = DateField('Fecha de Fin', validators=[DataRequired()], format='%Y-%m-%d')
