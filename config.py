import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dein_sehr_geheimer_und_einzigartiger_schluessel_hier'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:Nautilus@localhost:3306/flask_project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}