"""Práctica 10: CSRF con cookie y JWT por Bearer. Completá solo los tres TODO."""
import time
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from middleware.auth import verify_auth
from practicas_livecoding.base import autenticar, abrir_sesion, leer_jwt
from store import sessions

bp = Blueprint('practica_10', __name__)


def middleware(f):
    """verify_auth ya corre antes. Si g.auth_method == "jwt", permitir sin CSRF (JWT enviado explícitamente por Authorization). Con cookie, aplicar el contrato CSRF de p01. No basta con que exista el header Authorization: verify_auth tiene que haberlo validado."""
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
    Método de esta práctica: data.get('authMethod', 'cookie') (aceptar solo cookie o jwt; si no, 400).
    No devolver contraseñas ni hashes. Los errores usan {"error": "texto"}.
    """
    # TODO 2: validar entrada y credenciales, y abrir la sesión.
    return jsonify({"error": "Login pendiente"}), 501


@bp.route('/confirmar', methods=['POST'])
@verify_auth
@middleware
def protegida():
    """Devolver 200 con {"message": 'Acción confirmada', "email": g.user["email"]}.
    Simulación: no hay que persistir datos; alcanza con responder el JSON.
    """
    # TODO 3: responder utilizando la identidad autenticada.
    return jsonify({"error": "Ruta pendiente"}), 501
