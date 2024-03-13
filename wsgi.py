from app import create_app
from app.libs import db


settings_module = 'config.settings'

app = create_app(settings_module)

if __name__ == '__main__':
    # with app.app_context():
    #    db.create_all()
    app.run(host='0.0.0.0')