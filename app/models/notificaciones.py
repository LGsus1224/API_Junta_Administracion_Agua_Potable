from app.libs import db

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total = db.Column(db.Float, nullable=False, default=3)
    fecha_emision = db.Column(db.DateTime, nullable=False)
    pagado = db.Column(db.Boolean, nullable=False, default=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicios.id', ondelete='cascade', onupdate='cascade'), nullable=False)

    def __init__(self):
        super().__init__()