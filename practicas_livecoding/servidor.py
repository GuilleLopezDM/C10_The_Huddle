import argparse
from practicas_livecoding.base import crear_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Servidor de una práctica de livecoding')
    parser.add_argument('numero', type=int, choices=range(1, 11))
    parser.add_argument('--port', type=int, default=3001)
    args = parser.parse_args()
    app = crear_app(args.numero)
    print(f'Práctica {args.numero}: {app.config["PRACTICA"]["titulo"]}')
    app.run(port=args.port, debug=True)
