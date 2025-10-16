from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    # E-Mail-Feld: Muss vorhanden sein und ein gültiges E-Mail-Format haben
    email = StringField('E-Mail',
                        validators=[DataRequired(message='Bitte gib deine E-Mail-Adresse ein.'),
                                    Email(message='Ungültiges E-Mail-Format.'),
                                    Length(max=120)]) # Sollte zur DB-Spaltenlänge passen

    # Passwort-Feld: Muss vorhanden sein
    password = PasswordField('Passwort',
                             validators=[DataRequired(message='Bitte gib dein Passwort ein.')])

    # Checkbox für "Angemeldet bleiben"
    remember_me = BooleanField('Angemeldet bleiben')

    # Button zum Absenden des Formulars
    submit = SubmitField('Login')