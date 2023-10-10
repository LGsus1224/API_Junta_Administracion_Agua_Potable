from flask import Blueprint
from app.libs import api
# Api Namespaces
from .auth import api as api_auth_ns
from .administradores import api as api_admins_ns
from .logs import api as api_logs_ns
from .general import api as api_general_ns
from .clientes import api as api_clientes_ns
from .servicios import api as api_servicios_ns
from .planillas import api as api_planillas_ns
from .configuracion import api as api_config_ns
from .pagos_conexion import api as api_pagos_conexion_ns


api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

api.version = '1.0'
api.title = 'API DOCS'
api.description = """
Documentación sobre los endpoints y funciones que ofrece el API desarrollado para el
sistema de la Junta de Administración de Agua Potable.
"""

api.init_app(api_bp)

api.add_namespace(api_auth_ns, path='/auth')
api.add_namespace(api_admins_ns, path='/admin')
api.add_namespace(api_logs_ns, path='/logs')
api.add_namespace(api_general_ns, path='/general')
api.add_namespace(api_clientes_ns, path='/clientes')
api.add_namespace(api_servicios_ns, path='/servicios')
api.add_namespace(api_planillas_ns, path='/planillas')
api.add_namespace(api_config_ns, path='/configuracion')
api.add_namespace(api_pagos_conexion_ns, path='/pagos')
