from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from sqlalchemy import extract
from app.libs import db
from app.models import Planillas,Servicios,Configuracion
from app.common.api_utils import (
    success_message,
    error_message,
    item_planilla
)
from datetime import datetime


api = Namespace('Planillas', description='Endpoints para la gestión de planillas')


# ------------------------------------- GET ---------------------------------------
@api.route('/get/all/<int:id_servicio>')
class GetAllPlanillas(Resource):
    item_planilla = api.model('Item planilla de servicio', {
        'id':fields.Integer(
            readonly = True,
            title = 'Id de planilla',
            description = 'Id de planilla',
        ),
        'id_servicio':fields.Integer(
            readonly = True,
            title = 'ID servicio',
            description = 'ID del servicio al que pertenece la planilla'
        ),
        'fecha_emision':fields.String(
            readonly = True,
            title = 'Fecha de emisión',
            description = 'Fecha de emisión de la planilla',
            example = 'dd/mm/yyyy',
            pattern = '^\d{2}/\d{2}/\d{4}$'
        ),
        'pagado':fields.Boolean(
            readonly = True,
            title = 'Estado de pago',
            description = 'Estado del pago de planilla. True -> Pagado, False -> No pagado'
        ),
        'consumo_base':fields.Float(
            readonly = True,
            title = 'Consumo base',
            description = 'Default consumo base en m³'
        ),
        'exedente':fields.Float(
            readonly = True,
            title = 'Exedente',
            description = 'Default exedente en m³'
        ),
        'valor_consumo_base':fields.Float(
            readonly = True,
            title = 'Valor consumo base',
            description = 'Precio por el nivel de consumo base'
        ),
        'valor_exedente':fields.Float(
            readonly = True,
            title = 'Valor exedente',
            description = 'Precio por cada exedente'
        ),
        'lectura_anterior':fields.Integer(
            readonly = True,
            title = 'Lectura anterior',
            description = 'Lectura anterior del servicio'
        ),
        'lectura_actual':fields.Integer(
            readonly = True,
            title = 'Lectura actual',
            description = 'Lectura actual del servicio'
        ),
        'consumo_total':fields.Integer(
            readonly = True,
            title = 'Consumo total',
            description = 'Consumo total de servicio de agua en m³'
        ),
        'valor_consumo_total':fields.Float(
            readonly = True,
            title = 'Valor consumo total',
            description = 'Valor de consumo total en dinero'
        )
    })

    lista_planillas = api.model('Lista planillas', {
        'success':fields.List(fields.Nested(item_planilla))
    })

    @api.response(200, 'OK', lista_planillas)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self, id_servicio):
        """
        Obtener planillas se los servicios

        Obtiene todas las planillas emitidas par el servicio seleccionado
        """
        try:
            servicio = Servicios.query.get(id_servicio)
            if servicio is None: raise Exception('No existe el servicio buscado')
            planillas = Planillas.query.filter_by(id_servicio=id_servicio).all()
            results = []
            for item in planillas:
                results.append({
                    'id':item.id,
                    'id_servicio':item.id_servicio,
                    'fecha_emision':datetime.strftime(item.fecha_emision, '%d/%m/%Y'),
                    'consumo_base':item.consumo_base,
                    'exedente':item.exedente,
                    'valor_consumo_base':item.valor_consumo_base,
                    'valor_exedente':item.valor_exedente,
                    'lectura_anterior':item.lectura_anterior,
                    'lectura_actual':item.lectura_actual,
                    'consumo_total':item.consumo_total,
                    'valor_consumo_total':item.valor_consumo_total,
                    'pagado':item.pagado
                })
            return {
                'success':results
            },200
        except Exception as e:
            abort(400, error='No fue posible obtener los registros: ' + str(e))


