import os

# JWT (Req. 4 y 6)
JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-key-change-in-production")
JWT_EXPIRES_IN = 3600  # 1 hora en segundos

# Sesiones con cookie (Req. 3)
SESSION_EXPIRES_IN = 24 * 60 * 60  # 24 horas en segundos

# Hashing de contraseñas (Req. 2 y 6)
BCRYPT_ROUNDS = 10

# Protección fuerza bruta (Req. 9)
MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME = 15 * 60  # 15 minutos en segundos

PORT = int(os.environ.get("PORT", 3000))
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
