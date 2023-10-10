from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required, current_user
from app.libs import db
from app.common.api_utils import (
    success_message,
    error_message,
)
from app.models import PagosConexion
from app.common.enums import conexionEnums
import datetime


api = Namespace('Pagos Conexion', description='Endpoints de gestion de pagos por conexion de servicios')


# ----------------------------------- GET -----------------------------------------
@api.route('/reconexion/get/all')
class GetAllPagosReconexion(Resource):
    @api.response(200, 'OK')
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
    @api.response(200, 'OK')
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
    @api.response(200, 'OK')
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
                    'total_pagado':total_pagado
                })
            return {'success':results},200
        except Exception:
            abort(400, error='No fue posible obtener los registros')

