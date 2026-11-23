# 🔐 PassPort Inc. — Authentication & Session System

[![Tests](https://github.com/GuilleLopezDM/C10_The_Huddle/actions/workflows/tests.yml/badge.svg)](https://github.com/GuilleLopezDM/C10_The_Huddle/actions/workflows/tests.yml)

🇪🇸 [Versión en español](README.md)

> Challenge 10 · The Huddle · Python + Flask

Authentication API for a fictional digital identity app. It implements both session models (**stateful cookies** and **stateless JWT**) along with the standard defenses against the most common web attacks.

## ✨ Features

| Area | Implementation |
|---|---|
| Sign up / login | Email + password with input validation |
| Hashing | `bcrypt` (10 rounds); passwords are never stored in plain text |
| Sessions | User's choice: persistent `HttpOnly` cookie (24 h) or JWT (1 h) |
| RBAC | `user` / `admin` roles enforced by middleware on every route |
| CSRF | Per-session token required on state-changing requests |
| XSS | Input sanitization with `html.escape()` |
| Brute force | Temporary lockout after 5 failed attempts (15 min) |
| Auditing | Failed login attempts visible to administrators |

## 🛠️ Stack

`Python 3` · `Flask 3` · `bcrypt` · `PyJWT` · `pytest` · in-memory storage

## 📁 Structure

```text
app.py              # Entry point and blueprint registration
config.py           # Expirations, bcrypt rounds, attempt limits
store.py            # In-memory storage (users, sessions, attempts)
middleware/         # auth, rbac, csrf, rate_limiter
routes/             # auth_routes, user_routes, admin_routes
utils/sanitize.py   # XSS sanitization
templates/          # Minimal HTML frontend to try the API
tests/              # pytest suite (18 tests)
```

## 🚀 Running it

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:3000`. A demo administrator is created on startup (`admin@passport.com` / `Admin1234!`).

Optional environment variables: `JWT_SECRET`, `PORT`, `DEBUG`.

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

18 tests cover each defense: bcrypt hashing, `HttpOnly` + `SameSite=Strict` cookie, tampered JWT rejection, RBAC, mandatory CSRF token with cookies, lockout after 5 failed attempts and XSS escaping. GitHub Actions runs them on every push.

## 📡 Endpoints

| Method | Route | Access |
|---|---|---|
| `POST` | `/auth/register` | Public |
| `POST` | `/auth/login` | Public (choose `cookie` or `jwt`) |
| `POST` | `/auth/logout` | Authenticated |
| `GET` | `/auth/status` | Public |
| `GET` | `/auth/csrf-token` | Authenticated |
| `GET` | `/user/profile` | User |
| `GET` | `/admin/dashboard` | Admin |
| `GET` | `/admin/users` | Admin |
| `DELETE` | `/admin/users/<id>` | Admin |
| `GET` | `/admin/failed-logins` | Admin |

## 📝 Challenge statement

The full challenge statement (in Spanish) is in [`challenge10.md`](challenge10.md).
