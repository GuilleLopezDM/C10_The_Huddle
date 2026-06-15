import uuid
from datetime import datetime
import bcrypt
import config

# Base de datos en memoria (en producción usarías PostgreSQL, MongoDB, etc.)
users = {}           # id -> { id, email, password, role, created_at }
sessions = {}        # session_id -> { user_id, email, role, csrf_token, created_at, expires_at }
failed_attempts = {} # email -> { count, last_attempt, locked_until }

# Usuario admin precargado para demostración
_admin_id = str(uuid.uuid4())
users[_admin_id] = {
    "id": _admin_id,
    "email": "admin@passport.com",
    "password": bcrypt.hashpw(b"Admin1234!", bcrypt.gensalt(config.BCRYPT_ROUNDS)),
    "role": "admin",
    "created_at": datetime.now().isoformat(),
}
