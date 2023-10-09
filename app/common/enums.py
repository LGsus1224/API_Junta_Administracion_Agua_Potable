import enum


class logsCategories(enum.Enum):
    login = 'login'
    cliente_created = 'cliente_created'
    cliente_deleted = 'cliente_deleted'
    servicio_created = 'servicio_created'
    servicio_deleted = 'servicio_deleted'
    planilla_deleted = 'planilla_deleted'


class conexionEnums(enum.Enum):
    contado = 'contado'
    financiamiento = 'financiamiento'
    reconexion = 'reconexion'
