from app.libs import db


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
