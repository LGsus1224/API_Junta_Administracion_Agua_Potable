from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required, current_user
from app.libs import db
from app.common.logs import LogsServices
from app.common.api_utils import (
    success_message,
    error_message,
    item_servicio,
    item_cliente
)
from app.models import Notificaciones
from app.common.enums import logsCategories
from datetime import datetime


api = Namespace('Notificaciones', description='Endpoints para la gestión de notificaciones')


notificacion_item = api.model('NotificacionItem', {
    'id':fields.Integer(
        readonly=True,
        title = 'ID',
        description='Id de notificacion'
    ),
    'servicio':fields.Nested(item_servicio),
    'cliente':fields.Nested(item_cliente),
    'fecha_emision':fields.Float(readonly=True, title='Fecha de Emision'),
    'total':fields.Float(readonly=True, title='Total en $'),
    'pagado':fields.Boolean(readonly=True, title='Estado de pago')
})

notificaciones_list = api.model('Notificaciones', {
    'success':fields.List(fields.Nested(notificacion_item))
})


# ----------------------------------- GET -----------------------------------------
@api.route('/get/all')
class GetAllNotificacions(Resource):
    @api.response(200, 'OK', notificaciones_list)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        try:
            notificaciones = db.session.query(Notificaciones).all()
            results = []
            # Crear array de resultados
            for item in notificaciones:
                results.append({
                    'id':item.id,
                    'fecha_emision':datetime.strftime(item.fecha_emision, '%d-%m-%Y %H:%M'),
                    'total':item.total,
                    'pagado':item.pagado,
                    'servicio':{
                        'id':item.id_servicio,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor
                    },
                    'cliente':{
                        'id':item.servicio.cliente.id,
                        'nombres':item.servicio.cliente.nombres,
                        'apellidos':item.servicio.cliente.apellidos,
                        'cedula':item.servicio.cliente.cedula,
                        'telefono':item.servicio.cliente.telefono
                    }
                })
            return {'success': results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')


@api.route('/get/<int:id_servicio>')
class GetServicioNotificaciones(Resource):
    @api.response(200, 'OK', notificaciones_list)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self, id_servicio):
        try:
            # Consultar la lista de notificaciones para el servicio
            notificaciones = db.session.query(Notificaciones).filter(
                Notificaciones.id_servicio == id_servicio
            ).all()
            results = []
            # Crear array de resultados
            for item in notificaciones:
                results.append({
                    'id':item.id,
                    'fecha_emision':datetime.strftime(item.fecha_emision, '%d-%m-%Y %H:%M'),
                    'total':item.total,
                    'pagado':item.pagado,
                    'servicio':{
                        'id':item.id_servicio,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor
                    },
                    'cliente':{
                        'id':item.servicio.cliente.id,
                        'nombres':item.servicio.cliente.nombres,
                        'apellidos':item.servicio.cliente.apellidos,
                        'cedula':item.servicio.cliente.cedula,
                        'telefono':item.servicio.cliente.telefono
                    }
                })
            return {'success':results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')


# --------------------------------- POST ----------------------------------------
@api.route('/new/<int:id_servicio>')
class NewNotification(Resource):
    @api.response(201, 'Created', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self, id_servicio):
        try:
            # fecha actual
            current_date = datetime.now()
            # Crear la notificacion
            new_notification = Notificaciones()
            new_notification.id_servicio = id_servicio
            new_notification.fecha_emision = current_date
            db.session.add(new_notification)
            db.session.commit()
            LogsServices(db.session).new_log(logsCategories.notificacion_created, current_user.id)
            return {'success':'Notificacion creada'}, 201
        except Exception:
            db.session.rollback()
            abort(400, error='No fue posible registrar la notificacion')


# ------------------------------------- PUT ------------------------------------
@api.route('/update/pago/<int:id_notificacion>')
class UpdatePagoNotificacion(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_notificacion):
        try:
            notificacion: Notificaciones = db.session.query(Notificaciones).get(id_notificacion)
            if notificacion is None: raise Exception('No existe la notificacion')
            msg = [False, '']
            if not notificacion.pagado:
                notificacion.pagado = True
                msg[0] = True
                msg[1] = 'pagada'
            else:
                notificacion.pagado = False
                msg[1] = 'en deuda'
            # Verificar si se realizo un pago para guardar log
            if msg[0]:
                LogsServices(db.session).new_log(logsCategories.notificacion_cobrada, current_user.id)
            db.session.commit()
            return {'success':f'Notificacion marcada como {msg[1]}'},200
        except Exception as e:
            db.session.rollback()
            abort(400, error=f'No fue posible actualizar la notificacion: {e}')


# -------------------------------- DELETE --------------------------------------
@api.route('/delete/pagados')
class DeleteNotificacionesPagadas(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self):
        try:
            notificaciones = db.session.query(Notificaciones).filter(
                Notificaciones.pagado == True
            ).all()
            # Eliminar las notificaciones pagadas
            for item in notificaciones:
                db.session.delete(item)
            db.session.commit()
            LogsServices(db.session).new_log(logsCategories.notificacion_deleted, current_user.id)
            return {'success': 'Notificaciones pagadas eliminadas'},200
        except Exception:
            db.session.rollback()
            abort(400, error='No fue posible eliminar las notificaciones')


@api.route('/delete/pagados/<int:id_servicio>')
class DeleteNotificacionesServicioPagadas(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_servicio):
        try:
            notificaciones = db.session.query(Notificaciones).filter(
                Notificaciones.id_servicio == id_servicio,
                Notificaciones.pagado == True
            ).all()
            # Eliminar las notificaciones pagadas
            for item in notificaciones:
                db.session.delete(item)
            db.session.commit()
            LogsServices(db.session).new_log(logsCategories.notificacion_deleted, current_user.id)
            return {'success': 'Notificaciones pagadas eliminadas'},200
        except Exception:
            db.session.rollback()
            abort(400, error='No fue posible eliminar las notificaciones')


@api.route('/delete/<int:id_notificacion>')
class DeleteNotification(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_notificacion):
        try:
            notificacion = db.session.query(Notificaciones).get(id_notificacion)
            if notificacion is None: raise Exception('No existe la notificacion')
            db.session.delete(notificacion)
            db.session.commit()
            LogsServices(db.session).new_log(logsCategories.notificacion_deleted, current_user.id)
            return {'success': 'Notificacion eliminada'},200
        except Exception as e:
            db.session.rollback()
            abort(400, error=f'No fue posible eliminar el registro: {e}')
