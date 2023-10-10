from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required
from app.libs import db
from app.common.api_utils import (
    success_message,
    error_message,
    item_servicio,
    item_cliente,
    nullable
)
from app.models import PagosConexion
from app.common.enums import conexionEnums
import datetime


api = Namespace('Pagos Conexion', description='Endpoints de gestion de pagos por conexion de servicios')


# ----------------------------------- GET -----------------------------------------
@api.route('/reconexion/get/all')
class GetAllPagosReconexion(Resource):
    pago_reconexion_item = api.model('PagoReconexionItem', {
        'id': fields.Integer(title='ID'),
        'servicio':fields.Nested(item_servicio),
        'cliente':fields.Nested(item_cliente),
        'fecha_emision':fields.String(title='Fecha de emision', example='12-12-2000'),
        'hora_emision':fields.String(title='Hora de emision', example='10:00'),
        'total':fields.Float(title='Total cobrado')
    })

    all_pagos_reconexion = api.model('AllPagosReconexion', {
        'success':fields.Nested(pago_reconexion_item)
    })

    @api.response(200, 'OK', all_pagos_reconexion)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener lista de todos los pagos por reconexion
        """
        try:
            pagos = PagosConexion.query.filter(
                PagosConexion.tipo == conexionEnums.reconexion
            ).all()
            results = []
            for item in pagos:
                item: PagosConexion
                results.append({
                    'id':item.id,
                    'servicio':{
                        'id':item.servicio.id,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor,
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
                    'fecha_emision':datetime.datetime.strftime(item.fecha_emision, '%d-%m-%Y'),
                    'hora_emision':datetime.datetime.strftime(item.fecha_emision, '%H:%M'),
                    'total':item.total
                })
            return {'success':results},200
        except Exception as e:
            abort(400, error='No fue posible obtener los registros: ' + str(e))


@api.route('/contado/get/all')
class GetAllPagosContado(Resource):
    pago_contado_item = api.model('PagoContadoItem', {
        'id': fields.Integer(title='ID'),
        'servicio':fields.Nested(item_servicio),
        'cliente':fields.Nested(item_cliente),
        'fecha_emision':fields.String(title='Fecha de emision', example='12-12-2000'),
        'hora_emision':fields.String(title='Hora de emision', example='10:00'),
        'total':fields.Float(title='Total cobrado')
    })

    all_pagos_contado = api.model('AllPagosContado', {
        'success':fields.Nested(pago_contado_item)
    })

    @api.response(200, 'OK', all_pagos_contado)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener lista de todos los pagos de conexion por contado
        """
        try:
            pagos = PagosConexion.query.filter(
                PagosConexion.tipo == conexionEnums.contado
            ).all()
            results = []
            for item in pagos:
                item: PagosConexion
                results.append({
                    'id':item.id,
                    'servicio':{
                        'id':item.servicio.id,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor,
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
                    'fecha_emision':datetime.datetime.strftime(item.fecha_emision, '%d-%m-%Y'),
                    'hora_emision':datetime.datetime.strftime(item.fecha_emision, '%H:%M'),
                    'total':item.total
                })
            return {'success':results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')


@api.route('/financiamiento/get/all')
class GetAllPagosFinanciamiento(Resource):
    pago_financiamiento_item = api.model('PagoFinanciamientoItem', {
        'id': fields.Integer(title='ID'),
        'servicio':fields.Nested(item_servicio),
        'cliente':fields.Nested(item_cliente),
        'fecha_emision':fields.String(title='Fecha de emision', example='12-12-2000'),
        'hora_emision':fields.String(title='Hora de emision', example='10:00'),
        'total':fields.Float(title='Total cobrado'),
        'entrada':fields.Float(title='Entrada del pago ($100)', example=100),
        'cuota1':fields.Float(title='Cuota1', example=0),
        'cuota2':fields.Float(title='Cuota2', example=0),
        'cuota3':fields.Float(title='Cuota3', example=0),
        'cuota4':fields.Float(title='Cuota4', example=0),
        'cuota5':fields.Float(title='Cuota5', example=0),
        'cuota6':fields.Float(title='Cuota6', example=0),
        'total_pagar':fields.Float(title='Total a pagar ($250)', example=250),
        'total_pagado':fields.Float(title='Total pagado hasta el momento'),
        'restante_pagar':fields.Float(title='Valor restante por cobrar')
    })

    all_pagos_financiamiento = api.model('AllPagosFinanciamiento', {
        'success':fields.Nested(pago_financiamiento_item)
    })

    @api.response(200, 'OK', all_pagos_financiamiento)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Obtener lista de todos los pagos de conexion por financiamiento
        """
        try:
            pagos = PagosConexion.query.filter(
                PagosConexion.tipo == conexionEnums.financiamiento
            ).all()
            results = []
            for item in pagos:
                item: PagosConexion
                cuota1 = item.cuota1 if item.cuota1 is not None else 0
                cuota2 = item.cuota2 if item.cuota2 is not None else 0
                cuota3 = item.cuota3 if item.cuota3 is not None else 0
                cuota4 = item.cuota4 if item.cuota4 is not None else 0
                cuota5 = item.cuota5 if item.cuota5 is not None else 0
                cuota6 = item.cuota6 if item.cuota6 is not None else 0
                total_pagar = item.entrada
                total_pagado = total_pagar+cuota1+cuota2+cuota3+cuota4+cuota5+cuota6
                results.append({
                    'id':item.id,
                    'servicio':{
                        'id':item.servicio.id,
                        'n_conexion':item.servicio.n_conexion,
                        'n_medidor':item.servicio.n_medidor,
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
                    'fecha_emision':datetime.datetime.strftime(item.fecha_emision, '%d-%m-%Y'),
                    'hora_emision':datetime.datetime.strftime(item.fecha_emision, '%H:%M'),
                    'entrada':item.entrada,
                    'cuota1':cuota1,
                    'cuota2':cuota2,
                    'cuota3':cuota3,
                    'cuota4':cuota4,
                    'cuota5':cuota5,
                    'cuota6':cuota6,
                    'total_pagar':item.total,
                    'total_pagado':total_pagado,
                    'restante_pagar':item.total - total_pagado
                })
            return {'success':results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')


# --------------------------------- PUT ---------------------------------------
@api.route('/financiamiento/update/cuotas/<int:id_pago>')
class UpdatePagoFinanciamientoCuotas(Resource):
    cuotas_financiamiento = api.model('CuotasFinanciamiento', {
        'cuota1': nullable(
            fields.Float,
            title = 'Cuota 1',
            min=0
        ),
        'cuota2': nullable(
            fields.Float,
            title = 'Cuota 2',
            min=0
        ),
        'cuota3': nullable(
            fields.Float,
            title = 'Cuota 3',
            min=0
        ),
        'cuota4': nullable(
            fields.Float,
            title = 'Cuota 4',
            min=0
        ),
        'cuota5': nullable(
            fields.Float,
            title = 'Cuota 5',
            min=0
        ),
        'cuota6': nullable(
            fields.Float,
            title = 'Cuota 6',
            min=0
        ),
    })

    @api.expect(cuotas_financiamiento)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self, id_pago):
        """
        Actualizar el pago de cuotas de financiamiento
        """
        try:
            data = api.payload
            cuota1 = data['cuota1']
            cuota2 = data['cuota2']
            cuota3 = data['cuota3']
            cuota4 = data['cuota4']
            cuota5 = data['cuota5']
            cuota6 = data['cuota6']
            # buscar pago
            pago: PagosConexion = PagosConexion.query.get(id_pago)
            if pago is None:
                raise Exception('No existe el registro')
            total_pagado = pago.entrada+cuota1+cuota2+cuota3+cuota4+cuota5+cuota6
            if total_pagado > pago.total:
                raise Exception('Valor sobrepasa el total a pagar')
            pago.cuota1 = cuota1
            pago.cuota2 = cuota2
            pago.cuota3 = cuota3
            pago.cuota4 = cuota4
            pago.cuota5 = cuota5
            pago.cuota6 = cuota6
            db.session.commit()
            return {'success':'Cuotas actualizadas'},200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No fue posible actualizar las cuotas: ' + str(e))


# -------------------------------- DELETE --------------------------------------
# @api.route('/delete/<int:id_pago>')
# class DeletePagoReconexion(Resource):
#     @api.response(200, 'OK', success_message)
#     @api.response(400, 'Bad Request', error_message)
#     @login_required
#     def delete(self, id_pago):
#         """
#         Eliminar un pago por reconexion
#         """
#         try:
#             # buscar el pago
#             pago: PagosConexion = PagosConexion.query.get(id_pago)
#             if pago is None:
#                 raise Exception('No existe el pago de reconexion')
#             # Si el pago es del tipo financiamiento comprobar si ya ha sido pagado en su totalidad
#             if pago.tipo == conexionEnums.financiamiento:
#                 cuota1 = pago.cuota1 if pago.cuota1 is not None else 0
#                 cuota2 = pago.cuota2 if pago.cuota2 is not None else 0
#                 cuota3 = pago.cuota3 if pago.cuota3 is not None else 0
#                 cuota4 = pago.cuota4 if pago.cuota4 is not None else 0
#                 cuota5 = pago.cuota5 if pago.cuota5 is not None else 0
#                 cuota6 = pago.cuota6 if pago.cuota6 is not None else 0
#                 total_pagado = pago.entrada+cuota1+cuota2+cuota3+cuota4+cuota5+cuota6
#                 # Si el pago financiado aun no ha sido pagado lanzar excepcion
#                 if total_pagado < pago.total:
#                     raise Exception('Aun no se ha completado el pago')
#             db.session.delete(pago)
#             db.session.commit()
#             return {'success':'Pago eliminado'},200
#         except Exception as e:
#             db.session.rollback()
#             abort(400, error='No fue posible eliminar el pago: ' + str(e))
