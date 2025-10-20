import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der .env-Datei in os.environ
# Dies muss am Anfang passieren, damit die Variablen in Config verwendet werden können.
load_dotenv()


class Config:
    # 1. SECRET_KEY: Muss vorhanden sein für Sessions und Sicherheit
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # 2. SQLALCHEMY_DATABASE_URI: Wird direkt aus DATABASE_URL geladen.
    # Wichtig: Wir prüfen, ob die Variable gesetzt ist, sonst brechen wir ab.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Prüfe kritische Variablen beim Start
    if not SECRET_KEY:
        raise EnvironmentError("SECRET_KEY fehlt in der Umgebung (z.B. in der .env-Datei).")

    if not SQLALCHEMY_DATABASE_URI:
        raise EnvironmentError("DATABASE_URL fehlt in der Umgebung. Bitte die Datenbank-URI definieren.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- KORREKTUR DES UPLOAD-PFADES ---

    # 1. Definiere den Basis-Pfad (Projektstammverzeichnis)
    # Gehe vom aktuellen Verzeichnis (__file__) eine Ebene höher, um den 'Abschlussarbeit'-Ordner zu finden.
    # WICHTIG: Wenn Config in app/config.py liegt, ist das dirname(dirname(__file__))
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # 2. Setze den UPLOAD_FOLDER relativ zum Projektstamm ('Abschlussarbeit/')
    # Der korrekte Pfad ist: Abschlussarbeit/app/static/uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')

    # --- ENDE KORREKTUR ---

    # Erlaubte Dateiendungen für den Upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}