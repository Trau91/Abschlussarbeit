import os
import secrets
from uuid import uuid4
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db  # Stelle sicher, dass db importiert wird
from app.models import Post
from app.blueprints.admin.forms import PostForm  # Angenommen, du hast ein PostForm im Admin-Blueprint
from werkzeug.utils import secure_filename
from PIL import Image  # Wird für die Bildbearbeitung/Optimierung verwendet (muss noch installiert werden)

admin = Blueprint('admin', __name__)


# --- Dekorator zur Überprüfung der Admin-Rolle (Zugangskontrolle) ---
def admin_required(f):
    @login_required  # Schutz: Nur eingeloggte User
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            # Schutz: Nur Admin-User
            flash('Zugriff verweigert. Diese Seite ist nur für Administratoren.', 'danger')
            # Verwende abort(403) für "Forbidden" oder leite zur Startseite um
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__  # Um Namenskollisionen zu vermeiden
    return decorated_function


# --- Hilfsfunktion für sicheren Bild-Upload ---
def save_picture(form_picture):
    # 1. Dateiendung prüfen (wird auch im Formular geprüft, hier doppelt gemoppelt für die Sicherheit)
    if not form_picture.filename.lower().endswith(tuple(current_app.config['ALLOWED_EXTENSIONS'])):
        return None

    # 2. Eindeutigen Dateinamen erstellen (Sicherheit: Schutz vor Pfadmanipulation)
    # Nutzt UUID, wie im Pflichtenheft gefordert
    random_hex = str(uuid4())
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

    # 3. Bild speichern und optional größenoptimieren
    try:
        # Optimierung/Resize auf z.B. 500x500 (Optional, aber empfohlen für Performance)
        output_size = (500, 500)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    except Exception as e:
        # Im Falle eines Fehlers bei der Bildbearbeitung, einfach abspeichern
        form_picture.save(picture_path)

    return picture_fn


# ----------------- CRUD-Funktionalität -----------------

# --- Dashboard (Read: Alle Beiträge im Admin-Bereich) ---
@admin.route('/dashboard')
@admin_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # Eine einfache Liste im Admin-Bereich
    return render_template('admin/dashboard.html', title='Admin Dashboard', posts=posts)


# --- Neuen Beitrag erstellen (Create) ---
@admin.route('/post/new', methods=['GET', 'POST'])
@admin_required
def new_post():
    # NEU: Das Formular musst du noch erstellen (app/blueprints/admin/forms.py)
    form = PostForm()
    if form.validate_on_submit():
        image_file_name = 'default.jpg'
        if form.image.data:
            image_file_name = save_picture(form.image.data)

        post = Post(title=form.title.data,
                    content=form.content.data,
                    image_file=image_file_name
                    )
        # Hinzufügen der User-Beziehung (optional, basierend auf deinem Datenmodell)
        # Wenn Post eine 'user_id' hätte, müsste diese hier gesetzt werden.
        # Da dein Pflichtenheft nur eine 1:N Beziehung erwähnt, aber die Post-Klasse
        # keine user_id hat, lassen wir das hier weg und nehmen an, dass es nur *einen* Admin gibt.

        db.session.add(post)
        db.session.commit()
        flash('Dein Beitrag wurde erfolgreich erstellt!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_post.html', title='Neuer Beitrag', form=form, legend='Neuer Beitrag')


# --- Beitrag aktualisieren (Update) ---
@admin.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@admin_required
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm()

    if form.validate_on_submit():
        if form.image.data:
            # Altes Bild löschen, falls es nicht default.jpg ist
            if post.image_file != 'default.jpg':
                old_picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_file)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            post.image_file = save_picture(form.image.data)

        post.title = form.title.data
        post.content = form.content.data

        db.session.commit()
        flash('Dein Beitrag wurde erfolgreich aktualisiert!', 'success')
        return redirect(url_for('admin.dashboard'))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('admin/create_post.html', title='Beitrag aktualisieren', form=form,
                           legend='Beitrag aktualisieren', post=post)


# --- Beitrag löschen (Delete) ---
@admin.route('/post/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    # Die Delete-Route sollte idealerweise nur POST-Anfragen akzeptieren (Schutz vor CSRF)
    post = db.get_or_404(Post, post_id)

    # Bild-Datei löschen, falls es nicht default.jpg ist
    if post.image_file != 'default.jpg':
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_file)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    db.session.delete(post)
    db.session.commit()
    flash('Der Beitrag wurde unwiderruflich gelöscht!', 'success')
    return redirect(url_for('admin.dashboard'))