@api.route('/get/<int:id_planilla>')
class GetPlanilla(Resource):
    planilla = api.model('Planilla de servicio', {
        'success':fields.Nested(item_planilla)
    })

    @api.response(200, 'OK', planilla)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self, id_planilla):
        """
        Obtener la planilla

        Obtener la planilla por su id
        """
        try:
            planilla = Planillas.query.get(id_planilla)
            if planilla is None:
                raise Exception('No existe la planilla buscada')
            return {
                'success':{
                    'id':planilla.id,
                    'servicio':{
                        'id':planilla.servicio.id,
                        'n_conexion':planilla.servicio.n_conexion,
                        'n_medidor':planilla.servicio.n_medidor,
                        'id_cliente':planilla.servicio.id_cliente,
                        'direccion':planilla.servicio.direccion,
                        'estado':planilla.servicio.estado,
                        'lectura_anterior':planilla.servicio.lectura_anterior
                    },
                    'cliente':{
                        'id':planilla.servicio.cliente.id,
                        'cedula':planilla.servicio.cliente.cedula,
                        'nombres':planilla.servicio.cliente.nombres,
                        'apellidos':planilla.servicio.cliente.apellidos,
                        'telefono':planilla.servicio.cliente.telefono
                    },
                    'fecha_emision':datetime.strftime(planilla.fecha_emision, '%d/%m/%Y'),
                    'pagado':planilla.pagado,
                    'consumo_base':planilla.consumo_base,
                    'exedente':planilla.exedente,
                    'valor_consumo_base':planilla.valor_consumo_base,
                    'valor_exedente':planilla.valor_exedente,
                    'lectura_anterior':planilla.lectura_anterior,
                    'lectura_actual':planilla.lectura_actual,
                    'consumo_total':planilla.consumo_total,
                    'valor_consumo_total':planilla.valor_consumo_total
                }
            },200
        except Exception as e:
            abort(400, error='No fue posible obtener la planilla: ' + str(e))


# --------------------------------------- NEW --------------------------------------
@api.route('/new')
class NewPlanilla(Resource):
    new_planilla = api.model('Nueva planilla', {
        'id_servicio':fields.Integer(
            required=True,
            title = 'ID servicio',
            description='ID del servicio de un usuario'
        ),
        'lectura_actual':fields.Integer(
            required = True,
            title = 'Lectura actual',
            description = 'Lectura actual del medidor'
        )
    })

    @api.expect(new_planilla)
    @api.response(201, 'Created', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self):
        """
        Nueva planilla de pago

        Se registra una nueva planilla de pago de servicio
        La planilla se dirige al servicio del usuario y no al usuario como tal
        """
        try:
            data = api.payload
            id_servicio = data['id_servicio']
            lectura_actual = data['lectura_actual']
            fecha_emision = datetime.now()
            # Consultar servicio por su id
            servicio = Servicios.query.get(id_servicio)
            if servicio is None: raise Exception('No existe el servicio buscado')
            lectura_anterior = servicio.lectura_anterior
            # Verificar que el servicio este activo
            if not servicio.estado:
                raise Exception('Servicio apagado')
            # Verificar que la nueva lectura no sea menor que la lectura anterior
            if lectura_actual < lectura_anterior:
                raise Exception('Error en las lecturas. Lectura actual es menor a la lectura anterior')
            # Verificar que no se haya emitido una planilla de este mes para ese servicio
            planilla = Planillas.query.filter(
                extract('month',Planillas.fecha_emision) == fecha_emision.month,
                extract('year', Planillas.fecha_emision) == fecha_emision.year
            ).first()
            if planilla is not None:
                raise Exception('Ya se emitio una planilla en este mes para el servicio')
            # Obtener datos de configuracion
            configuracion = Configuracion.query.first()
            if configuracion is None:
                raise Exception('No existen valores de configuracion')
            consumo_base = configuracion.consumo_base
            exedente = configuracion.exedente
            valor_consumo_base = configuracion.valor_consumo_base
            valor_exedente = configuracion.valor_exedente
            # Calcular consumo total
            consumo_total = lectura_actual - lectura_anterior
            valor_consumo_total = valor_consumo_base
            if consumo_total > consumo_base:
                valor_consumo_total += ((consumo_total-consumo_base)/exedente)*valor_exedente
            # Crear nueva planilla
            new_planilla = Planillas()
            new_planilla.id_servicio = id_servicio
            new_planilla.fecha_emision = fecha_emision
            new_planilla.consumo_base = consumo_base
            new_planilla.exedente = exedente
            new_planilla.valor_consumo_base = valor_consumo_base
            new_planilla.valor_exedente = valor_exedente
            new_planilla.lectura_anterior = lectura_anterior
            new_planilla.lectura_actual = lectura_actual
            new_planilla.consumo_total = consumo_total
            new_planilla.valor_consumo_total = valor_consumo_total
            new_planilla.pagado = False
            db.session.add(new_planilla)
            # Actualizar lectura_anterior del servicio
            servicio.lectura_anterior = lectura_actual
            db.session.commit()
            return {
                'success':'Se registro la planilla de pago'
            }, 201
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible registrar la planilla de pago: ' + str(e))


