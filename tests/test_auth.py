import bcrypt

import store


# ─── Registro y hashing ───────────────────────────────────────────────────────

def test_registro_exitoso(register):
    assert register().status_code == 201


def test_registro_rechaza_email_duplicado(register):
    register()
    assert register().status_code == 409


def test_registro_valida_email_y_largo_de_contrasena(register):
    assert register(email="no-es-un-email").status_code == 400
    assert register(password="corta").status_code == 400


def test_contrasena_se_guarda_hasheada_con_bcrypt(register):
    register(password="Segura123")
    user = next(u for u in store.users.values() if u["email"] == "ana@test.com")
    assert user["password"] != b"Segura123"
    assert user["password"].startswith(b"$2b$")
    assert bcrypt.checkpw(b"Segura123", user["password"])


# ─── Login con cookie ─────────────────────────────────────────────────────────

def test_login_cookie_crea_cookie_httponly_samesite(register, login):
    register()
    resp = login()
    assert resp.status_code == 200
    assert resp.get_json()["csrfToken"]
    cookie = resp.headers["Set-Cookie"]
    assert "sessionId=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie


def test_cookie_da_acceso_a_ruta_protegida(client, register, login):
    register()
    login()
    resp = client.get("/user/profile")
    assert resp.status_code == 200


def test_ruta_protegida_sin_autenticacion(client):
    assert client.get("/user/profile").status_code == 401


def test_credenciales_invalidas(register, login):
    register()
    assert login(password="Incorrecta1").status_code == 401


# ─── Login con JWT ────────────────────────────────────────────────────────────

def test_jwt_da_acceso_a_ruta_protegida(client, register, jwt_header):
    register()
    resp = client.get("/user/profile", headers=jwt_header())
    assert resp.status_code == 200


def test_jwt_alterado_es_rechazado(client, register, jwt_header):
    register()
    header = jwt_header()
    header["Authorization"] = header["Authorization"][:-2] + "xx"
    assert client.get("/user/profile", headers=header).status_code == 401
