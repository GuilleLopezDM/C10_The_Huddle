# Guía de Estudio — Challenge 10: Maestro de la Autenticación Segura

> Para Guille. Todo lo que necesitás para entender este proyecto de punta a punta:
> los conceptos del PDF explicados de cero, dónde está cada requisito en el código,
> cómo corre el flujo, y qué se revisó/arregló. Los requisitos **opcionales (bonus)**
> — interfaz con CSS, tests automatizados y recuperación de contraseña por email —
> quedan **fuera de alcance** a propósito.

---

## 1. El challenge en una frase

Sos el responsable de seguridad de **PassPort Inc.**, una startup que guarda
documentos de identidad de la gente. Tu tarea: construir el **sistema de login y
sesiones** para que nadie robe cuentas ni datos. Es Flask puro, con una "base de
datos" en memoria (diccionarios), para que la atención esté 100% en la seguridad
y no en la infraestructura.

---

## 2. Los conceptos del PDF, explicados de cero

### 2.1 Sesiones vs. Tokens (los dos modelos de "mantenerte logueado")

Después de que ingresás usuario y contraseña una vez, ¿cómo hace el servidor para
recordarte en la siguiente petición? HTTP es "sin memoria": cada request es un
desconocido. Hay dos formas de resolverlo:

- **Sesión (con estado / stateful):** el servidor guarda tus datos en SU memoria y
  te da un ticket con un número (el `sessionId`). Vos mostrás el ticket en cada
  request; el servidor busca ese número en su lista y sabe quién sos.
  *Analogía:* el guardarropa de un boliche. Te dan un número; tu abrigo queda del
  lado de ellos.
- **Token (sin estado / stateless):** el servidor NO guarda nada. Te da un
  documento sellado (el JWT) que ya contiene quién sos, firmado para que no lo
  puedas falsificar. Vos lo mostrás en cada request y el servidor lo valida al vuelo.
  *Analogía:* tu DNI. Lo llevás vos; el que lo revisa no necesita llamar a ningún lado.

| | Sesión (cookie) | Token (JWT) |
|---|---|---|
| ¿Dónde vive el estado? | En el servidor | En el cliente |
| Escala a muchos servidores | Cuesta (hay que compartir el estado) | Fácil (cada servidor valida solo) |
| ¿Se puede revocar al toque? | Sí (borrás la sesión) | No fácil (vale hasta que vence) |
| ¿Necesita protección CSRF? | Sí | No |

Este challenge implementa **las dos** y te deja elegir en el login.

### 2.2 Cookies

Una **cookie** es un pedacito de dato que el servidor le pide al navegador que
guarde y reenvíe automáticamente en cada request al mismo sitio. Es el mecanismo
natural para las sesiones: guardamos el `sessionId` en una cookie y el navegador
lo manda solo. Lo importante son sus **flags de seguridad** (ver Req. 10):
`HttpOnly`, `Secure`, `SameSite`.

### 2.3 JWT (JSON Web Token) — y por qué **firmar ≠ cifrar**

Un JWT tiene tres partes separadas por puntos: `header.payload.signature`.

- El **payload** lleva los datos (quién sos, cuándo vence).
- La **signature** (firma) es un sello criptográfico hecho con una llave secreta.

> ⚠️ **El malentendido más común:** un JWT firmado **NO está cifrado**. El payload
> es solo **Base64**, que NO es encriptación: es codificación reversible por
> cualquiera. Si copiás un JWT normal en jwt.io, ves el email y el rol en texto claro.
>
> - **Firmar** = *integridad*. Garantiza que nadie **modificó** el contenido. Pero
>   cualquiera lo puede **leer**.
> - **Cifrar** = *confidencialidad*. Garantiza que nadie **lee** el contenido sin la llave.

El Req. 6 pide explícitamente **cifrar datos sensibles en los tokens**. Por eso en
este proyecto hacemos **las dos capas**: ciframos los datos del usuario con
**Fernet** (AES-128 + HMAC) y además firmamos el token con HS256. Ver `utils/tokens.py`.

### 2.4 Hashing vs. Cifrado (¡tampoco son lo mismo!)

- **Hashing** es de **una sola vía**: convertís la contraseña en un código y **no
  hay vuelta atrás**. Se usa para contraseñas: guardás el hash, nunca la contraseña.
  Al hacer login, hasheás lo que te mandan y comparás hashes.
- **Cifrado** es de **doble vía**: ciframos con una llave y **desciframos** con esa
  misma llave. Se usa cuando necesitás recuperar el dato original (como el payload
  del JWT, que hay que poder leer para saber quién sos).

Usamos **bcrypt** para las contraseñas. bcrypt suma un **salt** (sal) aleatorio, así
dos personas con la misma contraseña tienen hashes distintos, y es **lento a propósito**
(dificulta la fuerza bruta).

### 2.5 XSS (Cross-Site Scripting)

Un atacante logra que **su** JavaScript se ejecute en el navegador de **otra**
persona (por ejemplo, registrándose con un email que contiene `<script>...`). Si
después mostramos ese dato sin cuidado, el script corre en la víctima.
**Defensa:** *escapar* la entrada (convertir `< > & " '` en su versión inofensiva).
Ver `utils/sanitize.py` + la flag `HttpOnly` de la cookie.

