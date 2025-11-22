# Cambia a la carpeta "deployments" relativa al script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location "$scriptDir\deployments"

# Levanta todos los servicios definidos en docker-compose.yml en modo detach
docker compose up -d