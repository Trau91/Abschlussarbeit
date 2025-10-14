import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager # Neu Hinzugefügt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager() # NEU: Initialisierung des LoginManagers

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)  # NEU: Flask-Login mit der App verbinden
    login_manager.login_view = 'main.login'  # NEU: Route für die Login-Seite festlegen
    login_manager.login_message_category = 'info'  # NEU: Kategorie für Flash-Nachrichten beim Login

    # NEU: Flask-Login user_loader Funktion
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    # Stelle sicher, dass der UPLOAD_FOLDER existiert
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Blueprints registrieren
    from app.blueprints.main.routes import main as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.admin.routes import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin') # Admin-Routen bekommen einen Präfix

    with app.app_context():
        db.create_all() # Erstellt Datenbanktabellen, falls sie noch nicht existieren

        # Beispielbeiträge nur hinzufügen, wenn die Datenbank leer ist
        from app.models import Post, User
        if not Post.query.first():
            print("Füge Beispielbeiträge hinzu...")
            post1 = Post(
                title='Erster Prototypen-Update',
                content='Heute haben wir mit dem Bau des Hauptrahmens begonnen. Es läuft gut!',
                image_file='prototype_update.jpg'
            )
            post2 = Post(
                title='Elektronik-Integration',
                content='Die ersten Sensoren sind angeschlossen und die Verkabelung ist fast abgeschlossen. Eine Herausforderung war die Wasserdichtigkeit.',
                image_file='electronics_integration.jpg'
            )
            post3 = Post(
                title='Willkommen im Blog!',
                content='Dies ist unser erster Blogbeitrag. Bleibt dran für weitere Updates zu unserem Projekt!',
                image_file='default.jpg'
            )
            db.session.add(post1)
            db.session.add(post2)
            db.session.add(post3)
            db.session.commit()
            print("Beispielbeiträge hinzugefügt.")

        # NEU: Erstelle einen Admin-Benutzer, falls noch keiner existiert
        if not User.query.filter_by(is_admin=True).first():
            print("Erstelle Standart-Admin-Benutzer...")
            admin_user = User(email='admin@nautilus.com', is_admin=True)
            admin_user.set_password('AdminPassword123!')
            db.session.add(admin_user)
            db.session.commit()
            print("Standart-Admin-Benutzer hinzugefügt: admin@nautilus.com")

    return app