# ==============================================================================
# tests/app_test.py
# ==============================================================================

import pytest
import io
from werkzeug.datastructures import FileStorage
# Die Fixtures 'app' und 'client' werden automatisch von conftest.py geladen.
from app.models import Post, User
from app import db


# ==============================================================================
# 1. UNIT TESTS (BASE)
# ==============================================================================

# Test 1: Testet die Erreichbarkeit der Startseite
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Aktuelle Projekte' in response.data  # Prüft auf Titel im HTML
    assert b'Test Post 1' in response.data  # Prüft auf den initialen Post


# Test 2: Testet die Admin-Zugangskontrolle (Unauthentifizierter Zugriff)
def test_admin_required_redirect(client):
    # Versucht, ohne Login auf das Dashboard zuzugreifen
    response = client.get('/admin/dashboard', follow_redirects=False)
    # Muss zu /login umleiten (302)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login?next=%2Fadmin%2Fdashboard')


# ==============================================================================
# 2. INTEGRATION TESTS (POST & ADMIN)
# ==============================================================================

# Test 3: Testet die Erreichbarkeit des Admin Dashboards nach Login
def test_admin_dashboard_access(client):
    # Simuliert Login
    client.post('/login', data=dict(
        email='test_admin@blog.de',
        password='Sicher123!',
        remember_me='False'
    ), follow_redirects=True)

    # Prüft den Dashboard-Zugriff
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data
    assert b'Test Post 1' in response.data


# Test 4: Erstellung eines neuen Beitrags (Create)
def test_new_post_creation(client, app):
    # Setup: Admin Login
    client.post('/login', data=dict(
        email='test_admin@blog.de',
        password='Sicher123!',
        remember_me='False'
    ), follow_redirects=True)

    # Dummy-Bild für den Upload erstellen (benötigt io und FileStorage)
    data_io = io.BytesIO(b'dummy_image_data')
    image_filestorage = FileStorage(
        data_io, filename='test_upload.jpg', content_type='image/jpeg'
    )

    # Posten des neuen Beitrags mit Bild
    response = client.post('/admin/post/new', data=dict(
        title='Neuer Test Beitrag',
        content='Inhalt des neu erstellten Beitrags.',
        image=image_filestorage,
        submit='Speichern'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Dein Beitrag wurde erfolgreich erstellt!' in response.data

    # Datenbankprüfung
    with app.app_context():
        new_post = Post.query.filter_by(title='Neuer Test Beitrag').first()
        assert new_post is not None


# Test 5: Erfolgreicher Admin-Login (korrekte Umleitung und Meldung)
def test_admin_login_success(client):
    # Fügt den 'next' Parameter hinzu, um die Umleitung zum Dashboard zu forcieren.
    response = client.post('/login?next=/admin/dashboard', data=dict(
        email='test_admin@blog.de',
        password='Sicher123!',
        remember_me='False'
    ), follow_redirects=True)

    # Sucht nach dem UTF-8-kodierten String "zurück"
    assert b'Hallo Admin test_admin@blog.de! Willkommen zur\xc3\xbcck.' in response.data
    assert b'Admin Dashboard' in response.data
    assert response.status_code == 200


# Test 6: Misslungener Login (falsches Passwort)
def test_admin_login_failure(client):
    response = client.post('/login', data=dict(
        email='test_admin@blog.de',
        password='FalschesPasswort',
        remember_me='False'
    ), follow_redirects=True)

    # Sucht nach dem UTF-8-kodierten String "Überprüfe"
    assert b'Login fehlgeschlagen. \xc3\x9cberpr\xc3\xbcfe E-Mail und Passwort.' in response.data
    assert response.status_code == 200
    assert b'Admin Dashboard' not in response.data


# Test 7: Löschen eines Beitrags (Delete)
def test_post_deletion(client, app):
    # Setup: Admin Login
    client.post('/login', data=dict(
        email='test_admin@blog.de',
        password='Sicher123!',
        remember_me='False'
    ), follow_redirects=True)

    # Erstellt einen Post zum Löschen
    with app.app_context():
        admin_user_id = User.query.filter_by(email='test_admin@blog.de').first().id
        post_to_delete = Post(title='Lösch mich', content='Soll gelöscht werden.', user_id=admin_user_id)
        db.session.add(post_to_delete)
        db.session.commit()
        post_id = post_to_delete.id

    # Sendet die POST-Anfrage zum Löschen
    response = client.post(f'/admin/post/{post_id}/delete', follow_redirects=True)

    # Prüft die Erfolgsmeldung
    assert response.status_code == 200
    assert b'Der Beitrag wurde unwiderruflich gel\xc3\xb6scht!' in response.data  # Löscht: \xc3\xb6

    # Datenbankprüfung: Post sollte nicht mehr existieren
    with app.app_context():
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None