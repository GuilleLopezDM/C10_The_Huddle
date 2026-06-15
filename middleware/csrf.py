import uuid
from functools import wraps
from flask import request, jsonify, g
from store import sessions

# Req. 8 - Protección CSRF (Cross-Site Request Forgery).
#
# FLUJO:
#   1. Al hacer login con cookie, el servidor genera un csrfToken y lo devuelve en el body JSON.
#   2. El cliente guarda el csrfToken en JavaScript (no en cookie → un atacante cross-site no puede leerlo).
#   3. En cada petición que cambia estado (POST/PUT/DELETE), el cliente incluye el header X-CSRF-Token.
#   4. El servidor verifica que coincida con el almacenado en la sesión.
#
# ¿Por qué JWT no necesita CSRF?
#   El token JWT va en el header "Authorization", que un sitio externo no puede enviar automáticamente.


def generate_csrf_token():
    return str(uuid.uuid4())


def verify_csrf(f):
    """Debe aplicarse DESPUÉS de verify_auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # JWT no necesita CSRF
        if getattr(g, "auth_method", None) != "cookie":
            return f(*args, **kwargs)

        # GET/HEAD/OPTIONS no cambian estado → son seguros
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return f(*args, **kwargs)

        token_from_header = request.headers.get("X-CSRF-Token")
        session = sessions.get(getattr(g, "session_id", None))

        if not session or not token_from_header or session["csrf_token"] != token_from_header:
            return jsonify({"error": "Token CSRF inválido o ausente"}), 403

        return f(*args, **kwargs)
    return decorated
