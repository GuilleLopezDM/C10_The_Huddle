import time
from functools import wraps
import jwt
from flask import request, jsonify, g
import config
from store import sessions

# Req. 3 y 4 - Decorador que verifica autenticación.
# Soporta dos métodos:
#   1. JWT: el cliente envía "Authorization: Bearer <token>"
#   2. Cookie: el navegador envía automáticamente la cookie HttpOnly 'sessionId'


def verify_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # --- Método 1: JWT ---
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                decoded = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
                g.user = {"id": decoded["sub"], "email": decoded["email"], "role": decoded["role"]}
                g.auth_method = "jwt"
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token JWT expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token JWT inválido"}), 401

        # --- Método 2: Sesión con Cookie ---
        session_id = request.cookies.get("sessionId")
        if session_id:
            session = sessions.get(session_id)

            if not session:
                response = jsonify({"error": "Sesión no encontrada"})
                response.delete_cookie("sessionId")
                return response, 401

            if session["expires_at"] < time.time():
                del sessions[session_id]
                response = jsonify({"error": "Sesión expirada"})
                response.delete_cookie("sessionId")
                return response, 401

            g.user = {"id": session["user_id"], "email": session["email"], "role": session["role"]}
            g.auth_method = "cookie"
            g.session_id = session_id
            return f(*args, **kwargs)

        return jsonify({"error": "Autenticación requerida"}), 401

    return decorated
