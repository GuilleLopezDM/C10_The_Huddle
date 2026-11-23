# 🔐 PassPort Inc. — Sistema de Autenticación y Sesiones

[![Tests](https://github.com/GuilleLopezDM/C10_The_Huddle/actions/workflows/tests.yml/badge.svg)](https://github.com/GuilleLopezDM/C10_The_Huddle/actions/workflows/tests.yml)

> Challenge 10 · The Huddle · Python + Flask

API de autenticación para una app ficticia de gestión de identidad digital. Implementa los dos modelos de sesión (**cookies con estado** y **JWT sin estado**) y las defensas habituales contra los ataques web más comunes.

## ✨ Qué incluye

| Área | Implementación |
|---|---|
| Registro / login | Email + contraseña, validación de entrada |
| Hashing | `bcrypt` (10 rondas), nunca se guardan contraseñas en texto plano |
| Sesiones | A elección del usuario: cookie `HttpOnly` persistente (24 h) o JWT (1 h) |
| RBAC | Roles `user` / `admin` con middleware que protege cada ruta |
| CSRF | Token por sesión requerido en peticiones que modifican estado |
| XSS | Sanitización de entradas con `html.escape()` |
| Fuerza bruta | Bloqueo temporal tras 5 intentos fallidos (15 min) |
| Auditoría | Registro de intentos de login fallidos visible para administradores |

## 🛠️ Stack

`Python 3` · `Flask 3` · `bcrypt` · `PyJWT` · almacenamiento en memoria

## 📁 Estructura

```text
app.py              # Punto de entrada y registro de blueprints
config.py           # Expiraciones, rondas de bcrypt, límites de intentos
store.py            # Almacenamiento en memoria (usuarios, sesiones, intentos)
middleware/         # auth, rbac, csrf, rate_limiter
routes/             # auth_routes, user_routes, admin_routes
utils/sanitize.py   # Sanitización contra XSS
templates/          # Frontend HTML mínimo para probar la API
tests/              # Suite de pytest (18 tests)
```

## 🚀 Cómo ejecutarlo

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrí `http://localhost:3000`. Al arrancar se crea un administrador de prueba (`admin@passport.com` / `Admin1234!`).

Variables de entorno opcionales: `JWT_SECRET`, `PORT`, `DEBUG`.

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

18 tests verifican cada defensa: hashing con bcrypt, cookie `HttpOnly` + `SameSite=Strict`, JWT alterado rechazado, RBAC, CSRF obligatorio con cookies, bloqueo tras 5 intentos fallidos y escapado contra XSS. Corren automáticamente con GitHub Actions en cada push.

## 📡 Endpoints

| Método | Ruta | Acceso |
|---|---|---|
| `POST` | `/auth/register` | Público |
| `POST` | `/auth/login` | Público (elige `cookie` o `jwt`) |
| `POST` | `/auth/logout` | Autenticado |
| `GET` | `/auth/status` | Público |
| `GET` | `/auth/csrf-token` | Autenticado |
| `GET` | `/user/profile` | Usuario |
| `GET` | `/admin/dashboard` | Admin |
| `GET` | `/admin/users` | Admin |
| `DELETE` | `/admin/users/<id>` | Admin |
| `GET` | `/admin/failed-logins` | Admin |

## 📝 Enunciado

El enunciado completo del challenge está en [`challenge10.md`](challenge10.md).
