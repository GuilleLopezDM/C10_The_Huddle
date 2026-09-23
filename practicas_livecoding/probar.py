"""Pruebas de aceptación: ejecutar desde la raíz, sin levantar servidor."""
import argparse
import importlib
import time
import unittest

import jwt
from flask import g, jsonify

import config
from store import sessions
from practicas_livecoding.base import crear_app
from practicas_livecoding.catalogo import PRACTICAS


class Casos(unittest.TestCase):
    numero = 1

    def setUp(self):
        self.app = crear_app(self.numero)
        self.app.testing = True
        self.client = self.app.test_client()
        self.spec = PRACTICAS[self.numero]

    def login(self, email='alumno@demo.com', **extra):
        response = self.client.post('/login', json=dict(email=email, password='Clave123!', **extra))
        self.assertEqual(response.status_code, 200, response.get_json())
        data = response.get_json()
        self.assertNotIn('password', data)
        if self.spec['tipo'] == 'jwt' or extra.get('authMethod') == 'jwt':
            self.assertTrue(data.get('token'))
            return {'Authorization': 'Bearer ' + data['token']}
        self.assertTrue(data.get('csrfToken'))
        cookie = self.client.get_cookie('sessionId')
        self.assertIsNotNone(cookie)
        self.assertTrue(cookie.http_only)
        self.assertEqual(cookie.same_site, 'Strict')
        return {'X-CSRF-Token': data['csrfToken']}

    def recurso(self, headers=None, uid='alumno'):
        return self.client.open(self.spec['ruta'].replace('<user_id>', uid),
                                method=self.spec['metodo'], headers=headers or {})

    def rechazo(self, response, status):
        self.assertEqual(response.status_code, status, response.get_json())
        self.assertIsInstance(response.get_json().get('error'), str)

    def test_01_exactamente_dos_rutas(self):
        self.assertEqual(len(list(self.app.url_map.iter_rules())), 2)

    def test_02_login_valido_y_recurso(self):
        email = 'admin@demo.com' if self.spec['tipo'] == 'rol' else 'alumno@demo.com'
        headers = self.login(email)
        response = self.recurso(headers)
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json(), {'message': self.spec['mensaje'], 'email': email})

    def test_03_credenciales_incorrectas(self):
        for email in ['alumno@demo.com', 'nadie@demo.com']:
            with self.subTest(email=email):
                self.rechazo(self.client.post('/login', json={'email': email, 'password': 'incorrecta'}), 401)
                self.assertIsNone(self.client.get_cookie('sessionId'))

    def test_04_entrada_invalida(self):
        for data in [{}, [], {'email': 12, 'password': 'x'}, {'email': 'x', 'password': ''},
                     {'email': 'x', 'password': []}, {'email': '', 'password': 'x'}]:
            with self.subTest(data=data):
                self.rechazo(self.client.post('/login', json=data), 400)
        self.rechazo(self.client.post('/login', data='{', content_type='application/json'), 400)
        self.rechazo(self.client.post('/login', data='texto', content_type='text/plain'), 400)

    def test_05_sin_login(self):
        self.rechazo(self.recurso(), 401)

    def test_06_credencial_invalida(self):
        self.client.set_cookie('sessionId', 'inventada')
        self.rechazo(self.recurso(), 401)
        self.rechazo(self.recurso({'Authorization': 'Bearer inventado'}), 401)

    def test_07_expiracion(self):
        headers = self.login()
        if self.spec['tipo'] == 'jwt':
            expired = jwt.encode({'sub': 'alumno', 'email': 'alumno@demo.com', 'role': 'user',
                                  'exp': int(time.time()) - 10}, config.JWT_SECRET, algorithm='HS256')
            headers = {'Authorization': 'Bearer ' + expired}
        else:
            next(iter(sessions.values()))['expires_at'] = time.time() - 10
        self.rechazo(self.recurso(headers), 401)

    def test_08_regla_del_middleware(self):
        kind = self.spec['tipo']
        headers = self.login()
        if kind in ('csrf', 'logout', 'mixto'):
            for h in [{}, {'X-CSRF-Token': ''}, {'X-CSRF-Token': 'incorrecto'}]:
                self.rechazo(self.recurso(h), 403)
            # Un token de otra sesión tampoco sirve.
            self.login('admin@demo.com')
            self.rechazo(self.recurso(headers), 403)
        elif kind == 'rol':
            self.rechazo(self.recurso(headers), 403)
            self.rechazo(self.recurso({**headers, 'X-Role': 'admin'}), 403)
        elif kind == 'propietario':
            self.rechazo(self.recurso(headers, uid='admin'), 403)
            headers = self.login('admin@demo.com')
            self.rechazo(self.recurso(headers, uid='alumno'), 403)
        elif kind == 'reciente':
            next(iter(sessions.values()))['created_at'] = time.time() - 301
            self.rechazo(self.recurso(headers), 403)
        elif kind == 'cookie':
            self.client.delete_cookie('sessionId')
            token = jwt.encode({'sub': 'alumno', 'email': 'alumno@demo.com', 'role': 'user',
                                'exp': int(time.time()) + 3600}, config.JWT_SECRET, algorithm='HS256')
            self.rechazo(self.recurso({'Authorization': 'Bearer ' + token}), 401)
        elif kind == 'jwt':
            for header in ['Bearer ', 'Basic abc', headers['Authorization'] + 'alterado']:
                self.rechazo(self.recurso({'Authorization': header}), 401)

    def test_09_casos_especiales(self):
        kind = self.spec['tipo']
        if kind == 'logout':
            headers = self.login()
            sid = self.client.get_cookie('sessionId').value
            self.assertEqual(self.recurso(headers).status_code, 200)
            self.assertNotIn(sid, sessions)
            self.assertIsNone(self.client.get_cookie('sessionId'))
            self.client.set_cookie('sessionId', sid)
            self.rechazo(self.recurso(headers), 401)
        elif kind == 'mixto':
            headers = self.login(authMethod='jwt')
            self.assertEqual(self.recurso(headers).status_code, 200)
            self.rechazo(self.recurso({'Authorization': 'Bearer falso'}), 401)
            self.rechazo(self.client.post('/login', json={'email': 'alumno@demo.com',
                         'password': 'Clave123!', 'authMethod': 'otro'}), 400)
        elif kind in ('csrf',):
            # Prueba directa del middleware: no agrega rutas al ejercicio.
            module = importlib.import_module(f'practicas_livecoding.ejercicios.p{self.numero:02d}')
            for method in ['GET', 'HEAD', 'OPTIONS']:
                with self.app.test_request_context('/', method=method):
                    g.auth_method = 'cookie'
                    g.session_id = 'demo'
                    response = self.app.make_response(module.middleware(lambda: jsonify(ok=True))())
                    self.assertEqual(response.status_code, 200)
        else:
            self.skipTest('Los casos específicos están en la prueba 08')


def suite(numeros):
    result = unittest.TestSuite()
    for n in numeros:
        cls = type(f'Practica{n:02d}', (Casos,), {'numero': n})
        result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Corregir una práctica o todas')
    parser.add_argument('numero', help='1 a 10, o todas')
    args = parser.parse_args()
    if args.numero == 'todas':
        numeros = list(PRACTICAS)
    elif args.numero.isdigit() and int(args.numero) in PRACTICAS:
        numeros = [int(args.numero)]
    else:
        parser.error('Elegí un número del 1 al 10 o todas')
    result = unittest.TextTestRunner(verbosity=2).run(suite(numeros))
    raise SystemExit(0 if result.wasSuccessful() else 1)
