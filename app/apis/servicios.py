from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from sqlalchemy import extract
from app.libs import db
from app.common.api_utils import (
    success_message,
    error_message,
    item_servicio,
    item_cliente,
    nullable,
    is_not_null_empty
)
from app.models import Clientes,Servicios,Planillas
from datetime import datetime


api = Namespace('Servicios', description='Endpoints para la gestión de servicios')


# ----------------------------------- GET -----------------------------------------
@api.route('/get/all')
class GetAllServicios(Resource):
    item_estado_servicio = api.model('Estado de pago servicio', {
        'id':fields.Integer(
            readonly=True,
            title = 'ID',
            description='Id del servicio'
        ),
        'cliente':fields.Nested(item_cliente),
        'n_conexion':fields.Integer(
            readonly=True,
            title = 'Numero de conexion',
            description='Número de conexión de servicio'
        ),
        'n_medidor':fields.Integer(
            readonly=True,
            title = 'Numero de medidor',
            description='Número del medidor del servicio'
        ),
        'direccion':fields.String(
            readonly=True,
            title = 'Direccion del servicio',
            description='Dirección de instalación del servicio'
        ),
        'estado':fields.Boolean(
            readonly=True,
            title = 'Estado de servicio',
            description='Estado del servicio (Activo/Suspendido)'
        ),
        'lectura_anterior':fields.Integer(
            readonly=True,
            title = 'Lectura anterior medidor',
            description='Lectura anterior del medidor de servicio'
        ),
        'planilla_actual_emitida':fields.Boolean(
            readonly = True,
            title = 'Estado de verificación de pago',
            description = 'Estado de verificación de pago de planilla del servicio en el mes actual'
        )
    })

    estado_servicios = api.model('Todos los servicios', {
        'success':fields.List(fields.Nested(item_estado_servicio))
    })

    @api.response(200, 'OK', estado_servicios)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        try:
            servicios = Servicios.query.all()
            results = []
            current_date = datetime.now()
            for servicio in servicios:
                planillas = Planillas.query.filter(
                    Planillas.id_servicio == servicio.id,
                    extract('month',Planillas.fecha_emision) == current_date.month,
                    extract('year', Planillas.fecha_emision) == current_date.year
                ).count()
                emitido = True if planillas > 0 else False
                results.append({
                    'id':servicio.id,
                    'cliente':{
                        'id':servicio.cliente.id,
                        'cedula':servicio.cliente.cedula,
                        'nombres':servicio.cliente.nombres,
                        'apellidos':servicio.cliente.apellidos,
                        'telefono':servicio.cliente.telefono
                    },
                    'n_conexion':servicio.n_conexion,
                    'n_medidor':servicio.n_medidor,
                    'direccion':servicio.direccion,
                    'estado':servicio.estado,
                    'lectura_anterior':servicio.lectura_anterior,
                    'planilla_actual_emitida':emitido
                })
            return {'success':results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')


@api.route('/get/all/<int:id_cliente>')
class GetServiciosCliente(Resource):
    lista_servicios = api.model('Lista de servicios', {
        'success':fields.List(fields.Nested(item_servicio))
    })

    @api.response(200, 'OK', lista_servicios)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self,id_cliente):
        """
        Obtener lista de servicios por cliente

        Obtener la lista de servicios que tiene un cliente
        """
        try:
            cliente = Clientes.query.get(id_cliente)
            if cliente == None:
                raise Exception('No existe el cliente')
            servicios = Servicios.query.filter_by(id_cliente=id_cliente).all()
            results = []
            for item in servicios:
                results.append({
                    'id':item.id,
                    'n_conexion':item.n_conexion,
                    'n_medidor':item.n_medidor,
                    'id_cliente':item.id_cliente,
                    'direccion':item.direccion,
                    'estado':item.estado,
                    'lectura_anterior':item.lectura_anterior
                })
            return {
                'success':results
            },200
        except Exception as e:
            abort(400, error='No se pudo obtener los registros: ' + str(e))


@api.route('/get/<int:id_servicio>')
class GetServicio(Resource):
    info_servicio = api.model('Información de servicio', {
        'success':fields.Nested(item_servicio)
    })

    @api.response(200, 'OK', info_servicio)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self, id_servicio):
        """
        Buscar un servicio

        Buscar el servicio por su id
        """
        try:
            servicio = Servicios.query.get(id_servicio)
            if servicio is None:
                raise Exception('No existe el servicio buscado')
            results = {
                'id':servicio.id,
                'n_conexion':servicio.n_conexion,
                'n_medidor':servicio.n_medidor,
                'id_cliente':servicio.id_cliente,
                'direccion':servicio.direccion,
                'estado':servicio.estado,
                'lectura_anterior':servicio.lectura_anterior
            }
            return {
                'success':results
            },200
        except Exception as e:
            abort(400, error='No fue posible obtener la información: ' + str(e))


