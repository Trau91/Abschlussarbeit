from app import db # Importiere das db-Objekt aus dem __init__.py der App
from datetime import datetime, timezone
from flask_login import UserMixin # Neu Hinzugefügt
from werkzeug.security import generate_password_hash, check_password_hash # neu Hinzugefügt

# Unser Datenbankmodell für Blog-Beiträge
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120), nullable=True, default='default.jpg')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Post {self.id}: {self.title}>'

# Neues Datenbankmodell für Benutzer
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # WICHTIGE KORREKTUR: Länge von 128 auf 256 erhöht, um Scrypt-Hashes zu speichern
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

    # Methoden zum Hashen und Überprüfen von Passwörtern
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


