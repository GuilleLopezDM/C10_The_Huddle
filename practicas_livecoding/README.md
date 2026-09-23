# 10 prácticas de livecoding: un middleware + dos rutas

Son simulacros pequeños para repetir el formato de tu evaluación con Flask.
Cada archivo tiene **exactamente tres TODO**: el cuerpo de un middleware,
`POST /login` y una ruta protegida. La infraestructura y las pruebas están listas.
No hace falta crear un frontend, una base de datos ni herramientas de tokens.

## Empezar

Desde la raíz `C10_The_Huddle`, en PowerShell:

```powershell
# 1. Abrí practicas_livecoding/ejercicios/p01.py y completá los tres TODO.
# 2. Probá sin levantar ningún servidor:
.\.venv\Scripts\python.exe -m practicas_livecoding.probar 1

# 3. Opcional: levantar esa práctica para usar Postman:
.\.venv\Scripts\python.exe -m practicas_livecoding.servidor 1
```

Para pasar a otra práctica, cambiá `1` por un número del `2` al `10`.
Para corregir todas: `python -m practicas_livecoding.probar todas` usando el mismo
Python del entorno virtual. Si falta el entorno, crealo con Python y ejecutá
`python -m pip install -r requirements.txt`. No hay dependencias adicionales.

**Al principio las pruebas fallan porque los TODO responden 501. Es intencional.**
Terminaste una práctica cuando el comando termina con `OK`, sin fallos ni errores.
Algunos casos aparecen como `skipped` porque solo aplican a otros ejercicios.
Cada ejecución prepara datos nuevos; no depende de que hayas resuelto las anteriores.

## Los diez simulacros

En todos implementás `POST /login` además de la ruta de esta tabla. Las rutas,
imports y posiciones de los decoradores ya están definidos; completá los cuerpos.

| Nº | Archivo | Tu middleware | Tu ruta protegida | Objetivo extra |
|---|---|---|---|---|
| 1 | [p01.py](ejercicios/p01.py) | CSRF | `POST /confirmar` | Repetir el caso del examen |
| 2 | [p02.py](ejercicios/p02.py) | CSRF | `PATCH /preferencias` | Proteger también PATCH |
| 3 | [p03.py](ejercicios/p03.py) | CSRF | `DELETE /borrador` | Proteger también DELETE |
| 4 | [p04.py](ejercicios/p04.py) | CSRF | `POST /logout` | Invalidar sesión y borrar cookie |
| 5 | [p05.py](ejercicios/p05.py) | Autenticación cookie | `GET /perfil` | Rechazar sesiones desconocidas o vencidas |
| 6 | [p06.py](ejercicios/p06.py) | Autenticación JWT | `GET /perfil` | Validar Bearer, firma y vencimiento |
| 7 | [p07.py](ejercicios/p07.py) | Rol admin | `GET /panel` | Distinguir autenticación de permisos |
| 8 | [p08.py](ejercicios/p08.py) | Propietario | `GET /usuarios/<user_id>` | Comparar el ID de la URL con la identidad |
| 9 | [p09.py](ejercicios/p09.py) | Sesión reciente | `GET /datos-sensibles` | Exigir login de hace como máximo 5 minutos |
| 10 | [p10.py](ejercicios/p10.py) | CSRF según método de autenticación | `POST /confirmar` | Cookie exige CSRF; JWT por Bearer no |

Los primeros tres y el décimo simulan una acción: su respuesta exitosa alcanza;
no tenés que implementar edición o eliminación de datos. El cuarto sí debe
cerrar la sesión. Cada archivo indica el JSON exacto de su respuesta.

## Herramientas que ya tenés

- `autenticar(email, password)`: busca al usuario y compara el hash. Devuelve el
  usuario o `None`. No crea ninguna sesión.
- `abrir_sesion(user, metodo)`: devuelve una respuesta 200 con la cookie
  `sessionId` y `csrfToken`, o con `token` para JWT. No hay que implementar hashes,
  generación de tokens ni flags de cookies.
- `leer_jwt(token)`: verifica firma y vencimiento; devuelve `sub`, `email`, `role`
  y `exp`. Si es inválido o venció, lanza `jwt.InvalidTokenError`.
