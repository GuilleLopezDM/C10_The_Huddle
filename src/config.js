module.exports = {
  PORT: process.env.PORT || 3000,
  NODE_ENV: process.env.NODE_ENV || 'development',

  // JWT (Req. 4 y 6)
  JWT_SECRET: process.env.JWT_SECRET || 'super-secret-key-change-in-production',
  JWT_EXPIRES_IN: '1h',

  // Sesiones con cookie (Req. 3)
  SESSION_EXPIRES_IN: 24 * 60 * 60 * 1000, // 24 horas en ms

  // Hashing de contraseñas (Req. 2 y 6)
  BCRYPT_ROUNDS: 10,

  // Protección fuerza bruta (Req. 9)
  MAX_LOGIN_ATTEMPTS: 5,
  LOCK_TIME: 15 * 60 * 1000, // 15 minutos en ms
};
