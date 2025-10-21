# ==============================================================================
# tests/conftest.py
# ==============================================================================

import pytest
import os
import shutil
from app import create_app, db
from app.models import User, Post
from config import Config
from werkzeug.security import generate_password_hash


# Erstellt eine Testkonfiguration, die eine In-Memory SQLite-Datenbank verwendet
class TestConfig(Config):
    """Konfiguration für Pytest: Nutzt In-Memory DB und deaktiviert CSRF."""
    TESTING = True
    # Nutze :memory: für eine schnelle In-Memory SQLite-DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # SECRET_KEY muss auch im Test vorhanden sein
    SECRET_KEY = 'test_secret_key'
    # Setze den Upload-Folder in ein temporäres Verzeichnis
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'test_uploads')
    ADMIN_INIT_PASSWORD = 'Sicher123!'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    # CSRF für die Tests deaktivieren
    WTF_CSRF_ENABLED = False


# Fixture für die App-Instanz und den Datenbank-Kontext (SCOPE='module')
@pytest.fixture(scope='module')
def app():
    """Erzeugt die Flask-App mit Test-Konfiguration und setzt die Datenbank auf."""
    app = create_app(TestConfig)

    # Erstellt den temporären Upload-Ordner für den Test
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        # Löscht alte Tabellen und erstellt neue
        db.drop_all()
        db.create_all()

        # Erstellt Admin und Test-User
        if not User.query.filter_by(email='test_admin@blog.de').first():
            admin = User(email='test_admin@blog.de', is_admin=True)
            admin.set_password('Sicher123!')
            db.session.add(admin)
        if not User.query.filter_by(email='normal_user@blog.de').first():
            user = User(email='normal_user@blog.de', is_admin=False)
            user.set_password('Standard456!')
            db.session.add(user)

        db.session.commit()

        # Fügt initialen Post hinzu
        admin_user_id = User.query.filter_by(email='test_admin@blog.de').first().id
        if not Post.query.first():
            initial_post = Post(title='Test Post 1', content='Inhalt des ersten Testbeitrags.',
                                image_file='default.jpg', user_id=admin_user_id)
            db.session.add(initial_post)
            db.session.commit()

    yield app

    # Aufräumarbeiten nach dem Test-Modul
    with app.app_context():
        db.session.remove()
        db.drop_all()
    # Löscht den temporären Upload-Ordner und dessen Inhalt
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])


# Fixture für den Test-Client (SCOPE='function')
@pytest.fixture(scope='function')
def client(app):
    """Erzeugt einen Test-Client für HTTP-Requests."""
    # Pytest findet das 'app' Fixture automatisch in conftest.py
    return app.test_client()