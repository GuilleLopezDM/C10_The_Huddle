"""Infraestructura lista. No necesitás editar este archivo."""
import importlib
import time
import uuid

import bcrypt
import jwt
from flask import Flask, jsonify

import config
from store import sessions, users


def autenticar(email, password):
    """Devuelve un usuario o None. Valida tipos y compara el hash con bcrypt."""
    if not isinstance(email, str) or not isinstance(password, str):
        return None
    user = next((u for u in users.values() if u['email'] == email.strip().lower()), None)
    try:
        return user if user and bcrypt.checkpw(password.encode(), user['password']) else None
    except ValueError:
        return None


def abrir_sesion(user, metodo='cookie'):
    """Respuesta HTTP 200 lista con cookie + csrfToken, o token JWT."""
    if metodo == 'jwt':
        token = jwt.encode({
            'sub': user['id'], 'email': user['email'], 'role': user['role'],
            'exp': int(time.time()) + 3600,
        }, config.JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token, 'authMethod': 'jwt'})
    sid, csrf = str(uuid.uuid4()), str(uuid.uuid4())
    sessions[sid] = {
        'user_id': user['id'], 'email': user['email'], 'role': user['role'],
        'csrf_token': csrf, 'created_at': time.time(), 'expires_at': time.time() + 3600,
    }
    response = jsonify({'csrfToken': csrf, 'authMethod': 'cookie'})
    response.set_cookie('sessionId', sid, httponly=True, samesite='Strict')
    return response


def leer_jwt(token):
    """Valida firma/expiración; devuelve claims o lanza jwt.InvalidTokenError."""
    return jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'],
                      options={'require': ['exp', 'sub', 'email', 'role']})


def crear_app(numero):
    """Carga solamente una práctica. Cada instancia reinicia los datos del laboratorio."""
    from practicas_livecoding.catalogo import PRACTICAS
    spec = PRACTICAS[numero]
    sessions.clear()
    users.clear()
    for uid, email, role in [('alumno', 'alumno@demo.com', 'user'),
                             ('admin', 'admin@demo.com', 'admin')]:
        users[uid] = {
            'id': uid, 'email': email, 'role': role,
            'password': bcrypt.hashpw(b'Clave123!', bcrypt.gensalt(4)),
        }
    app = Flask(__name__, static_folder=None)
    module = importlib.import_module(f'practicas_livecoding.ejercicios.p{numero:02d}')
    app.register_blueprint(module.bp)
    app.config['PRACTICA'] = spec
    return app
