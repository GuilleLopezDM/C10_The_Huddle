import time

from flask import Blueprint, g, jsonify

from middleware.auth import verify_auth
from middleware.csrf import verify_csrf
from middleware.rbac import require_role
from store import failed_attempts, sessions, users

admin_bp = Blueprint("admin", __name__)


# ─── GET /admin/dashboard ─────────────────────────────────────────────────────
# Req. 5: solo accesible con role=admin
@admin_bp.route("/dashboard", methods=["GET"])
@verify_auth
@require_role("admin")
def dashboard():
    now = time.time()
    locked = sum(
        1 for a in failed_attempts.values()
        if a.get("locked_until") and a["locked_until"] > now
    )
    return jsonify({
        "message": "Panel de Administración",
        "stats": {
            "total_users": len(users),
            "active_sessions": len(sessions),
            "locked_accounts": locked,
        },
    })


# ─── GET /admin/users ─────────────────────────────────────────────────────────
# Req. 5: lista todos los usuarios (sin exponer passwords)
@admin_bp.route("/users", methods=["GET"])
@verify_auth
@require_role("admin")
def list_users():
    user_list = [
        {"id": u["id"], "email": u["email"], "role": u["role"], "created_at": u["created_at"]}
        for u in users.values()
    ]
    return jsonify({"users": user_list})


# ─── DELETE /admin/users/<user_id> ────────────────────────────────────────────
# Req. 5: solo admin puede eliminar usuarios
# Req. 8: requiere CSRF token válido
@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@verify_auth
@require_role("admin")
@verify_csrf
def delete_user(user_id):
    if user_id == g.user["id"]:
        return jsonify({"error": "No podés eliminar tu propia cuenta"}), 400

    if user_id not in users:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Cerrar todas las sesiones activas del usuario eliminado
    to_remove = [sid for sid, s in sessions.items() if s["user_id"] == user_id]
    for sid in to_remove:
        del sessions[sid]

    del users[user_id]
    return jsonify({"message": "Usuario eliminado exitosamente"})


# ─── GET /admin/failed-logins ─────────────────────────────────────────────────
# Req. 5: solo admin puede ver los intentos fallidos de login
@admin_bp.route("/failed-logins", methods=["GET"])
@verify_auth
@require_role("admin")
def failed_logins():
    now = time.time()
    result = [
        {
            "email": email,
            "count": data["count"],
            "last_attempt": data["last_attempt"],
            "locked_until": data["locked_until"],
            "is_locked": bool(data.get("locked_until") and data["locked_until"] > now),
        }
        for email, data in failed_attempts.items()
    ]
    return jsonify({"failed_logins": result})
