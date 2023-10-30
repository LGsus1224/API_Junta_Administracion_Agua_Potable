from sqlalchemy.orm import Session
from app.models import Logs
from app.common.enums import logsCategories
import datetime


class LogsServices():
    def __init__(self, db: Session):
        self.db = db

    def new_log(self, categoria:logsCategories, id_usuario: int, detalle: str = None) -> None:
        try:
            new_log = Logs()
            new_log.categoria = categoria
            new_log.id_usuario = id_usuario
            if detalle is not None:
                new_log.detalle = detalle
            self.db.add(new_log)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise Exception('No fue posible registrar el log')

    def get_all_logs(self):
        try:
            logs = self.db.query(Logs).all()
            return logs
        except Exception:
            raise Exception('No fue posible obtener los registros')

    def delete_old_logs(self) -> None:
        try:
            old_logs = self.get_old_logs()
            for i in old_logs:
                self.db.delete(i)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise Exception('No fue posible eliminar los logs')

    def get_old_logs(self):
        try:
            current_datetime = datetime.datetime.now()
            old_logs_datetime = current_datetime - datetime.timedelta(2*365/12) # fecha actual menos 2 meses
            old_logs = self.db.query(Logs).filter(
                Logs.fecha <= old_logs_datetime
            ).all()
            return old_logs
        except Exception:
            raise Exception('No se pudo obtener los registros')