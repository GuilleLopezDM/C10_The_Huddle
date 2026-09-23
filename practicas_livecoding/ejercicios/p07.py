"""Práctica 07: Permisos de administrador. Completá solo los tres TODO."""
import time
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from middleware.auth import verify_auth
from practicas_livecoding.base import autenticar, abrir_sesion, leer_jwt
from store import sessions

bp = Blueprint('practica_07', __name__)


def middleware(f):
    """verify_auth ya corre antes. Permitir solo g.user["role"] == "admin"; de lo contrario 403. Nunca usar un rol recibido en el JSON o headers."""
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


@bp.route('/panel', methods=['GET'])
@verify_auth
@middleware
def protegida():
    """Devolver 200 con {"message": 'Panel privado', "email": g.user["email"]}.
    """
    # TODO 3: responder utilizando la identidad autenticada.
    return jsonify({"error": "Ruta pendiente"}), 501
