"""Práctica 04: CSRF: cerrar sesión. Completá solo los tres TODO."""
import time
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from middleware.auth import verify_auth
from practicas_livecoding.base import autenticar, abrir_sesion, leer_jwt
from store import sessions

bp = Blueprint('practica_04', __name__)


def middleware(f):
    """Mismo contrato CSRF de p01. La ruta además elimina sessions[g.session_id] y borra la cookie sessionId en la respuesta exitosa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # TODO 1: implementar la verificación y continuar o rechazar.
        return jsonify({"error": "Middleware pendiente"}), 501
    return decorated


@bp.route('/login', methods=['POST'])
def login():
    """Leer JSON con request.get_json(silent=True).
    Si no es un objeto o email/password no son strings no vacíos: 400.
    Llamar autenticar(email, password); si devuelve None: 401.
    Si es correcto, devolver abrir_sesion(user, metodo).
    Método de esta práctica: 'cookie'.
    No devolver contraseñas ni hashes. Los errores usan {"error": "texto"}.
    """
    # TODO 2: validar entrada y credenciales, y abrir la sesión.
    return jsonify({"error": "Login pendiente"}), 501


@bp.route('/logout', methods=['POST'])
@verify_auth
@middleware
def protegida():
    """Devolver 200 con {"message": 'Sesión cerrada', "email": g.user["email"]}.
    Además: eliminar la sesión del servidor y borrar la cookie sessionId.
    """
    # TODO 3: responder utilizando la identidad autenticada.
    return jsonify({"error": "Ruta pendiente"}), 501
