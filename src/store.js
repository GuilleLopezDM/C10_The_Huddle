const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const { BCRYPT_ROUNDS } = require('./config');

// Base de datos en memoria (en producción usarías PostgreSQL, MongoDB, etc.)
const users = new Map();          // id -> { id, email, password, role, createdAt }
const sessions = new Map();       // sessionId -> { userId, email, role, csrfToken, createdAt, expiresAt }
const failedAttempts = new Map(); // email -> { count, lastAttempt, lockedUntil }

// Usuario admin precargado para demostración
const adminId = uuidv4();
users.set(adminId, {
  id: adminId,
  email: 'admin@passport.com',
  password: bcrypt.hashSync('Admin1234!', BCRYPT_ROUNDS),
  role: 'admin',
  createdAt: new Date(),
});

module.exports = { users, sessions, failedAttempts };
