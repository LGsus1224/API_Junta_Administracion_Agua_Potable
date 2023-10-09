from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from sqlalchemy import extract
from app.models import Configuracion,Planillas
from app.libs import db
from app.common.api_utils import (
    success_message,
    error_message,
    nullable
)
from datetime import datetime


api = Namespace('Configuración', description='Endpoints relacionados con la configuracion de valores por defecto')


# --------------------------------------- GET -----------------------------------------
@api.route('/get/default')
class GetDefault(Resource):
    configuracion = api.model('Configuracion', {
        'consumo_base':fields.Float(
            readonly = True,
            title = 'Consumo base',
            description = 'Total de consumo base por defecto'
        ),
        'exedente':fields.Float(
            readonly = True,
            title = 'Exedente',
            description = 'Total de exedente'
        ),
        'valor_consumo_base':fields.Float(
            readonly = True,
            title = 'Valor consumo base',
            description = 'Precio por el consumo base'
        ),
        'valor_exedente':fields.Float(
            readonly = True,
            title = 'Valor exedente',
            description = 'Precio default por cada exedente'
        ),
        'reconexion':fields.Float(
            readonly = True,
            title = 'Reconexión de servicio',
            description = 'Precio a pagar por reconexión de servicio'
        )
    })

    configuracion_actual = api.model('Configuracion actual', {
        'success':fields.Nested(configuracion)
    })

    @api.response(200, 'OK', configuracion_actual)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener valores por defecto

        Devuelve los valores por defecto de la configuración
        """
        try:
            configuracion = Configuracion.query.first()
            if configuracion is None:
                raise Exception('No existen valores predeterminados')
            return {
                'success':{
                    'consumo_base':configuracion.consumo_base,
                    'exedente':configuracion.exedente,
                    'valor_consumo_base':configuracion.valor_consumo_base,
                    'valor_exedente':configuracion.valor_exedente,
                    'reconexion':configuracion.reconexion
                }
            },200
        except Exception as e:
            abort(400, error='No fue posible obtener la configuracion: ' + str(e))


# ----------------------------------------- UPDATE ------------------------------------
@api.route('/update/default')
class UpdateConfiguracion(Resource):
    configuracion = api.model('Actualizar configuracion', {
        'consumo_base':nullable(
            fields.Float,
            required = True,
            title = 'Consumo base (Opcional)',
            description = 'Total de consumo base por defecto'
        ),
        'exedente':nullable(
            fields.Float,
            required = True,
            title = 'Exedente (Opcional)',
            description = 'Total de exedente'
        ),
        'valor_consumo_base':nullable(
            fields.Float,
            required = True,
            title = 'Valor consumo base (Opcional)',
            description = 'Precio por el consumo base'
        ),
        'valor_exedente':nullable(
            fields.Float,
            required = True,
            title = 'Valor exedente (Opcional)',
            description = 'Precio default por cada exedente'
        ),
        'reconexion':nullable(
            fields.Float,
            required = True,
            title = 'Valor por reconexion (Opcional)',
            description = 'Precio a pagar por reconexion del servicio'
        )
    })

    @api.expect(configuracion)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self):
        """
        Editar configuracion

        Editar los valores de la configuracion.
        Si no existe ningun valor de configuracion se creara uno.

        Los valores enviados para la configuracion deben ser numéricos y son opcionales.
        Si no se quiere actualizar un valor de la configuración y dejarlo como se encuentra debe pasar null.
        """
        try:
            data = api.payload
            consumo_base = data['consumo_base']
            exedente = data['exedente']
            valor_consumo_base = data['valor_consumo_base']
            valor_exedente = data['valor_exedente']
            reconexion = data['reconexion']
            # Buscar configuracion
            configuracion = Configuracion.query.first()
            if configuracion is None:
                if consumo_base is None:
                    raise Exception('<consumo_base> no tiene un valor')
                elif exedente is None:
                    raise Exception('<exedente> no tiene un valor')
                elif valor_consumo_base is None:
                    raise Exception('<valor_consumo_base> no tiene un valor')
                elif valor_exedente is None:
                    raise Exception('<valor_exedente> no tiene un valor')
                new_configuracion = Configuracion()
                new_configuracion.consumo_base = consumo_base
                new_configuracion.exedente = exedente
                new_configuracion.valor_consumo_base = valor_consumo_base
                new_configuracion.valor_exedente = valor_exedente
                db.session.add(new_configuracion)
            else:
                fecha_actual = datetime.now()
                planillas = Planillas.query.filter(
                    extract('month', Planillas.fecha_emision) == fecha_actual.month,
                    extract('year', Planillas.fecha_emision) == fecha_actual.year
                ).all()
                if len(planillas) > 0:
                    raise Exception('Existen planillas de este mes emitidas con esta configuracion')
                if consumo_base is not None:
                    configuracion.consumo_base = consumo_base
                if exedente is not None:
                    configuracion.exedente = exedente
                if valor_consumo_base is not None:
                    configuracion.valor_consumo_base = valor_consumo_base
                if valor_exedente is not None:
                    configuracion.valor_exedente = valor_exedente
                if reconexion is not None:
                    configuracion.valor_exedente = valor_exedente
            db.session.commit()
            return {
                'success':'Configuracion cambiada'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible actualizar la configuracion: ' + str(e))
