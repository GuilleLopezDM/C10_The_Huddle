from flask import Blueprint, g, jsonify

from middleware.auth import verify_auth
from store import users

user_bp = Blueprint("user", __name__)


# ─── GET /user/profile ────────────────────────────────────────────────────────
# Req. 1 y 5: ruta protegida, accesible para cualquier usuario autenticado (role: user o admin)
@user_bp.route("/profile", methods=["GET"])
@verify_auth
def profile():
    user = users.get(g.user["id"])
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"],
        "auth_method_used": g.auth_method,
    })
