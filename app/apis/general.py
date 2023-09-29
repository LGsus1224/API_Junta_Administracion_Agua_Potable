from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from app.models import Clientes,Servicios,Planillas
from app.common.api_utils import (
    error_message,
    item_planilla
)
from datetime import datetime


api = Namespace('General', description='Endpoints generales. Estadisticas y rutas varias')


# --------------------------------------- GET -------------------------------------------------
@api.route('/get/stats')
class GetStats(Resource):
    val_stats = api.model('Valores estadisticas', {
        'clientes':fields.Integer(
            readonly = True,
            title = 'N° de clientes',
            description = 'N° de clientes que tiene la app'
        ),
        'servicios':fields.Integer(
            readonly = True,
            title = 'N° de servicios',
            description = 'N° de servicios que tiene la app'
        ),
        'notificaciones':fields.Integer(
            readonly = True,
            title = 'N° de notificaciones',
            description = 'N° de notificaciones que tiene la app'
        ),
    })

    stats = api.model('Estadisticas', {
        'success':fields.Nested(val_stats)
    })

    @api.response(200, 'OK', stats)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener estadisticas

        Obtiene las estadisticas de la aplicación.

        Los valores que devuelve son:
        * N° de clientes
        * N° de servicios
        * N° de notificaciones
        """
        try:
            n_clientes = Clientes.query.count()
            n_servicios = Servicios.query.count()
            n_notificaciones = Planillas.query.filter(
                Planillas.pagado == False
            ).count()
            return {
                'success':{
                    'clientes':n_clientes,
                    'servicios':n_servicios,
                    'notificaciones':n_notificaciones
                }
            },200
        except Exception:
            abort(400, error='No fue posible obtener las estadisticas')


@api.route('/get/planillas/pendientes')
class GetPlanillasPendientes(Resource):
    planillas_pendientes = api.model('Planillas pendientes', {
        'success':fields.List(fields.Nested(item_planilla))
    })

    @api.response(200, 'OK', planillas_pendientes)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener lista de planillas con pago pendiente

        Obtiene la lista de planillas del mes en curso las cuales aun no han sido pagadas
        """
        try:
            planillas = Planillas.query.filter(
                Planillas.pagado == False
            ).all()
            results = []
            for item in planillas:
                results.append({
                    'id':item.id,
                    'servicio':{
                        'id':item.servicio.id,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor,
                        'id_cliente':item.servicio.id_cliente,
                        'direccion':item.servicio.direccion,
                        'estado':item.servicio.estado,
                        'lectura_anterior':item.servicio.lectura_anterior
                    },
                    'cliente':{
                        'id':item.servicio.cliente.id,
                        'cedula':item.servicio.cliente.cedula,
                        'nombres':item.servicio.cliente.nombres,
                        'apellidos':item.servicio.cliente.apellidos,
                        'telefono':item.servicio.cliente.telefono
                    },
                    'fecha_emision':datetime.strftime(item.fecha_emision, '%d/%m/%Y'),
                    'pagado':item.pagado,
                    'consumo_base':item.consumo_base,
                    'exedente':item.exedente,
                    'valor_consumo_base':item.valor_consumo_base,
                    'valor_exedente':item.valor_exedente,
                    'lectura_anterior':item.lectura_anterior,
                    'lectura_actual':item.lectura_actual,
                    'consumo_total':item.consumo_total,
                    'valor_consumo_total':item.valor_consumo_total
                })
            return {
                'success':results
            }
        except:
            abort(400, error='No fue posible obtener los registros')
