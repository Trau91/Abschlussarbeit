import os
from flask import Blueprint, render_template, current_app, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db  # Stelle sicher, dass db importiert wird
from app.models import Post, User
from app.blueprints.main.forms import LoginForm  # Angenommen, du hast ein LoginForm im Main-Blueprint

main = Blueprint('main', __name__)


# --- Hilfsfunktion für den Admin-Check (für die Übersicht) ---
# Obwohl die Admin-Funktionalität in admin.py ist, ist dieser Check
# nützlich, falls wir den Edit/Delete-Button auf der Hauptseite anzeigen wollen.
def is_admin_check():
    return current_user.is_authenticated and current_user.is_admin


# --- Hauptseite / Übersicht (Read: Alle Beiträge anzeigen) ---
@main.route('/')
@main.route('/home')
def index():
    # Beiträge paginiert anzeigen, z.B. 5 Beiträge pro Seite
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        db.select(Post).order_by(Post.created_at.desc()),
        page=page,
        per_page=5,
        error_out=False
    )
    # is_admin_check wird im Template verwendet, um z.B. das Admin-Dashboard zu verlinken
    return render_template('main/index.html', title='Aktuelle Projekte', posts=posts, is_admin=is_admin_check())


# --- Detailansicht eines einzelnen Beitrags (Read: Einzeln anzeigen) ---
@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template('main/post_detail.html', title=post.title, post=post)


# --- Login-Route (Sicherheit: Authentifizierung) ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    # Verhindere, dass eingeloggte User die Login-Seite sehen
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # NEU: Das Formular musst du noch erstellen (app/blueprints/main/forms.py)
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            # Weiterleitung zur Admin-Seite, falls Login erfolgreich war
            if user.is_admin:
                flash(f'Hallo Admin {user.email}! Willkommen zurück.', 'success')
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                # Optional: Weiterleitung für nicht-Admin User (hier zur Startseite)
                flash('Anmeldung erfolgreich, aber kein Zugriff auf den Admin-Bereich.', 'info')
                return redirect(url_for('main.index'))
        else:
            flash('Login fehlgeschlagen. Überprüfe E-Mail und Passwort.', 'danger')

    return render_template('main/login.html', title='Admin Login', form=form)


# --- Logout-Route ---
@main.route('/logout')
def logout():
    logout_user()
    flash('Du wurdest erfolgreich abgemeldet.', 'success')
    return redirect(url_for('main.index'))