from app.libs import db
from app.common.enums import logsCategories
from datetime import datetime


class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    categoria = db.Column(db.Enum(logsCategories), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id', onupdate='cascade', ondelete='cascade'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now())
    detalle = db.Column(db.String(500), nullable=True)

