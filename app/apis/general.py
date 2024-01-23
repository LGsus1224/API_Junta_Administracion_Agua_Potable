from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from app.libs import db
from sqlalchemy import extract, func
from app.models import Clientes,Servicios,Planillas,PagosConexion
from app.common.api_utils import (
    error_message,
    item_planilla
)
from app.common.enums import conexionEnums
from datetime import datetime, timedelta


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
        except Exception:
            abort(400, error='No fue posible obtener los registros')


@api.route('/get/stats/cobros/planilla')
class GetStatsCobrosPlanilla(Resource):
    cobros_planillas = api.model('StatsCobrosPlanillas', {
        'semana':fields.List(
            fields.Integer,
            readonly = True,
            title = 'Total recaudado en la semana',
            default=[0 for i in range(7)]
        ),
        'mes':fields.List(
            fields.Integer,
            readonly = True,
            title = 'Total recaudado en el año',
            default = [0 for i in range(13)]

        )
    })

    stats = api.model('Estadisticas', {
        'success':fields.Nested(cobros_planillas)
    })

    @api.response(200, 'OK', stats)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener estadisticas de los cobros por planillas
        """
        try:
            current_date = datetime.now()
            # Calculo total por cada dia de la semana en curso
            dia_semana = current_date.weekday()
            inicio_semana = (current_date - timedelta(days=dia_semana)).date()
            fin_semana = (current_date + timedelta(days=6)).date()
            planillas_semana: list[Planillas] = Planillas.query.filter(
                Planillas.fecha_emision >= inicio_semana,
                Planillas.fecha_emision <= fin_semana
            ).all()
            resumen_semana = [0 for i in range(7)]
            for ps in planillas_semana:
                resumen_semana[ps.fecha_emision.weekday()] += ps.valor_consumo_total

            # Calcular el total por cada mes del año en curso
            planillas_meses: list[Planillas] = Planillas.query.filter(
                extract('year',Planillas.fecha_emision) == current_date.year
            ).all()
            resumen_meses = [0 for i in range(13)]
            for pm in planillas_meses:
                resumen_meses[pm.fecha_emision.month-1] += pm.valor_consumo_total
            # Response
            return {
                'success':{
                    'semana':resumen_semana,
                    'mes':resumen_meses
                }
            }
        except Exception:
            abort(400, error='No fue posible obtener el resumen de cobros')


@api.route('/get/stats/cobros/conexion')
class GetStatsCobrosConexion(Resource):
    @api.response(200, 'OK', )
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener estadisticas de los cobros por conexion
        """
        try:
            current_date = datetime.now() # Fecha actual
            total_default_meses = [0 for mes in range(1,13)] # Lista default de valores por mes
            # Labels para la consulta select
            query_labels = [
                func.sum(PagosConexion.entrada + PagosConexion.cuota1 + PagosConexion.cuota2 +
                        PagosConexion.cuota3 + PagosConexion.cuota4 + PagosConexion.cuota5 +
                        PagosConexion.cuota6).label('total'),
                extract('month', PagosConexion.fecha_emision).label('month'),
                extract('year', PagosConexion.fecha_emision).label('year')
            ]

            # Consultar el total de pagos por conexion al contado
            total_pagos_conexion_contado = db.session.query(*query_labels).filter(
                PagosConexion.tipo == conexionEnums.contado,
                extract('year', PagosConexion.fecha_emision) == current_date.year
            ).group_by(
                extract('month', PagosConexion.fecha_emision),
                extract('year', PagosConexion.fecha_emision),
            ).all()

            # Crea un diccionario con valor por mes
            resumen_conexion_contado = total_default_meses.copy()

            # Actualizar el elemento n del mes en la lista
            for group in total_pagos_conexion_contado:
                resumen_conexion_contado[group.month-1] = group.total

            # Consultar el total de pagos de conexion por financiamiento
            total_pagos_conexion_financiamiento = db.session.query(*query_labels).filter(
                PagosConexion.tipo == conexionEnums.financiamiento,
                extract('year', PagosConexion.fecha_emision) == current_date.year
            ).group_by(
                extract('month', PagosConexion.fecha_emision),
                extract('year', PagosConexion.fecha_emision),
            ).all()

            # Crea un diccionario con valor por mes
            resumen_conexion_financiamiento = total_default_meses.copy()

            # Actualizar el elemento n del mes en la lista
            for group in total_pagos_conexion_financiamiento:
                resumen_conexion_financiamiento[group.month-1] = group.total

            # Consultar el total de pagos de conexion por reconexion
            total_pagos_reconexion = db.session.query(*query_labels).filter(
                PagosConexion.tipo == conexionEnums.reconexion.value,
                extract('year', PagosConexion.fecha_emision) == current_date.year
            ).group_by(
                extract('month', PagosConexion.fecha_emision),
                extract('year', PagosConexion.fecha_emision),
            ).all()

            # Crea un diccionario con valor por mes
            resumen_reconexion = total_default_meses.copy()

            # Actualizar el elemento n del mes en la lista
            for group in total_pagos_reconexion:
                resumen_reconexion[group.month-1] = group.total

            return {'success':{
                'resumen_conexion_contado':resumen_conexion_contado,
                'resumen_conexion_financiamiento':resumen_conexion_financiamiento,
                'resumen_reconexion':resumen_reconexion
            }},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')
