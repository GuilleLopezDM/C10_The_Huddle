"""
¿Qué hace este archivo y por qué existe?
========================================
Acá vive TODA la lógica del JWT en un solo lugar: cómo se arma un token cuando
el usuario hace login, y cómo se lee/valida cuando el usuario nos manda ese token
de vuelta. Antes esta lógica estaba desparramada entre auth_routes.py, auth.py y
el endpoint /auth/status, y cada uno la repetía. Al centralizarla acá:
  - si mañana cambia el algoritmo o el formato, se toca UN solo archivo,
  - nadie se olvida de descifrar o de validar la firma en algún lado.

La idea clave del challenge (Req. 4 y Req. 6):
  - FIRMAR el token  -> garantiza INTEGRIDAD: nadie pudo modificar el contenido.
  - CIFRAR los datos -> garantiza CONFIDENCIALIDAD: nadie puede LEER el contenido.

¡OJO! Firmar y cifrar NO son lo mismo (es el error más común con JWT):
  - Un JWT "normal" solo va FIRMADO. Su payload es base64, o sea, texto plano
    disfrazado: cualquiera que copie el token puede leer el email y el rol.
  - Para que un dato sensible viaje ilegible, hay que CIFRARLO.
Por eso acá hacemos las DOS cosas: ciframos los datos del usuario con Fernet
(AES-128 + HMAC) y además firmamos el token entero con HS256. Doble capa.
"""

import json
import time

import jwt
from cryptography.fernet import Fernet, InvalidToken

import config

# Fernet es el "candado" que cifra y descifra. Necesita una llave (FERNET_KEY),
# que armamos en config.py. Creamos el objeto una sola vez y lo reusamos.
_fernet = Fernet(config.FERNET_KEY)


def create_jwt(user):
    """
    Arma el JWT que le devolvemos al usuario cuando hace login con método 'jwt'.

    Paso 1: metemos los datos sensibles (id, email, rol) en un JSON y lo CIFRAMOS.
            El resultado es un chorizo ilegible (el claim 'data').
    Paso 2: metemos ese chorizo cifrado dentro del payload del JWT, le agregamos
            la fecha de expiración, y FIRMAMOS todo con HS256.

    Resultado: un token que ni se puede leer (cifrado) ni se puede alterar (firmado).
    """
    # Paso 1 - CIFRAR los datos sensibles del usuario.
    claims = json.dumps({
        "sub": user["id"],      # 'sub' = "subject", el dueño del token (su id)
        "email": user["email"],
        "role": user["role"],
    }).encode()
    encrypted = _fernet.encrypt(claims).decode()  # -> string cifrado

    # Paso 2 - FIRMAR el token. 'exp' es cuándo caduca (config.JWT_EXPIRES_IN).
    payload = {
        "data": encrypted,
        "exp": int(time.time()) + config.JWT_EXPIRES_IN,
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def read_jwt(token):
    """
    Hace el camino inverso: agarra el token que mandó el usuario, verifica que
    sea legítimo y devuelve los datos del usuario {sub, email, role}.

    Si algo está mal, LANZA una excepción para que quien llame decida qué hacer
    (típicamente responder 401). Los dos motivos posibles:
      - jwt.ExpiredSignatureError -> el token venció.
      - jwt.InvalidTokenError     -> la firma no cierra, o el cifrado está roto.

    Elegimos lanzar jwt.InvalidTokenError también cuando falla el descifrado, así
    quien llama solo tiene que atrapar los errores de la librería jwt y listo.
    """
    # Primero validamos la FIRMA. Si el token fue tocado o venció, esto explota.
    payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])

    # Si la firma cerró, ahora DESCIFRAMOS los datos sensibles.
    try:
        raw = _fernet.decrypt(payload["data"].encode())
    except (InvalidToken, KeyError):
        # KeyError: no vino el claim 'data'. InvalidToken: el cifrado no cierra.
        # En cualquier caso, el token no es de fiar.
        raise jwt.InvalidTokenError("Payload cifrado inválido o ausente")

    return json.loads(raw)
