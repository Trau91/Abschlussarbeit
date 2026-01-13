from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

class PostForm(FlaskForm):
    # Titel des Beitrags: Muss vorhanden sein und zwischen 2 und 100 Zeichen lang
    title = StringField('Titel',
                        default="Meilenstein: ",
                        validators=[DataRequired(message='Der Titel ist erforderlich.'),
                                    Length(min=2, max=100, message='Titel muss zwischen 2 und 100 Zeichen lang sein.')])

    # Inhalt des Beitrags: Muss vorhanden sein
    content = TextAreaField('Inhalt',
                            default="Status: \nTechnische Details: \nTeam-Notiz: ",
                            validators=[DataRequired(message='Der Inhalt ist erforderlich.')])

    # Optionales Bildfeld:
    # FileAllowed stellt sicher, dass nur die erlaubten Dateitypen hochgeladen werden.
    # Da dies ein Blogbeitrag ist, ist das Bild nicht zwingend erforderlich.
    image = FileField('Beitragsbild (Optional)',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                              'Nur Bilder (JPG, PNG, GIF) sind erlaubt.')])

    # Button zum Absenden des Formulars
    submit = SubmitField('Speichern')