# ------------------------------------- UPDATE --------------------------------------
@api.route('/update/pago/<int:id_planilla>')
class UpdatePagoPlanilla(Resource):
    actualizar_pago = api.model('Actualizar pago planilla', {
        'pagado':fields.Boolean(
            required = True,
            title = 'Planilla pagada',
            description = 'Estado de pago de planilla. True -> pagado, False -> No Pagado'
        )
    })

    @api.expect(actualizar_pago)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_planilla):
        """
        Actualizar estado de la planilla

        Varia el estado de la planilla por True -> Pagado, y False -> No Pagado
        """
        try:
            data = api.payload
            pagado = data['pagado']
            planilla = Planillas.query.get(id_planilla)
            if planilla is None:
                raise Exception('No existe la planilla buscada')
            if planilla.pagado != pagado:
                planilla.pagado = pagado
                db.session.commit()
            return {
                'success':'Pago de planilla actualizado'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible actualizar el estado de pago de la planilla')


@api.route('/update/lectura/<int:id_planilla>')
class UpdateLecturaPlanilla(Resource):
    editar_lectura = api.model('Editar lectura', {
        'nueva_lectura':fields.Integer(
            required = True,
            title = 'Nueva lectura',
            description = 'Nueva lectura del servicio'
        )
    })

    @api.expect(editar_lectura)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_planilla):
        """
        Actualizar lectura_actual de servicio

        Actualiza la lectura actual de la planilla y recalcular el consumo total y costos
        """
        try:
            data = api.payload
            nueva_lectura = data['nueva_lectura']
            fecha_actual = datetime.now()
            # Buscar planilla
            planilla = Planillas.query.get(id_planilla)
            if planilla is None:
                raise Exception('No existe la planilla buscada')
            if planilla.fecha_emision.month != fecha_actual.month or planilla.fecha_emision.year != fecha_actual.year:
                raise Exception('La planilla seleccionada no corresponde al mes en curso')
            if planilla.pagado:
                raise Exception('La planilla ya ha sido pagada')
            if nueva_lectura < planilla.lectura_anterior:
                raise Exception('Error en lecturas. Lectura anterior es menor a nueva lectura')
            # Recalcular costos
            consumo_total = nueva_lectura - planilla.lectura_anterior
            valor_consumo_total = planilla.valor_consumo_base
            if consumo_total > planilla.consumo_base:
                valor_consumo_total += ((consumo_total-planilla.consumo_base)/planilla.exedente)*planilla.valor_exedente
            planilla.consumo_total = consumo_total
            planilla.valor_consumo_total = valor_consumo_total
            planilla.lectura_actual = nueva_lectura
            # Actualizar lectura en en servicio
            planilla.servicio.lectura_anterior = nueva_lectura
            db.session.commit()
            return {
                'success':'Planilla actualizada'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible cambiar la lectura: ' + str(e))


# ----------------------------------- DELETE ---------------------------------------
@api.route('/delete/<int:id_planilla>')
class DeletePlanilla(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_planilla):
        """
        Eliminar una planilla de pago

        Eliminar una planilla de pago de servicio y actualizar la ultima lectura
        """
        try:
            fecha_actual = datetime.now()
            planilla = Planillas.query.get(id_planilla)
            # Verificar si planilla existe
            if planilla is None: raise Exception('No existe la planilla buscada')
            # Verificar que la planilla no sea del mes en curso
            if planilla.fecha_emision.month == fecha_actual.month and planilla.fecha_emision.year == fecha_actual.year:
                planilla.servicio.lectura_anterior = planilla.lectura_anterior
            db.session.delete(planilla)
            db.session.commit()
            return {
                'success':'Planilla de pago eliminada'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible eliminar la planilla de pago: ' + str(e))

