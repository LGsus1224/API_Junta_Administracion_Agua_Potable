from flask import Flask,redirect,url_for
from flask_restx import abort
from app.libs import *
# DB MODELS
from app.models import *
# API BP
from .apis import api_bp


def create_app(settings_module):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(settings_module)

    # Libraries initialization
    db.init_app(app)
    login_manager.init_app(app)

    # API initialize
    app.register_blueprint(api_bp)

    # MAIN ROUTE REDIRECTION
    @app.route('/')
    def main_redirect():
        return redirect(url_for('api_bp.doc'))

    # Error handlers
    @login_manager.unauthorized_handler
    def unauthorized():
        abort(401, error='No has iniciado sesión')
    return app
