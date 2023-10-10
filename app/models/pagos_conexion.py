from app.libs import db
from sqlalchemy import ForeignKey
from app.common.enums import conexionEnums


class PagosConexion(db.Model):
    __tablename__ = 'pagos_conexion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    tipo = db.Column(db.Enum(conexionEnums), nullable=False)
    id_servicio = db.Column(db.Integer, ForeignKey('servicios.id', ondelete='cascade', onupdate='cascade'), nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    entrada = db.Column(db.Float, nullable=False)
    cuota1 = db.Column(db.Float, nullable=False, default=0)
    cuota2 = db.Column(db.Float, nullable=False, default=0)
    cuota3 = db.Column(db.Float, nullable=False, default=0)
    cuota4 = db.Column(db.Float, nullable=False, default=0)
    cuota5 = db.Column(db.Float, nullable=False, default=0)
    cuota6 = db.Column(db.Float, nullable=False, default=0)

    def __init__(self):
        super().__init__()
