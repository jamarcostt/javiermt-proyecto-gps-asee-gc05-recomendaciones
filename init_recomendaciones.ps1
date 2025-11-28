# init_recomendaciones.ps1

Write-Host "--- Iniciando Script de Inicio ---" -ForegroundColor Cyan

# 1. Comprobar si Docker está corriendo
$dockerIsRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

if (!$dockerIsRunning) {
    Write-Host "Docker Desktop no esta abierto. Iniciando Docker Desktop..." -ForegroundColor Yellow
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
    } else {
        Write-Error "No se ha encontrado Docker Desktop en la ruta estandar."
        exit 1
    }

    Write-Host "Esperando a que el motor de Docker se prepare..." -NoNewline
    do {
        Start-Sleep -Seconds 2
        Write-Host "." -NoNewline
        $dockerInfo = docker info 2>&1 | Out-String
    } until ($dockerInfo -notmatch "error" -and $dockerInfo -notmatch "Is the docker daemon running")
    Write-Host "`nDocker esta listo." -ForegroundColor Green
} else {
    Write-Host "Docker ya se esta ejecutando." -ForegroundColor Green
}

# 2. Entrar en la carpeta deployments
if (Test-Path ".\deployments") {
    Set-Location ".\deployments"
    Write-Host "Entrando en 'deployments'..."
} else {
    Write-Error "La carpeta 'deployments' no existe."
    exit 1
}

# 3. Docker Compose Up
Write-Host "Levantando servicios auxiliares (Docker)..." -ForegroundColor Cyan
docker compose up -d

# 4. Salir del directorio
Set-Location ..
Write-Host "Regresando al directorio raiz..."

# 5. Instalar dependencias Python
# Asumimos que requirements.txt está en la raíz, donde estamos ahora.
if (Test-Path "requirements.txt") {
    Write-Host "Instalando dependencias desde requirements.txt..." -ForegroundColor Cyan
    py -m pip install -r requirements.txt
} else {
    Write-Warning "No se ha encontrado el archivo requirements.txt. Saltando instalacion."
}

# Comprobar si la instalación fue bien (o si se saltó) antes de ejecutar
if ($LASTEXITCODE -eq 0) {
    # 6. Ejecutar servidor
    Write-Host "Iniciando servidor Python (openapi_server)..." -ForegroundColor Cyan
    python -m openapi_server
} else {
    Write-Error "Ha habido un error al instalar las dependencias."
}