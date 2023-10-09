from app.libs import db,login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash


class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)
    logs = db.relationship('Logs', backref='usuario', cascade='all, delete-orphan', lazy=True)

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