- `verify_auth`: middleware del proyecto, ya conectado donde hace falta. Deja
  `g.user = {"id": ..., "email": ..., "role": ...}`, `g.auth_method` y, con cookie,
  `g.session_id`. En p05 y p06 vos implementás la autenticación, por eso no está conectado.
- `sessions`: diccionario compartido con `csrf_token`, `user_id`, `email`, `role`,
  `created_at` y `expires_at` por cada ID de sesión. Los tiempos son segundos Unix.
- `request`, `jsonify`, `g`, `wraps`, `time` y `jwt`: ya importados.

El laboratorio usa JWT firmado compatible con `middleware/auth.py`. No usa
`utils/tokens.py`, que en este checkout depende de una `FERNET_KEY` que no figura
en `config.py`. No necesitás arreglar ese archivo para practicar.

## Contrato del login en todas las prácticas

1. Leer el cuerpo con `request.get_json(silent=True)`.
2. Si no es un objeto JSON, o email/password no son strings no vacíos: **400**.
3. Verificar credenciales con `autenticar`. Si no coinciden: **401**.
4. Devolver `abrir_sesion` con el método correspondiente: cookie en p01–p05 y
   p07–p09; JWT en p06. En p10 aceptar `authMethod` (`cookie` por defecto o `jwt`),
   y responder **400** para cualquier otro valor.
5. Todos los errores deben ser JSON `{"error": "texto explicativo"}`. El texto es libre.

Usuarios precargados, ambos con contraseña `Clave123!`:

| Email | ID | Rol |
|---|---|---|
| `alumno@demo.com` | `alumno` | `user` |
| `admin@demo.com` | `admin` | `admin` |

## Probar manualmente la práctica 1

Con el servidor ejecutándose en otra terminal:

```powershell
# Guardar cookie y obtener el CSRF asociado a esa sesión.
$loginPractica = Invoke-RestMethod -Method Post -Uri http://localhost:3001/login `
  -ContentType 'application/json' `
  -Body '{"email":"alumno@demo.com","password":"Clave123!"}' `
  -SessionVariable sesionPractica

# Caso permitido: cookie + CSRF correcto => 200.
Invoke-RestMethod -Method Post -Uri http://localhost:3001/confirmar `
  -WebSession $sesionPractica -Headers @{'X-CSRF-Token'=$loginPractica.csrfToken}

# Falta CSRF => 403 (PowerShell muestra el error HTTP).
Invoke-RestMethod -Method Post -Uri http://localhost:3001/confirmar `
  -WebSession $sesionPractica

# Falta login => 401.
Invoke-RestMethod -Method Post -Uri http://localhost:3001/confirmar
```

En Postman: hacé el login, conservá la cookie que recibe y copiá `csrfToken`
al header `X-CSRF-Token` de la ruta protegida. En p06 usá
`Authorization: Bearer <token>`. En p10 probá ambos métodos por separado.

## Cómo entrenar

Reservá 15–20 minutos por práctica. Primero leé el contrato del archivo, completá
los tres TODO, corré las pruebas y corregí el primer fallo. El número de prueba y
el estado esperado te dicen qué revisar. Después explicá en voz alta el recorrido:
login → credencial → middleware → ruta → respuesta.

Recordatorios para el examen:

- **401**: no hay una autenticación válida. **403**: la verificación de CSRF o
  de permisos rechaza la solicitud después de autenticarla.
- El CSRF se compara contra **la sesión actual**, no contra cualquier token guardado.
- `verify_auth` debe ejecutarse antes del middleware que consulta `g.user` o `g.session_id`.
- Un decorador debe devolver su función interna; esa función debe llamar a
  `f(*args, **kwargs)` cuando permite continuar.
- No alcanza con probar el 200: también hay que demostrar que se rechazan los accesos inválidos.

Los archivos del laboratorio son independientes de `app.py`: solo se carga una
práctica a la vez, en el puerto 3001. Los datos viven en memoria y se reinician al
crear la app o recargar el servidor. Las pruebas usan el cliente de Flask y no requieren red.
