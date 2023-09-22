from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


api = Api(
    doc='/docs/',
    validate=True
)
db = SQLAlchemy()
login_manager = LoginManager()