### 2.6 CSRF (Cross-Site Request Forgery)

Un sitio malicioso hace que **tu** navegador dispare una petición a un sitio donde
estás logueado, aprovechando que el navegador manda tus cookies solo. **Defensa:**
un **token CSRF** único por sesión, que el sitio atacante no puede leer, y que
exigimos en toda petición que cambie estado. Ver `middleware/csrf.py`.

### 2.7 RBAC (Control de Acceso Basado en Roles)

No todos pueden todo. Hay dos roles: **user** y **admin**. El admin puede borrar
usuarios y ver los intentos fallidos; el user no. Se implementa con el decorador
`require_role(...)`. Ver `middleware/rbac.py`.

### 2.8 Fuerza bruta

Un atacante prueba miles de contraseñas hasta acertar. **Defensa:** limitar los
intentos — tras 5 fallos, bloqueamos la cuenta 15 minutos. Ver `middleware/rate_limiter.py`.

### 2.9 Cabeceras HTTP de seguridad

- `Authorization: Bearer <token>` — así viaja el JWT.
- `Set-Cookie` con `HttpOnly; Secure; SameSite=Strict` — así endurecemos la cookie.
- `X-CSRF-Token` — así el cliente reenvía el token anti-CSRF.

---

## 3. Mapa: requisito obligatorio → dónde está en el código

| # | Requisito | Archivo(s) principal(es) |
|---|-----------|--------------------------|
| 1 | Registro + login con email/password | `routes/auth_routes.py` → `register`, `login` |
| 2 | Contraseñas con hashing (bcrypt) | `routes/auth_routes.py:register`, `store.py` (admin) |
| 3 | Sesiones con cookie (crear/mantener/eliminar) | `login` (crea), `middleware/auth.py` (mantiene), `logout` (elimina) |
| 4 | Autenticación con JWT | `utils/tokens.py`, `login` (crea), `middleware/auth.py` (valida) |
| 5 | RBAC (user / admin) | `middleware/rbac.py`, `routes/admin_routes.py` |
| 6 | **Cifrado** de datos sensibles en tokens + hash de passwords | `utils/tokens.py` (Fernet), `config.py` (FERNET_KEY), bcrypt |
| 7 | Filtrar/escapar entradas (anti-XSS) | `utils/sanitize.py`, aplicado en `register`/`login` |
| 8 | Tokens CSRF | `middleware/csrf.py`, usado en `logout` y `delete_user` |
| 9 | Limitar intentos de login | `middleware/rate_limiter.py`, chequeado en `login` |
| 10 | Cookies con `HttpOnly` y `Secure` | `routes/auth_routes.py:login` → `set_cookie(...)` |

---

## 4. El flujo, paso a paso

### Registro
1. `POST /auth/register` con `{email, password}`.
2. Se **sanitiza** y normaliza el email (anti-XSS), se validan formato y longitud
   (mínimo 8, máximo 72 bytes por el límite de bcrypt).
3. Se **hashea** la contraseña con bcrypt (+ salt) y se guarda el usuario con rol `user`.

### Login — camino Cookie (stateful)
1. `POST /auth/login` con `authMethod: "cookie"`.
2. Se chequea el **lockout** (¿está bloqueada la cuenta?).
3. Se verifica la contraseña con `bcrypt.checkpw`.
4. Se crea una **sesión** en el servidor y un **csrfToken**.
5. Se manda el `sessionId` en una cookie `HttpOnly; SameSite=Strict` y el `csrfToken`
   en el body. El navegador reenviará la cookie sola en cada request.

### Login — camino JWT (stateless)
1. `POST /auth/login` con `authMethod: "jwt"`.
2. Igual chequeo de lockout + verificación de contraseña.
3. Se arma el token: se **cifran** los datos del usuario (Fernet) y se **firma** todo
   (HS256). Se devuelve en el body. El cliente lo guarda y lo manda en `Authorization`.

### Request autenticado
- El decorador `verify_auth` mira si viene `Authorization: Bearer` (JWT) o la cookie
  (sesión), identifica al usuario y deja sus datos en `g.user`.
- Si la ruta exige rol, `require_role` lo chequea. Si cambia estado y es sesión-cookie,
  `verify_csrf` exige el `X-CSRF-Token`.

### Logout
- Cookie: se **borra la sesión** del servidor y se **elimina la cookie** del navegador.
- JWT: el cliente simplemente **tira el token** (no hay estado que borrar).

---

## 5. Revisión del código: qué se encontró y qué se hizo

> Dos revisores independientes (caza de bugs + fit con requisitos) recorrieron el
> código. **Buena noticia:** los 10 requisitos ya estaban implementados y andando.
> Lo que sigue son endurecimientos. Cada uno fue **verificado corriendo la app**.

