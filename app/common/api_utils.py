from flask_restx import fields
from app.libs import api


# ----------------------------- CLASES --------------------------------
# Clase para instanciar fields nulos
def nullable(fld, *args, **kwargs):
    """Makes any field nullable."""

    class NullableField(fld):
        """Nullable wrapper."""

        __schema_type__ = [fld.__schema_type__, "null"]
        __schema_example__ = f"nullable {fld.__schema_type__}"

    return NullableField(*args, **kwargs)


# ------------------------------ FUNCIONES ------------------------------
# Funcion para verificar si la variable es nula o se encuentra vacia
def is_not_null_empty(variable):
    if type(variable) is int:
        return True if variable is not None else False
    elif type(variable) is str:
        return True if variable is not None and variable.strip() != '' else False


# ------------------------------- MODELOS --------------------------------
# Modelo de respuesta correcta
success_message = api.model('Success Response',{
    'success':fields.String(
        readonly = True,
        title = 'Mensaje',
        description = 'Success message'
    )
})


# Modelo de respuesta erronea
error_message = api.model('Error Response',{
    'error':fields.String(
        readonly = True,
        title = 'Mensaje',
        description = 'Error message'
    )
})


# Modelo de cliente
item_cliente = api.model('Cliente', {
    'id':fields.Integer(
        readonly = True,
        title = 'ID',
        description = 'Id del cliente'
    ),
    'cedula':fields.String(
        readonly=True,
        title = 'Numero de cedula',
        description = 'Número de cédula del cliente',
        example = '0200001145'
    ),
    'nombres':fields.String(
        readonly = True,
        title = 'Nombres del cliente',
        description = 'Nombres del cliente'
    ),
    'apellidos':fields.String(
        readonly = True,
        title = 'Apellidos del cliente',
        description = 'Apellidos del cliente'
    ),
    'telefono':fields.String(
        readonly = True,
        title = 'Numero de telefono',
        description = 'Número de teléfono del cliente'
    )
})


# Modelo de servicio
item_servicio = api.model('Servicio', {
    'id':fields.Integer(
        readonly=True,
        title = 'ID',
        description='Id del servicio'
    ),
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
    'id_cliente':fields.Integer(
        readonly=True,
        title = 'ID cliente',
        description='Id de cliente del servicio'
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
    )
})


# Modelo de planilla
item_planilla = api.model('Planilla de pago', {
    'id':fields.Integer(
        readonly = True,
        title = 'Id de planilla',
        description = 'Id de planilla',
    ),
    'servicio':fields.Nested(item_servicio),
    'cliente':fields.Nested(item_cliente),
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

