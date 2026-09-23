"""Contratos de los diez simulacros; no contiene soluciones."""
PRACTICAS = {
    1: dict(titulo='CSRF: confirmar una acción', metodo='POST', ruta='/confirmar', tipo='csrf', mensaje='Acción confirmada'),
    2: dict(titulo='CSRF: editar preferencias', metodo='PATCH', ruta='/preferencias', tipo='csrf', mensaje='Preferencias actualizadas'),
    3: dict(titulo='CSRF: eliminar un borrador', metodo='DELETE', ruta='/borrador', tipo='csrf', mensaje='Borrador eliminado'),
    4: dict(titulo='CSRF: cerrar sesión', metodo='POST', ruta='/logout', tipo='logout', mensaje='Sesión cerrada'),
    5: dict(titulo='Autenticación con cookie', metodo='GET', ruta='/perfil', tipo='cookie', mensaje='Perfil privado'),
    6: dict(titulo='Autenticación con JWT', metodo='GET', ruta='/perfil', tipo='jwt', mensaje='Perfil privado'),
    7: dict(titulo='Permisos de administrador', metodo='GET', ruta='/panel', tipo='rol', mensaje='Panel privado'),
    8: dict(titulo='Acceso al recurso propio', metodo='GET', ruta='/usuarios/<user_id>', tipo='propietario', mensaje='Recurso privado'),
    9: dict(titulo='Sesión reciente', metodo='GET', ruta='/datos-sensibles', tipo='reciente', mensaje='Datos privados'),
    10: dict(titulo='CSRF con cookie y JWT por Bearer', metodo='POST', ruta='/confirmar', tipo='mixto', mensaje='Acción confirmada'),
}

CONTRATOS = {
    'csrf': 'verify_auth ya corre antes. Exigir sesión existente y X-CSRF-Token no vacío igual al csrf_token de esa sesión en métodos de escritura. Si falta o difiere: 403. GET/HEAD/OPTIONS pasan sin CSRF. Usar g.session_id y sessions. Conservar @wraps y ejecutar f(*args, **kwargs) si está permitido.',
    'logout': 'Mismo contrato CSRF de p01. La ruta además elimina sessions[g.session_id] y borra la cookie sessionId en la respuesta exitosa.',
    'cookie': 'Leer cookie sessionId. Si falta, no existe en sessions o expires_at <= time.time(): 401. Si es válida, guardar g.user con id (desde user_id), email y role; g.session_id y g.auth_method="cookie". Ejecutar la ruta. No aceptar JWT en este ejercicio.',
    'jwt': 'Exigir Authorization: Bearer <token> no vacío. Usar leer_jwt para validar firma y vencimiento; ante jwt.InvalidTokenError responder 401. Guardar g.user con id (desde sub), email y role, y g.auth_method="jwt". Ejecutar la ruta. No aceptar cookies en este ejercicio.',
    'rol': 'verify_auth ya corre antes. Permitir solo g.user["role"] == "admin"; de lo contrario 403. Nunca usar un rol recibido en el JSON o headers.',
    'propietario': 'verify_auth ya corre antes. Comparar kwargs["user_id"] con g.user["id"]. Solo permitir si coinciden, incluso para un administrador. De lo contrario 403. Reenviar args y kwargs a la ruta.',
    'reciente': 'verify_auth ya corre antes. Exigir autenticación cookie y sesión existente. Si falta la sesión o el método no es cookie: 401. Permitir antigüedad time.time() - created_at <= 300 segundos; si es mayor: 403. La expiración general ya la verifica verify_auth.',
    'mixto': 'verify_auth ya corre antes. Si g.auth_method == "jwt", permitir sin CSRF (JWT enviado explícitamente por Authorization). Con cookie, aplicar el contrato CSRF de p01. No basta con que exista el header Authorization: verify_auth tiene que haberlo validado.',
}
