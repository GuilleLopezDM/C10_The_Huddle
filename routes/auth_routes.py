import re
import time
import uuid
from datetime import datetime

import bcrypt
import jwt
from flask import Blueprint, g, jsonify, make_response, request

import config
from middleware.auth import verify_auth
from middleware.csrf import generate_csrf_token, verify_csrf
from middleware.rate_limiter import check_rate_limit, clear_attempts, record_failed_attempt
from store import sessions, users
from utils.sanitize import sanitize

auth_bp = Blueprint("auth", __name__)


# ─── POST /auth/register ─────────────────────────────────────────────────────
# Req. 1 - Registro con email y contraseña
# Req. 2 - Contraseña almacenada con bcrypt (hashing seguro)
# Req. 7 - Sanitización de email para prevenir XSS
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = sanitize(data.get("email", "")).lower().strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Formato de email inválido"}), 400

    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    if any(u["email"] == email for u in users.values()):
        return jsonify({"error": "El email ya está registrado"}), 409

    user_id = str(uuid.uuid4())
    # Req. 2 y 6: bcrypt convierte la contraseña en un hash irreversible.
    # Nadie puede recuperar la contraseña original, ni el propio administrador.
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(config.BCRYPT_ROUNDS))

    users[user_id] = {
        "id": user_id,
        "email": email,
        "password": hashed,
        "role": "user",
        "created_at": datetime.now().isoformat(),
    }

    return jsonify({"message": "Usuario registrado exitosamente"}), 201


# ─── POST /auth/login ─────────────────────────────────────────────────────────
# Req. 3 - Sesión persistente con cookie
# Req. 4 - Sesión sin estado con JWT
# Req. 9 - Verificación de intentos fallidos antes de procesar
# Req. 10 - Cookie con flags HttpOnly y SameSite=Strict
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = sanitize(data.get("email", "")).lower().strip()
    password = data.get("password", "")
    auth_method = data.get("authMethod", "cookie")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Req. 9: verificar bloqueo por fuerza bruta
    rate_check = check_rate_limit(email)
    if rate_check["locked"]:
        mins = int((rate_check["locked_until"] - time.time()) / 60) + 1
        return jsonify({"error": f"Cuenta bloqueada. Intentá de nuevo en {mins} minuto(s)"}), 429

    user = next((u for u in users.values() if u["email"] == email), None)

    # bcrypt.checkpw compara la contraseña con el hash almacenado
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        record_failed_attempt(email)
        return jsonify({"error": "Credenciales inválidas"}), 401

    clear_attempts(email)

    # ── Req. 4: JWT (sesión sin estado) ──────────────────────────────────────
    if auth_method == "jwt":
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "exp": int(time.time()) + config.JWT_EXPIRES_IN,
        }
        # Req. 6: el JWT está firmado con HS256 usando el JWT_SECRET.
        # Cualquier modificación del payload invalida la firma.
        token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
        return jsonify({"message": "Login exitoso", "token": token, "role": user["role"], "authMethod": "jwt"})

    # ── Req. 3 y 10: Cookie session (sesión persistente) ─────────────────────
    session_id = str(uuid.uuid4())
    csrf_token = generate_csrf_token()  # Req. 8

    sessions[session_id] = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "csrf_token": csrf_token,
        "created_at": time.time(),
        "expires_at": time.time() + config.SESSION_EXPIRES_IN,
    }

    response = make_response(jsonify({
        "message": "Login exitoso",
        "role": user["role"],
        "authMethod": "cookie",
        "csrfToken": csrf_token,  # Req. 8: el cliente debe enviarlo en X-CSRF-Token
    }))
    # Req. 10: HttpOnly impide que JavaScript lea la cookie (protege contra XSS).
    # SameSite=Strict bloquea envíos cross-site (protege contra CSRF).
    # secure=True en producción solo permite la cookie en HTTPS.
    response.set_cookie(
        "sessionId",
        session_id,
        httponly=True,
        secure=config.DEBUG is False,  # True en producción
        samesite="Strict",
        max_age=config.SESSION_EXPIRES_IN,
    )
    return response


# ─── POST /auth/logout ────────────────────────────────────────────────────────
# Req. 3 - Eliminación de sesión del servidor + borrado de cookie
@auth_bp.route("/logout", methods=["POST"])
@verify_auth
@verify_csrf
def logout():
    session_id = getattr(g, "session_id", None)
    if session_id and session_id in sessions:
        del sessions[session_id]

    response = make_response(jsonify({"message": "Sesión cerrada exitosamente"}))
    response.delete_cookie("sessionId")
    return response


# ─── GET /auth/status ─────────────────────────────────────────────────────────
@auth_bp.route("/status", methods=["GET"])
def status():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            decoded = jwt.decode(auth_header[7:], config.JWT_SECRET, algorithms=["HS256"])
            return jsonify({"authenticated": True, "email": decoded["email"], "role": decoded["role"], "authMethod": "jwt"})
        except Exception:
            return jsonify({"authenticated": False})

    session_id = request.cookies.get("sessionId")
    if session_id:
        session = sessions.get(session_id)
        if session and session["expires_at"] > time.time():
            return jsonify({"authenticated": True, "email": session["email"], "role": session["role"], "authMethod": "cookie"})

    return jsonify({"authenticated": False})


# ─── GET /auth/csrf-token ─────────────────────────────────────────────────────
# Permite recuperar el CSRF token tras un refresh de página (la cookie persiste, el token JS no)
@auth_bp.route("/csrf-token", methods=["GET"])
@verify_auth
def get_csrf_token():
    if g.auth_method != "cookie":
        return jsonify({"csrfToken": None})
    session = sessions.get(g.session_id)
    return jsonify({"csrfToken": session["csrf_token"] if session else None})
