import enum


class logsCategories(enum.Enum):
    login = 'login'
    cliente_created = 'cliente_created'
    cliente_deleted = 'cliente_deleted'
    servicio_created = 'servicio_created'
    servicio_deleted = 'servicio_deleted'
    planilla_deleted = 'planilla_deleted'
    notificacion_created = 'notificacion_created'
    notificacion_deleted = 'notificacion_deleted'
    notificacion_cobrada = 'notificacion_cobrada'


class conexionEnums(enum.Enum):
    contado = 'contado'
    financiamiento = 'financiamiento'
    reconexion = 'reconexion'
