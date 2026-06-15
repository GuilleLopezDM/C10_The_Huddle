import time
import config
from store import failed_attempts

# Req. 9 - Protección contra ataques de fuerza bruta.
# Bloquea la cuenta después de MAX_LOGIN_ATTEMPTS fallos durante LOCK_TIME segundos.


def check_rate_limit(email):
    """Devuelve {'locked': True/False, 'locked_until': timestamp}"""
    record = failed_attempts.get(email)
    if not record:
        return {"locked": False}

    # Si el bloqueo ya expiró, limpiamos el registro
    if record["locked_until"] and record["locked_until"] <= time.time():
        del failed_attempts[email]
        return {"locked": False}

    if record["locked_until"] and record["locked_until"] > time.time():
        return {"locked": True, "locked_until": record["locked_until"]}

    return {"locked": False}


def record_failed_attempt(email):
    """Incrementa el contador de fallos. Si supera el límite, bloquea la cuenta."""
    record = failed_attempts.get(email, {"count": 0, "last_attempt": None, "locked_until": None})
    record["count"] += 1
    record["last_attempt"] = time.time()

    if record["count"] >= config.MAX_LOGIN_ATTEMPTS:
        record["locked_until"] = time.time() + config.LOCK_TIME

    failed_attempts[email] = record


def clear_attempts(email):
    """Limpia los intentos fallidos tras un login exitoso."""
    failed_attempts.pop(email, None)
