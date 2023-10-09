from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required,current_user
from app.libs import db
from app.common.api_utils import (
    success_message,
    error_message,
    item_cliente,
    nullable,
    is_not_null_empty
)
from app.common.logs import LogsServices
from app.common.enums import logsCategories
from app.models import Clientes


api = Namespace('Clientes', description='Endpoints para la gestion de clientes')


# -------------------------------------- GET --------------------------------------
@api.route('/get/all')
class GetClientes(Resource):
    lista_clientes = api.model('Lista clientes', {
        'success':fields.List(fields.Nested(item_cliente))
    })

    @api.response(200, 'OK', lista_clientes)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener lista de todos los clientes

        Obtiene la lista de todos los clientes registrados.
        """
        try:
            clientes = Clientes.query.all()
            results = []
            for item in clientes:
                results.append({
                    'id':item.id,
                    'cedula':item.cedula,
                    'nombres':item.nombres,
                    'apellidos':item.apellidos,
                    'telefono':item.telefono
                })
            return {
                'success':results
            },200
        except Exception:
            abort(400, eror='No se pudo obtener los registros')


@api.route('/get/<int:id_cliente>')
class GetCliente(Resource):
    info_cliente = api.model('Información cliente', {
        'success':fields.Nested(item_cliente)
    })

    @api.response(200, 'OK', info_cliente)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self, id_cliente):
        """
        Informacion del cliente

        Obtener los datos e información acerca del cliente
        """
        try:
            cliente = Clientes.query.get(id_cliente)
            if cliente is None: raise Exception('No se encontro al cliente')
            return {
                'success':{
                    'id':cliente.id,
                    'cedula':cliente.cedula,
                    'nombres':cliente.nombres,
                    'apellidos':cliente.apellidos,
                    'telefono':cliente.telefono
                }
            }
        except Exception as e:
            abort(400, error='No fue posible obtener la información del cliente: ' + str(e))


# ----------------------------------------- POST -----------------------------------
@api.route('/new')
class NewCliente(Resource):
    new_cliente = api.model('Nuevo cliente',{
        'cedula':fields.String(
            required = True,
            title = 'Número de cedula',
            description = 'Número de cédula del usuario',
            pattern = '^\d{10}$',
            example='0000000000'
        ),
        'nombres':fields.String(
            required = True,
            title = 'Nombres',
            description = 'Nombres del usuario'
        ),
        'apellidos':fields.String(
            required = True,
            title = 'Apellidos',
            description = 'Apellidos del usuario'
        ),
        'telefono':fields.String(
            required = True,
            title = 'Numero de telefono',
            description = 'Número de telefono del cliente',
            pattern = '^\d{8,10}$',
            example = '0900000000'
        )
    })

    @api.expect(new_cliente)
    @api.response(201, 'Created', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self):
        """
        Registrar nuevo cliente

        Registra un nuevo cliente en la DB
        """
        try:
            data = api.payload
            cedula = data['cedula']
            nombres = data['nombres']
            apellidos = data['apellidos']
            telefono = data['telefono']
            # Crear nuevo cliente
            new_cliente = Clientes()
            new_cliente.cedula = cedula
            new_cliente.nombres = ' '.join(str(nombres).strip().title().split())
            new_cliente.apellidos = ' '.join(str(apellidos).strip().title().split())
            new_cliente.telefono = telefono
            db.session.add(new_cliente)
            LogsServices(db.session).new_log(logsCategories.cliente_created, current_user.id)
            db.session.commit()
            return {
                'success':'Cliente registrado'
            },201
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible registrar el cliente' + str(e))


# ------------------------------------- UPDATE ------------------------------------
@api.route('/update/<int:id_cliente>')
class UpdateCliente(Resource):
    update_cliente = api.model('Editar cliente', {
        'cedula':nullable(
            fields.String,
            required=False,
            title = 'Numero de cédula (Opcional)',
            description='Número de cédula del cliente',
            help = 'error cedula',
            example = '0200000000',
            pattern = '^\d{10}$'
        ),
        'nombres':nullable(
            fields.String,
            required=False,
            title = 'Nombres del cliente (Opcional)',
            description='Nombres del cliente'
        ),
        'apellidos':nullable(
            fields.String,
            required=False,
            title = 'Apellidos del cliente (Opcional)',
            description='Apellidos del cliente'
        ),
        'telefono':nullable(
            fields.String,
            required=False,
            title = 'Número de teléfono (Opcional)',
            description='Número de teléfono del cliente',
            example='0900000000',
            pattern = '^\d{7,10}$'
        )
    })

    @api.expect(update_cliente)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_cliente):
        """
        Actualizar información del cliente

        Actualiza la información personal del cliente cuando sea necesario

        Los campos que puede actualizar con opcionales, si quiere que se mantenga igual enviar null
        """
        try:
            data = api.payload
            cedula = data['cedula']
            nombres = data['nombres']
            apellidos = data['apellidos']
            telefono = data['telefono']
            # Obtener el cliente
            cliente = Clientes.query.get(id_cliente)
            if cliente is None: raise Exception('No existe el cliente buscado')
            if is_not_null_empty(cedula):
                cliente.cedula = cedula
            if is_not_null_empty(nombres):
                cliente.nombres = ' '.join(str(nombres).strip().title().split())
            if is_not_null_empty(apellidos):
                cliente.apellidos = ' '.join(str(apellidos).strip().title().split())
            if is_not_null_empty(telefono):
                cliente.telefono = telefono
            db.session.commit()
            return {
                'success':'Información de cliente actualizada'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible actualizar la información del usuario: ' + str(e))


# ------------------------------------- DELETE -------------------------------------
@api.route('/delete/<int:id_cliente>')
class DeleteCliente(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_cliente):
        """
        Eliminar cliente

        Eliminar un cliente de la base de datos.
        Se eliminaran sus servicios y sus planillas de pago
        """
        try:
            cliente = Clientes.query.get(id_cliente)
            if cliente is None: raise Exception('No se encontro al cliente')
            db.session.delete(cliente)
            db.session.commit()
            LogsServices(db.session).new_log(logsCategories.cliente_deleted, current_user.id)
            return {
                'success':'Cliente eliminado'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible eliminar el cliente: ' + str(e))
