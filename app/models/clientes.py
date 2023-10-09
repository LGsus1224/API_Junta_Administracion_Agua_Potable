from app.libs import db

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