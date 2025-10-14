import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dein_sehr_geheimer_und_einzigartiger_schluessel_hier'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:testo123!%40%40@Rushraw:3306/dive_glider_db_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}