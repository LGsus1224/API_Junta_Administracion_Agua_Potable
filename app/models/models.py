from app.libs import db,login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime


class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)

    def __init__(self):
        super().__init__()

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password,password)

    @classmethod
    def hash_password(self, password):
        return generate_password_hash(password)

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(user_id)


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consumo_base = db.Column(db.Float, nullable=False)
    exedente = db.Column(db.Float, nullable=False)
    valor_consumo_base = db.Column(db.Float, nullable=False)
    valor_exedente = db.Column(db.Float, nullable=False)

    def __init__(self):
        super().__init__()


class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cedula = db.Column(db.String(10), nullable=False, unique=True)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(10), nullable=True)
    servicios = db.relationship('Servicios', backref='cliente', cascade='all, delete-orphan', lazy=True)

    def __init__(self):
        super().__init__()


class Servicios(db.Model):
    _tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    n_conexion = db.Column(db.Integer, nullable=False, unique=True)
    n_medidor = db.Column(db.Integer, nullable=False, unique=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    direccion = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Boolean, nullable=False, default=1)
    lectura_anterior = db.Column(db.Integer, nullable=False)
    mis_planillas = db.relationship('Planillas', backref='servicio', cascade='all, delete-orphan', lazy=True)

    def __init__(self):
        super().__init__()


class Planillas(db.Model):
    __tablename__ = 'planillas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicios.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.now())
    consumo_base = db.Column(db.Float, nullable=False)
    exedente = db.Column(db.Float, nullable=False)
    valor_consumo_base = db.Column(db.Float, nullable=False) # Dinero
    valor_exedente = db.Column(db.Float, nullable=False) # Dinero
    lectura_anterior = db.Column(db.Integer, nullable=False)
    lectura_actual = db.Column(db.Integer, nullable=False)
    consumo_total = db.Column(db.Integer, nullable=False)
    valor_consumo_total = db.Column(db.Float, nullable=False) # Dinero
    pagado = db.Column(db.Boolean, nullable=False, default=0)

    def __init__(self):
        super().__init__()
