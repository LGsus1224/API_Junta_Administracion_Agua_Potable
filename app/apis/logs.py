from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from app.libs import db
from app.common.logs import LogsServices
from app.common.api_utils import (
    error_message,
    success_message
)
import datetime


api = Namespace('Logs', description='Endpoints de logs del sistema')


# -------------------------------------- GET ------------------------------------------
@api.route('/get/all')
class GetAdminAll(Resource):
    log_item = api.model('LogItem',{
        'usuario': fields.String(
            required=True,
            title='Usuario',
            description='Usuario generador del log'
        ),
        'categoria': fields.String(
            required=True,
            title='Categoria de log',
            description='Categoria del log (Login, eliminacion, actualizacion , etc)'
        ),
        'fecha': fields.DateTime(
            required=True,
            title='Fecha',
            description='Fecha de emision del log',
            example='09-10-2023'
        ),
        'hora': fields.DateTime(
            required=True,
            title='Hora',
            description='Hora de emision del log',
            example='10:00'
        ),
        'detalle': fields.String(
            required=True,
            title='Detalle',
            description='Detalle del log (Opcional)'
        )
    })

    all_logs = api.model('AllLogs', {
        'success': fields.Nested(log_item)
    })

    @api.response(200, 'OK', all_logs)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Todos los logs
        """
        try:
            all_logs = LogsServices(db.session).get_all_logs()
            results = []
            for item in all_logs:
                results.append({
                    'usuario':item.usuario.username,
                    'categoria':item.categoria.value,
                    'fecha':datetime.datetime.strftime(item.fecha, '%d-%m-%Y'),
                    'hora':datetime.datetime.strftime(item.fecha, '%H:%M'),
                    'detalle':item.detalle
                })
            return {'success':results},200
        except Exception as e:
            abort(400, error=str(e))


# ----------------------------------- DELETE -----------------------------------
@api.route('/delete/old')
class DeleteOldLogs(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self):
        """
        Eliminar logs con más de 2 meses de antiguedad
        """
        try:
            LogsServices(db.session).delete_old_logs()
            return {'success':'Logs eliminados'},200
        except Exception as e:
            abort(400, error=str(e))
