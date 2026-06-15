from functools import wraps
from flask import jsonify, g

# Req. 5 - Control de Acceso Basado en Roles (RBAC).
# Debe aplicarse DESPUÉS de verify_auth para que g.user esté disponible.


def require_role(role):
    """Decorador de fábrica: require_role('admin') o require_role('user')"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, "user") or g.user["role"] != role:
                return jsonify({"error": "Acceso denegado: permisos insuficientes"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
