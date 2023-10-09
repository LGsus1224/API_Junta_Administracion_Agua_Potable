from flask_restx import Namespace,Resource,fields,abort
from flask_login import login_user,login_required,logout_user
from app.libs import db
from app.models import Usuarios,Logs
from app.common.enums import logsCategories


api = Namespace('Acceso y Autenticación', description='Endpoints para el acceso al sistema, autneticación y servicios relacionados')


# Modelo de respuesta correcta
success_message = api.model('Success Response',{
    'success':fields.String(readonly=True, description='Success message')
})


# Modelo de respuesta erronea
error_message = api.model('Error Response',{
    'error':fields.String(readonly=True, description='Error message')
})


@api.route('/sign_in')
class SignIn(Resource):
    signIn_model = api.model('Inicio de sesión',{
        'username':fields.String(required=True, description='Nombre del usuario'),
        'password':fields.String(required=True, description='Contraseña de la cuenta del usuario')
    })

    @api.expect(signIn_model)
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    def post(self):
        """
        Inicio de sesión con credenciales del usuario

        Inicio de sesión del usuario
        """
        try:
            data = api.payload
            username = data['username']
            password = data['password']
            user = Usuarios.query.filter_by(username=username).first()
            if user is None: raise Exception("Usuario o contraseña incorrecta")
            if not user.check_password(user.password,password):
                raise Exception("Usuario o contraseña incorrecta")
            login_user(user)
            new_log = Logs()
            new_log.id_usuario = user.id
            new_log.categoria = logsCategories.login
            db.session.add(new_log)
            db.session.commit()
            return {
                'success':'Inicio de sesión exitoso'
            },200
        except Exception as e:
            db.session.rollback()
            abort(400, error='No se pudo iniciar la sesión: '+str(e))


@api.route('/logout')
class Logout(Resource):
    @api.response(200, 'OK', success_message)
    @api.response(400, 'Bad Request', error_message)
    @login_required
    def post(self):
        """
        Cerrar la sesión del usuario

        Cierra la sesión del usuario
        """
        try:
            logout_user()
            return {
                'success':'Sesion de usuario terminada'
            },200
        except Exception:
            abort(400, error='Hubo un error al intentar cerrar la sesión')

