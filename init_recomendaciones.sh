#!/bin/bash

echo "--- Iniciando Script de Inicio ---"

# 1. Comprobar y abrir Docker
if ! docker info > /dev/null 2>&1; then
    echo "Docker no esta ejecutandose. Intentando iniciar..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Docker
    else
        echo "Iniciando Docker en Linux..."
        # Descomenta la línea de abajo si usas systemd y tienes permisos
        # sudo systemctl start docker
    fi

    echo "Esperando a que Docker se inicie..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
        printf "."
    done
    echo ""
    echo "Docker está listo."
fi

# 2. Entrar en deployments
if [ -d "./deployments" ]; then
    cd deployments
    echo "Directorio cambiado a 'deployments'"
else
    echo "Error: La carpeta 'deployments' no existe."
    exit 1
fi

# 3. Docker Compose Up
echo "Levantando contenedores..."
docker compose up -d

# 4. Salir del directorio
cd ..
echo "Regresando al directorio raiz"

# 5. Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias..."
    py -m pip install -r requirements.txt
else
    echo "Aviso: No se ha encontrado requirements.txt"
fi

# 6. Ejecutar servidor
# Solo ejecutamos si el paso anterior (pip) no dio error
if [ $? -eq 0 ]; then
    echo "Iniciando openapi_server..."
    python -m openapi_server
else
    echo "Error instalando dependencias. Abortando ejecucion."
    exit 1
fi