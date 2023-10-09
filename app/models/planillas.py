from app.libs import db
from datetime import datetime


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