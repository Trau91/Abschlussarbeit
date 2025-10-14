from app import create_app, db # NEU db Hinzugefügt
from flask_migrate import Migrate # NEU Hinzugefügt

app = create_app()
migrate = Migrate(app, db) # NEU: Initialisiere Flask-Migrate

if __name__ == '__main__':
    app.run(debug=True)