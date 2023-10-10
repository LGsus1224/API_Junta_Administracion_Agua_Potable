from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_required, current_user
from app.libs import db
from app.models import Usuarios
from app.common.api_utils import (
    error_message,
    success_message,
    is_not_null_empty
)


api = Namespace('Admins', description='Endpoints de gestión de administradores del sistema')


# -------------------------------------- GET ------------------------------------------
@api.route('/get/all')
class GetAdminAll(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def get(self):
        """
        Lista de administradores del sistema
        """
        try:
            admins = db.session.query(Usuarios).filter(Usuarios.id != 1).all()
            results = []
            for item in admins:
                results.append({
                    'id':item.id,
                    'username':item.username,
                })
            return {
                'success':results
            },200
        except Exception:
            abort(code=400, error='No fue posible obtener los registros')


# -------------------------------------- POST -----------------------------------------
@api.route('/new')
class NewAdmin(Resource):
    new_user = api.model('NewAdmin',{
        'username': fields.String(
            required=True,
            title = 'Nombre de usuario',
            description = 'Nombre de usuario'
        ),
        'password': fields.String(
            required = True,
            title = 'Contraseña',
            description = 'Contraseña para el nuevo usuario'
        )
    })

    @api.expect(new_user)
    @api.response(201, 'Created', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self):
        """
        Nuevo administrador del sistema

        Permite crear un nuevo administrador con capacidad de ingresar y manipular el sistema
        """
        try:
            data = api.payload
            username = data['username']
            password = data['password']
            new_user = Usuarios()
            if not is_not_null_empty(username):
                raise Exception('Nombre de usuario vacio')
            if not is_not_null_empty(password):
                raise Exception('Contraseña vacia')
            new_user.username = username
            new_user.password = new_user.hash_password(password)
            db.session.add(new_user)
            db.session.commit()
            return {'success':'Admin registrado'},201
        except Exception:
            db.session.rollback()
            abort(code=400, error='No fue posible registrar al admin')


# -------------------------------------- PUT ------------------------------------------
@api.route('/reset/password')
class ResetPassword(Resource):
    reset_password = api.model('ResetPassword',{
        'id_user': fields.Integer(
            required=True,
            title='ID user',
            description='ID del usuario administrador'
        ),
        'new_password': fields.String(
            required = True,
            title='Nueva contraseña',
            description='Nueva contraseña para la cuenta del administrador'
        )
    })

    @api.expect(reset_password)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def put(self):
        """
        Establecer nueva contraseña para un usuario administrador
        """
        try:
            data = api.payload
            id_user = data['id_user']
            new_password = data['new_password']
            if id_user == 1:
                raise Exception('Superadmin no es editable')
            if not is_not_null_empty(new_password):
                raise Exception('Contraseña vacia')
            # revisar si el id de usuario no es del current_user
            if id_user == current_user.id:
                raise Exception('Usuario de la sesion actual')
            # buscar usuario
            user: Usuarios = db.session.query(Usuarios).get(id_user)
            if user is None:
                raise Exception('No existe el usuario')
            user.password = user.hash_password(new_password)
            db.session.commit()
            return {'success': 'Contraseña restablecida'}
        except Exception as e:
            db.session.rollback()
            abort(400, error=str(e))


# ------------------------------------ DELETE ----------------------------------
@api.route('/delete/<int:id_admin>')
class DeleteAdmin(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def delete(self, id_admin):
        """
        Eliminar un administrador del sistema
        """
        try:
            # buscar usuario
            if id_admin == 1:
                raise Exception('Superadmin no es borrable')
            admin = db.session.query(Usuarios).get(id_admin)
            if admin is None:
                raise Exception('Usuario no encontrado')
            db.session.delete(admin)
            db.session.commit()
            return {'success': 'Usuario eliminado'}
        except Exception as e:
            db.session.rollback()
            abort(400, error=str(e))
