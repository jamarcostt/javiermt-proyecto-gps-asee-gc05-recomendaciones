#!/usr/bin/env python3

import connexion
from flask_cors import CORS

from openapi_server import encoder


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    # Habilitar CORS para todas las rutas y orígenes.
    CORS(app.app)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Microservicio Recomendaciones'},
                pythonic_params=True)

    app.run(port=8082)


if __name__ == '__main__':
    main()
