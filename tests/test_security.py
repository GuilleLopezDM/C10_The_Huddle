import store
from conftest import ADMIN
from utils.sanitize import sanitize


# ─── RBAC ─────────────────────────────────────────────────────────────────────

def test_usuario_comun_no_accede_al_panel_admin(client, register, jwt_header):
    register()
    resp = client.get("/admin/dashboard", headers=jwt_header())
    assert resp.status_code == 403


def test_admin_accede_al_panel(client, jwt_header):
    resp = client.get("/admin/dashboard", headers=jwt_header(**ADMIN))
    assert resp.status_code == 200
    assert "total_users" in resp.get_json()["stats"]


def test_listado_de_usuarios_no_expone_contrasenas(client, register, jwt_header):
    register()
    users = client.get("/admin/users", headers=jwt_header(**ADMIN)).get_json()["users"]
    assert users and all("password" not in u for u in users)


# ─── CSRF ─────────────────────────────────────────────────────────────────────

def test_logout_con_cookie_exige_token_csrf(client, register, login):
    register()
    csrf = login().get_json()["csrfToken"]

    assert client.post("/auth/logout").status_code == 403
    assert client.post("/auth/logout", headers={"X-CSRF-Token": "falso"}).status_code == 403
    assert client.post("/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.get("/user/profile").status_code == 401


def test_borrar_usuario_con_cookie_exige_csrf(client, register, login):
    register()
    user_id = next(u["id"] for u in store.users.values() if u["email"] == "ana@test.com")
    csrf = login(**ADMIN).get_json()["csrfToken"]

    assert client.delete(f"/admin/users/{user_id}").status_code == 403
    resp = client.delete(f"/admin/users/{user_id}", headers={"X-CSRF-Token": csrf})
    assert resp.status_code == 200


# ─── Fuerza bruta ─────────────────────────────────────────────────────────────

def test_cuenta_se_bloquea_tras_5_intentos_fallidos(register, login):
    register()
    for _ in range(5):
        assert login(password="Incorrecta1").status_code == 401
    # Incluso con la contraseña correcta, la cuenta queda bloqueada
    assert login().status_code == 429


def test_login_exitoso_reinicia_el_contador(register, login):
    register()
    for _ in range(4):
        login(password="Incorrecta1")
    assert login().status_code == 200
    assert login(password="Incorrecta1").status_code == 401
    assert login().status_code == 200


# ─── XSS ──────────────────────────────────────────────────────────────────────

def test_sanitize_escapa_html():
    assert sanitize('<script>alert("x")</script>') == "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
    assert sanitize(123) == 123
