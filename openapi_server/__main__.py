#!/usr/bin/env python3

import connexion
from flask_cors import CORS
from openapi_server import encoder

def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    
    # --- CAMBIO CRÍTICO AQUÍ ---
    # supports_credentials=True: Permite que viajen las cookies
    # origins: Define explícitamente quién puede pedir datos (Tu Frontend)
    CORS(app.app, 
         origins=["http://localhost:5173"], # <--- AJUSTA ESTE PUERTO si tu React usa el 3000 o 5173
         supports_credentials=True)
    # ---------------------------

    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Microservicio Recomendaciones'},
                pythonic_params=True)

    app.run(port=8082)

if __name__ == '__main__':
    main()