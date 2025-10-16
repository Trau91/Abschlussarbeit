import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisiere Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Flask-Login user_loader Funktion
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        # Die empfohlene Methode zur Abfrage über die ID
        return db.session.get(User, int(user_id))

    # Stelle sicher, dass der UPLOAD_FOLDER existiert
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Blueprints registrieren
    from app.blueprints.main.routes import main as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.admin.routes import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        # WICHTIG: db.create_all() wurde entfernt, da Flask-Migrate verwendet wird.
        # Nutze 'flask db upgrade', um die Datenbank zu erstellen und zu aktualisieren.

        from app.models import Post, User

        # Beispielbeiträge nur hinzufügen, wenn die Datenbank leer ist
        if not Post.query.first():
            print("Füge Beispielbeiträge hinzu...")
            # NEU: Um Fremdschlüsselprobleme zu vermeiden, weisen wir die Postings
            # dem Admin zu, falls er existiert.
            admin_user = User.query.filter_by(is_admin=True).first()
            user_id_for_posts = admin_user.id if admin_user else None

            post1 = Post(
                title='Erster Prototypen-Update',
                content='Heute haben wir mit dem Bau des Hauptrahmens begonnen. Es läuft gut!',
                image_file='prototype_update.jpg',
                user_id=user_id_for_posts
            )
            post2 = Post(
                title='Elektronik-Integration',
                content='Die ersten Sensoren sind angeschlossen und die Verkabelung ist fast abgeschlossen. Eine Herausforderung war die Wasserdichtigkeit.',
                image_file='electronics_integration.jpg',
                user_id=user_id_for_posts
            )
            post3 = Post(
                title='Willkommen im Blog!',
                content='Dies ist unser erster Blogbeitrag. Bleibt dran für weitere Updates zu unserem Projekt!',
                image_file='default.jpg',
                user_id=user_id_for_posts
            )
            db.session.add_all([post1, post2, post3])
            db.session.commit()
            print("Beispielbeiträge hinzugefügt.")

        # NEU: Erstelle einen Admin-Benutzer, falls noch keiner existiert (Sichere Methode)
        admin_init_password = os.environ.get('ADMIN_INIT_PASSWORD')

        if not User.query.filter_by(is_admin=True).first():
            if admin_init_password:
                print("Erstelle Standart-Admin-Benutzer...")
                admin_user = User(email='admin@nautilus.com', is_admin=True)
                # Das Passwort wird sicher aus der Umgebungsvariable geladen
                admin_user.set_password(admin_init_password)
                db.session.add(admin_user)
                db.session.commit()
                print("Standart-Admin-Benutzer hinzugefügt: admin@nautilus.com")
                print("BITTE ÄNDERE DAS PASSWORT IM NÄCHSTEN SCHRITT!")
            else:
                # Wichtiger Hinweis bei fehlendem Passwort
                print("!!! SICHERHEITS-WARNUNG: ADMIN_INIT_PASSWORD fehlt in .env. Es wurde kein Admin erstellt. !!!")

    return app