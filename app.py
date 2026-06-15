from flask import Flask, jsonify, send_from_directory

import config
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

app = Flask(__name__, static_folder="templates", static_url_path="")

# Registrar blueprints con sus prefijos de URL
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(admin_bp, url_prefix="/admin")


@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no encontrada"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    print("\n PassPort Inc. - Sistema de Autenticacion")
    print(f" Servidor en http://localhost:{config.PORT}")
    print("\n Admin por defecto:")
    print("   Email:     admin@passport.com")
    print("   Password:  Admin1234!")
    print("\n Metodos de auth disponibles: Cookie | JWT\n")
    app.run(port=config.PORT, debug=config.DEBUG)
