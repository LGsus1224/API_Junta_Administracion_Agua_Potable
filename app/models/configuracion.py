from app.libs import db


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consumo_base = db.Column(db.Float, nullable=False)
    exedente = db.Column(db.Float, nullable=False)
    valor_consumo_base = db.Column(db.Float, nullable=False)
    valor_exedente = db.Column(db.Float, nullable=False)
    reconexion = db.Column(db.Float, nullable=False)

    def __init__(self):
        super().__init__()