| ID | Qué era | Severidad | Qué se hizo |
|----|---------|-----------|-------------|
| **R6** | El JWT se **firmaba** pero NO se **cifraba**; el payload (email, rol) era legible en Base64, y los comentarios afirmaban falsamente "cifrado". Era el único **gap real de un requisito obligatorio**. | Alta | Se cifran los datos sensibles con **Fernet** en `utils/tokens.py` (nuevo) + `config.py`. El token queda cifrado **y** firmado. Verificado: el email ya no aparece al decodificar el payload. |
| **B1** | Enumeración de usuarios por **timing**: si el email no existía, se saltaba `bcrypt.checkpw` y la respuesta era instantánea, revelando qué emails están registrados. | Baja | En `login` se corre siempre un `bcrypt.checkpw` contra un **hash señuelo** (`_DUMMY_HASH`), así ambos caminos tardan lo mismo. |
| **B2** | Sesiones y bloqueos **vencidos nunca se barrían**: quedaban en memoria y el dashboard los contaba como "activos". | Baja | Nueva función `purge_expired()` en `store.py`; el dashboard la llama y cuenta solo sesiones vigentes. Además, ventana deslizante en el lockout. |
| **B3** | La comparación del token CSRF usaba `!=`, vulnerable a **timing attack**. | Baja | Se usa `hmac.compare_digest` (tiempo constante) en `middleware/csrf.py`. |
| **B4** | bcrypt **trunca la contraseña a 72 bytes** en silencio: dos contraseñas largas con los mismos 72 primeros bytes entraban igual. | Baja | En `register` se rechazan contraseñas de más de 72 bytes con un 400 claro. |
| **B5** | Un admin **borrado** seguía entrando con su **JWT** viejo hasta 1 hora (el token es stateless y no se revoca). El código sí revocaba las sesiones-cookie, pero no el JWT. | Alta (tradeoff) | En `verify_auth`, rama JWT, se **re-verifica contra la base**: si el usuario ya no existe → 401; el rol se toma de la base (no del token). Tradeoff: se sacrifica algo de "pureza stateless" a cambio de poder revocar. |
| **B6** | El lockout **por email** permite un **DoS**: un atacante manda 5 fallos contra `admin@passport.com` y lo bloquea 15 min. | Media (tradeoff) | **Documentado, no corregido**: el fix real requiere contar también por **IP** o pedir **CAPTCHA**, lo cual excede el alcance del challenge. Queda anotado en `middleware/rate_limiter.py`. |

---

## 6. Cómo correr y probar

### Correr
```bash
pip install -r requirements.txt
python app.py
# Abrí http://localhost:3000  (admin@passport.com / Admin1234!)
```

### Probar por consola (curl)
```bash
BASE=http://localhost:3000

# Registro
curl -X POST $BASE/auth/register -H "Content-Type: application/json" \
  -d '{"email":"guille@test.com","password":"Passw0rd!"}'

# Login con COOKIE (guarda la cookie en cookies.txt y te devuelve el csrfToken)
curl -c cookies.txt -X POST $BASE/auth/login -H "Content-Type: application/json" \
  -d '{"email":"admin@passport.com","password":"Admin1234!","authMethod":"cookie"}'

# Ruta protegida con la cookie
curl -b cookies.txt $BASE/user/profile

# Logout (necesita el X-CSRF-Token que te dio el login)
curl -b cookies.txt -X POST $BASE/auth/logout -H "X-CSRF-Token: <PEGA_EL_CSRF>"

# Login con JWT
curl -X POST $BASE/auth/login -H "Content-Type: application/json" \
  -d '{"email":"admin@passport.com","password":"Admin1234!","authMethod":"jwt"}'

# Ruta protegida con el token
curl $BASE/user/profile -H "Authorization: Bearer <PEGA_EL_TOKEN>"
```

**Comprobación clave del Req. 6** (que el email va cifrado): pegá el JWT en
[jwt.io](https://jwt.io) o decodificá el payload; deberías ver solo un claim `data`
con un chorizo ilegible, **no** tu email.

---

## 7. Glosario rápido

- **Hash:** huella digital irreversible de un dato (contraseñas).
- **Salt:** dato aleatorio que se suma antes de hashear, para que hashes iguales no se repitan.
- **Cifrado:** transformación reversible con llave (para poder recuperar el dato).
- **JWT:** token firmado (y acá, además, cifrado) que lleva tu identidad.
- **Firma (HS256):** sello que garantiza que el token no fue modificado.
- **Fernet:** esquema de cifrado simétrico (AES-128 + HMAC) de la librería `cryptography`.
- **CSRF token:** valor secreto por sesión que frena peticiones forjadas cross-site.
- **Decorador:** función que "envuelve" a otra para agregarle comportamiento (acá: auth, rol, CSRF).
- **Stateless / stateful:** sin estado en el servidor (JWT) / con estado en el servidor (sesión).
- **Lockout:** bloqueo temporal de una cuenta tras demasiados fallos.

---

> **Nota sobre los bonus:** interfaz con UX/CSS, pruebas automatizadas y recuperación
> de contraseña por email eran **opcionales** y quedaron fuera de alcance, tal como
> se acordó. Todo lo obligatorio está implementado, endurecido y verificado.