# -------------------------------------- NEW --------------------------------------
@api.route('/new')
class NewServicio(Resource):
    new_servicio = api.model('Nuevo servicio', {
        'id_cliente':fields.Integer(
            required=True,
            title = 'Id de cliente',
            description = 'Id del cliente del servicio',
            min=1
        ),
        'n_conexion':fields.Integer(
            required=True,
            title = 'N° de conexión',
            description='Número de conexión del servicio instalado',
            min = 1
        ),
        'n_medidor':fields.Integer(
            required = True,
            title = 'N° de del medidor',
            description = 'Número de medidor del servicio instalado',
            min=1
        ),
        'direccion':fields.String(
            required = True,
            title = 'Direccion de servicio',
            description = 'Dirección de instalación de servicio'
        ),
        'estado':fields.Boolean(
            required = True,
            title = 'Estado de servicio',
            description = 'Estado del servicio (Activo/Suspendido)'
        ),
        'lectura_anterior':fields.Integer(
            required = True,
            title = 'Lectura anterior',
            description = 'Lectura anterior que indica el medidor',
            min=0
        )
    })

    @api.expect(new_servicio)
    @api.response(201, 'Created', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self):
        """
        Registrar un nuevo servicio

        Registra un nuevo servicio para un cliente
        """
        try:
            data = api.payload
            id_cliente = data['id_cliente']
            n_conexion = data['n_conexion']
            n_medidor = data['n_medidor']
            direccion = data['direccion']
            estado = data['estado']
            lectura_anterior = data['lectura_anterior']
            # Buscar id_cliente
            cliente = Clientes.query.get(id_cliente)
            if cliente is None: raise Exception()
            # Crear nuevo servicio
            new_servicio = Servicios()
            new_servicio.id_cliente = id_cliente
            new_servicio.n_conexion= n_conexion
            new_servicio.n_medidor = n_medidor
            new_servicio.direccion = ' '.join(str(direccion).strip().title().split())
            new_servicio.estado = estado
            new_servicio.lectura_anterior = lectura_anterior
            db.session.add(new_servicio)
            db.session.commit()
            return {
                'success':'Servicio creado'
            },201
        except Exception:
            db.session.rollback()
            abort(400, error='No fue posible registrar el servicio')


# ------------------------------------ UPDATE -------------------------------------
@api.route('/update/<int:id_servicio>')
class UpdateServicio(Resource):
    update_servicio = api.model('Editar información de servicio', {
        'n_conexion':nullable(
            fields.Integer,
            required=False,
            title = 'Número de conexión (Opcional)',
            description = 'Referente al número de conexión del servicio instalado',
            min=1
        ),
        'n_medidor':nullable(
            fields.Integer,
            required = False,
            title = 'Número de medidor (Opcional)',
            description = 'Referente al número de medidor del servicio instalado',
            min=1
        ),
        'direccion':nullable(
            fields.String,
            required = False,
            title = 'Dirección de servicio (Opcional)',
            description = 'Dirección de instalación del servicio'
        )
    })

    @api.expect(update_servicio)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_servicio):
        """
        Editar servicio

        Editar la información del servicio

        Los campos que pueden enviarse con opcionales. Si quiere mantener un valor como se encuentra enviar null
        """
        try:
            data = api.payload
            n_conexion = data['n_conexion']
            n_medidor = data['n_medidor']
            direccion = data['direccion']
            # Obtener servicio
            servicio = Servicios.query.get(id_servicio)
            if servicio is None: raise Exception('No se encontro el servicio')
            # Validar datos y actualizar data
            if is_not_null_empty(n_conexion):
                servicio.n_conexion = n_conexion
            if is_not_null_empty(n_medidor):
                servicio.n_medidor = n_medidor
            if is_not_null_empty(direccion):
                servicio.direccion = ' '.join(str(direccion).strip().title().split())
            db.session.commit()
            return {
                'success':'Información de servicio actualizada'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible editar el servicio: ' + str(e))


@api.route('/update/cliente/<int:id_servicio>')
class UpdateServicioCliente(Resource):
    change_usuario = api.model('Reasignar usuario de servicio', {
        'id_cliente':fields.Integer(
            required = True,
            title = 'ID cliente',
            description = 'ID del cliente que se asignará al servicio',
            min=1
        )
    })

    @login_required
    @api.expect(change_usuario)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    def put(self, id_servicio):
        """
        Cambiar cliente asignado a un servicio

        Cambiar a que cliente le pertenece el servicio
        """
        try:
            data = api.payload
            id_cliente = data['id_cliente']
            servicio = Servicios.query.get(id_servicio)
            if servicio is None:
                raise Exception('No existe el servicio buscado')
            cliente = Clientes.query.get(id_cliente)
            if cliente is None:
                raise Exception('No existe el cliente seleccionado')
            servicio.id_cliente = id_cliente
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible reasignar el servicio: ' + str(e))


@api.route('/update/estado/<int:id_servicio>')
class UpdateServicioEstado(Resource):
    estado = api.model('Estado de servicio', {
        'estado':fields.Boolean(
            required = True,
            title = 'Estado del servicio',
            description = 'Indica el estado para el servicio True -> Activo, False -> Inactivo'
        )
    })

    @api.expect(estado)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_servicio):
        """
        Cambiar estado del servicio

        Cambiar el estado del servicio por activo o inactivo
        """
        try:
            data = api.payload
            estado = data['estado']
            # Buscar servicio
            servicio = Servicios.query.get(id_servicio)
            if servicio is None:
                raise Exception('No existe el servicio buscado')
            servicio.estado = estado
            db.session.commit()
            return {
                'success':'Estado de servicio actualizado'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible actualizar el estado del servicio: ' + str(e))


# -------------------------------------- DELETE -----------------------------------
@api.route('/delete/<int:id_servicio>')
class DeleteServicio(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_servicio):
        """
        Eliminar servicio

        Elimina un servicio relacionado por su id y las planillas generadas por el mismo
        """
        try:
            servicio = Servicios.query.get(id_servicio)
            if servicio is None: raise Exception('No existe el servicio buscado')
            db.session.delete(servicio)
            db.session.commit()
            return {
                'success':'Servicio eliminado'
            },200
        except Exception as e:
            abort(400, error='No fue posible eliminar el servicio: ' + str(e))

