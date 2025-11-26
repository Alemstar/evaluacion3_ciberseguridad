# Script de Monitorización de Seguridad en Tiempo Real
# Proyecto: evaluacion3_ciberseguridad
# Fecha: 26 de Noviembre de 2025

param(
    [int]$DurationMinutes = 5
)

$ErrorActionPreference = "SilentlyContinue"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "INFORME_MONITORIZACION_$timestamp.md"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   MONITORIZACION DE SEGURIDAD EN TIEMPO REAL" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Función para escribir en el informe
function Write-Report {
    param([string]$Text)
    $Text | Out-File -FilePath $script:reportFile -Append -Encoding UTF8
}

# Inicializar informe
"# INFORME DE MONITORIZACION DE SEGURIDAD EN TIEMPO REAL" | Out-File -FilePath $reportFile -Encoding UTF8
"" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"**Proyecto:** evaluacion3_ciberseguridad" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"**Fecha:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"**Duracion:** $DurationMinutes minutos de monitorizacion continua" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"---" | Out-File -FilePath $reportFile -Append -Encoding UTF8
"" | Out-File -FilePath $reportFile -Append -Encoding UTF8

# 1. ESTADO DE SERVICIOS
Write-Host "[1/8] Verificando estado de servicios..." -ForegroundColor Yellow
Write-Report "## 1. ESTADO DE SERVICIOS"
Write-Report ""
Write-Report "### 1.1 Contenedores Docker"
Write-Report ""
Write-Report '```'

$containerStatus = docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}" 2>&1
$containerStatus | Out-File -FilePath $reportFile -Append -Encoding UTF8

Write-Report '```'
Write-Report ""

# Contar contenedores activos
$runningContainers = (docker ps | Measure-Object -Line).Lines - 1
Write-Host "  Contenedores activos: $runningContainers" -ForegroundColor Green
Write-Report "**Total de contenedores activos:** $runningContainers"
Write-Report ""

# 2. ANÁLISIS DE LOGS
Write-Host "[2/8] Analizando logs de aplicacion..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 2. ANALISIS DE LOGS DE SEGURIDAD"
Write-Report ""
Write-Report "### 2.1 Logs de Aplicacion Flask (Ultimas 30 lineas)"
Write-Report ""
Write-Report '```'

$appLogs = docker logs evaluacion3_ciberseguridad-taskapp-1 --tail 30 2>&1
$appLogs | Out-File -FilePath $reportFile -Append -Encoding UTF8

Write-Report '```'
Write-Report ""

# Detectar patrones sospechosos
$securityPatterns = @{
    "Failed login" = 0
    "404" = 0
    "403" = 0
    "500" = 0
    "error" = 0
    "warning" = 0
}

foreach ($pattern in $securityPatterns.Keys) {
    $count = ($appLogs | Select-String -Pattern $pattern -AllMatches).Matches.Count
    $securityPatterns[$pattern] = $count
}

Write-Report "### 2.2 Eventos Detectados en Logs"
Write-Report ""
Write-Report "| Patron | Cantidad | Nivel |"
Write-Report "|--------|----------|-------|"

$totalEvents = 0
foreach ($pattern in $securityPatterns.Keys) {
    $count = $securityPatterns[$pattern]
    $totalEvents += $count
    $nivel = if ($count -gt 10) { "CRITICO" } elseif ($count -gt 5) { "ALTO" } elseif ($count -gt 0) { "INFO" } else { "OK" }
    Write-Report "| $pattern | $count | $nivel |"
    if ($count -gt 0) {
        Write-Host "  Detectado: $pattern - $count ocurrencias" -ForegroundColor $(if ($count -gt 5) { "Red" } else { "Yellow" })
    }
}

Write-Report ""
if ($totalEvents -eq 0) {
    Write-Host "  No se detectaron eventos sospechosos" -ForegroundColor Green
    Write-Report "**No se detectaron eventos sospechosos**"
}
Write-Report ""

# 3. PRUEBAS DE DISPONIBILIDAD
Write-Host "[3/8] Probando endpoints..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 3. PRUEBAS DE DISPONIBILIDAD"
Write-Report ""
Write-Report "| Endpoint | Estado | Tiempo de Respuesta | Codigo HTTP |"
Write-Report "|----------|--------|---------------------|-------------|"

$endpoints = @(
    @{url="http://localhost:5000/"; name="Pagina principal"}
    @{url="http://localhost:5000/login"; name="Login"}
    @{url="http://localhost:9090/-/healthy"; name="Prometheus"}
    @{url="http://localhost:9100/metrics"; name="Node Exporter"}
)

$endpointsUp = 0
foreach ($ep in $endpoints) {
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $ep.url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $sw.Stop()
        $status = "UP"
        $time = "$($sw.ElapsedMilliseconds)ms"
        $code = $response.StatusCode
        $endpointsUp++
        Write-Host "  $($ep.name): OK ($time)" -ForegroundColor Green
    } catch {
        $status = "DOWN"
        $time = "N/A"
        $code = "Error"
        Write-Host "  $($ep.name): FAILED" -ForegroundColor Red
    }
    Write-Report "| $($ep.name) | $status | $time | $code |"
}

Write-Report ""
Write-Report "**Disponibilidad:** $endpointsUp/$($endpoints.Count) endpoints operativos ($([math]::Round(($endpointsUp/$endpoints.Count)*100, 2))%)"
Write-Report ""

# 4. MÉTRICAS DE PROMETHEUS
Write-Host "[4/8] Recopilando metricas de Prometheus..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 4. METRICAS DE PROMETHEUS"
Write-Report ""

$targetsUp = 0
try {
    $prometheusTargets = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets" -TimeoutSec 10
    $activeTargets = $prometheusTargets.data.activeTargets
    
    Write-Report "### 4.1 Targets Monitoreados"
    Write-Report ""
    Write-Report "| Job Name | Health | Last Scrape | Scrape URL |"
    Write-Report "|----------|--------|-------------|------------|"
    
    foreach ($target in $activeTargets) {
        $health = if ($target.health -eq "up") { 
            $targetsUp++
            "UP" 
        } else { 
            "DOWN" 
        }
        $lastScrape = if ($target.lastScrape) { $target.lastScrape } else { "N/A" }
        $scrapeUrl = $target.scrapeUrl
        $jobName = $target.labels.job
        
        Write-Host "  Target: $jobName - $health" -ForegroundColor $(if ($target.health -eq "up") { "Green" } else { "Red" })
        Write-Report "| $jobName | $health | $lastScrape | $scrapeUrl |"
    }
    
    Write-Report ""
    Write-Report "**Status:** $targetsUp/$($activeTargets.Count) targets operativos"
    Write-Report ""
    
} catch {
    Write-Host "  Prometheus no disponible aun" -ForegroundColor Yellow
    Write-Report "**Nota:** Prometheus iniciando o no disponible"
    Write-Report ""
}

# 5. MÉTRICAS DEL SISTEMA
Write-Host "[5/8] Recopilando metricas del sistema..." -ForegroundColor Yellow
Write-Report "### 4.2 Metricas del Sistema (Node Exporter)"
Write-Report ""

$cpuUsage = $null
$memUsage = $null

try {
    Start-Sleep -Seconds 2
    
    # Intentar obtener CPU usage
    $cpuQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=100-(avg(irate(node_cpu_seconds_total{mode='idle'}[5m]))*100)" -TimeoutSec 10
    if ($cpuQuery.data.result.Count -gt 0) {
        $cpuUsage = [math]::Round([double]$cpuQuery.data.result[0].value[1], 2)
    }
    
    # Intentar obtener Memory usage
    $memQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100)" -TimeoutSec 10
    if ($memQuery.data.result.Count -gt 0) {
        $memUsage = [math]::Round([double]$memQuery.data.result[0].value[1], 2)
    }
    
    Write-Report "| Metrica | Valor | Umbral | Estado |"
    Write-Report "|---------|-------|--------|--------|"
    
    if ($cpuUsage) {
        $cpuStatus = if ($cpuUsage -lt 80) { "Normal" } else { "Alto" }
        Write-Report "| **CPU Usage** | $cpuUsage% | <80% | $cpuStatus |"
        Write-Host "  CPU: $cpuUsage%" -ForegroundColor $(if ($cpuUsage -lt 80) { "Green" } else { "Yellow" })
    }
    
    if ($memUsage) {
        $memStatus = if ($memUsage -lt 85) { "Normal" } else { "Alto" }
        Write-Report "| **Memory Usage** | $memUsage% | <85% | $memStatus |"
        Write-Host "  Memory: $memUsage%" -ForegroundColor $(if ($memUsage -lt 85) { "Green" } else { "Yellow" })
    }
    
    if (!$cpuUsage -and !$memUsage) {
        Write-Report "**Nota:** Metricas del sistema no disponibles (esperando datos...)"
        Write-Host "  Esperando datos del sistema..." -ForegroundColor Yellow
    }
    
} catch {
    Write-Report "**Nota:** Node Exporter iniciando o metricas no disponibles"
    Write-Host "  Node Exporter no disponible" -ForegroundColor Yellow
}

Write-Report ""

# 6. CONFIGURACIÓN DE SEGURIDAD
Write-Host "[6/8] Verificando configuracion de seguridad..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 5. VERIFICACION DE CONFIGURACION DE SEGURIDAD"
Write-Report ""
Write-Report "| Verificacion | Estado | Comentario |"
Write-Report "|--------------|--------|------------|"

$securityChecks = 0
$totalChecks = 0

# Check .env file
$totalChecks++
if (Test-Path .env) {
    $securityChecks++
    Write-Report "| Archivo .env | Presente | Configuracion cargada |"
    Write-Host "  .env: OK" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    
    # Check SECRET_KEY
    $totalChecks++
    if ($envContent -match "SECRET_KEY=.{20,}") {
        $securityChecks++
        Write-Report "| SECRET_KEY | Configurado | Longitud adecuada |"
        Write-Host "  SECRET_KEY: OK" -ForegroundColor Green
    } else {
        Write-Report "| SECRET_KEY | Debil | Requiere mejora |"
        Write-Host "  SECRET_KEY: Debil" -ForegroundColor Yellow
    }
    
    # Check GRAFANA_PASSWORD
    $totalChecks++
    if ($envContent -match "GRAFANA_PASSWORD") {
        $securityChecks++
        Write-Report "| GRAFANA_PASSWORD | Configurado | Proteccion activada |"
        Write-Host "  GRAFANA_PASSWORD: OK" -ForegroundColor Green
    } else {
        Write-Report "| GRAFANA_PASSWORD | No configurado | Acceso sin proteccion |"
        Write-Host "  GRAFANA_PASSWORD: No configurado" -ForegroundColor Red
    }
} else {
    Write-Report "| Archivo .env | No encontrado | Usar .env.example |"
    Write-Host "  .env: No encontrado" -ForegroundColor Red
}

# Check docker-compose running
$totalChecks++
$dcStatus = docker-compose ps 2>&1
if ($LASTEXITCODE -eq 0) {
    $securityChecks++
    Write-Report "| Docker Compose | Operativo | Stack activo |"
    Write-Host "  Docker Compose: OK" -ForegroundColor Green
} else {
    Write-Report "| Docker Compose | Error | Verificar configuracion |"
    Write-Host "  Docker Compose: Error" -ForegroundColor Red
}

Write-Report ""
Write-Report "**Score de Seguridad:** $securityChecks/$totalChecks verificaciones pasadas ($([math]::Round(($securityChecks/$totalChecks)*100, 2))%)"
Write-Report ""

# 7. MONITOREO CONTINUO
Write-Host "[7/8] Ejecutando monitoreo continuo..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 6. MONITOREO CONTINUO ($DurationMinutes minutos)"
Write-Report ""

$startTime = Get-Date
$endTime = $startTime.AddMinutes($DurationMinutes)
$interval = 30 # segundos
$iteration = 0

Write-Host "  Monitoreando durante $DurationMinutes minutos..." -ForegroundColor Cyan
Write-Report "**Inicio:** $(Get-Date -Format 'HH:mm:ss')"
Write-Report "**Intervalo de muestreo:** $interval segundos"
Write-Report ""
Write-Report "| Hora | Containers | CPU% | Mem% | Eventos | Status |"
Write-Report "|------|------------|------|------|---------|--------|"

while ((Get-Date) -lt $endTime) {
    $iteration++
    $now = Get-Date -Format "HH:mm:ss"
    
    # Contar containers activos
    $containers = (docker ps --filter "name=evaluacion3" | Measure-Object -Line).Lines - 1
    
    # Obtener métricas básicas
    try {
        $cpuQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=100-(avg(irate(node_cpu_seconds_total{mode='idle'}[1m]))*100)" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($cpuQuery.data.result.Count -gt 0) {
            $cpu = [math]::Round([double]$cpuQuery.data.result[0].value[1], 1)
        } else {
            $cpu = "N/A"
        }
    } catch {
        $cpu = "N/A"
    }
    
    try {
        $memQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($memQuery.data.result.Count -gt 0) {
            $mem = [math]::Round([double]$memQuery.data.result[0].value[1], 1)
        } else {
            $mem = "N/A"
        }
    } catch {
        $mem = "N/A"
    }
    
    # Contar eventos nuevos en logs
    $newLogs = docker logs evaluacion3_ciberseguridad-taskapp-1 --since 30s 2>&1
    $errorCount = ($newLogs | Select-String -Pattern "error|warning|404|500" -AllMatches).Matches.Count
    
    $status = if ($containers -ge 4 -and $errorCount -eq 0) { "OK" } elseif ($errorCount -gt 5) { "CRITICO" } else { "MONITOR" }
    
    Write-Report "| $now | $containers | $cpu | $mem | $errorCount | $status |"
    Write-Host "  [$iteration] Containers: $containers | CPU: $cpu% | Mem: $mem% | Eventos: $errorCount" -ForegroundColor Cyan
    
    Start-Sleep -Seconds $interval
}

Write-Report ""
Write-Report "**Fin:** $(Get-Date -Format 'HH:mm:ss')"
Write-Report ""

# 8. CONCLUSIONES Y RECOMENDACIONES
Write-Host "[8/8] Generando conclusiones..." -ForegroundColor Yellow
Write-Report "---"
Write-Report ""
Write-Report "## 7. CONCLUSIONES Y RECOMENDACIONES"
Write-Report ""

# Determinar estado general
$overallScore = 0
$maxScore = 4

if ($endpointsUp -ge 3) { $overallScore++ }
if ($securityChecks -ge 3) { $overallScore++ }
if ($totalEvents -lt 10) { $overallScore++ }
if ($targetsUp -ge 2) { $overallScore++ }

$overallPercent = [math]::Round(($overallScore / $maxScore) * 100, 0)

Write-Report "### 7.1 Estado General del Sistema"
Write-Report ""

if ($overallPercent -ge 80) {
    Write-Report "**SEGURO** - Sistema operando dentro de parametros normales ($overallPercent% score)"
    Write-Host "`n  Estado: SEGURO ($overallPercent%)" -ForegroundColor Green
} elseif ($overallPercent -ge 60) {
    Write-Report "**MONITOREAR** - Algunos aspectos requieren atencion ($overallPercent% score)"
    Write-Host "`n  Estado: MONITOREAR ($overallPercent%)" -ForegroundColor Yellow
} else {
    Write-Report "**ALERTA** - Multiples problemas detectados ($overallPercent% score)"
    Write-Host "`n  Estado: ALERTA ($overallPercent%)" -ForegroundColor Red
}

Write-Report ""
Write-Report "### 7.2 Recomendaciones Prioritarias"
Write-Report ""

$recommendations = @()

if ($endpointsUp -lt $endpoints.Count) {
    $recommendations += "- ALTO: Verificar endpoints no disponibles"
}

if ($totalEvents -gt 20) {
    $recommendations += "- CRITICO: Alto numero de eventos de seguridad detectados"
}

if ($securityChecks -lt $totalChecks) {
    $recommendations += "- MEDIO: Completar configuracion de seguridad"
}

if (!$cpuUsage -or !$memUsage) {
    $recommendations += "- INFO: Esperar a que Node Exporter recopile metricas completas"
}

if ($recommendations.Count -eq 0) {
    Write-Report "**No se requieren acciones inmediatas**"
    Write-Report ""
    Write-Report "El sistema esta operando correctamente. Continuar con monitoreo rutinario."
} else {
    foreach ($rec in $recommendations) {
        Write-Report "$rec"
    }
}

Write-Report ""
Write-Report "### 7.3 Proximos Pasos"
Write-Report ""
Write-Report "1. **Inmediato:**"
Write-Report "   - Configurar Grafana con dashboard de seguridad"
Write-Report "   - Implementar alertas automaticas"
Write-Report ""
Write-Report "2. **Corto plazo (24h):**"
Write-Report "   - Establecer baseline de metricas normales"
Write-Report "   - Configurar notificaciones por correo/Slack"
Write-Report ""
Write-Report "3. **Medio plazo (1 semana):**"
Write-Report "   - Integrar analisis de logs centralizado con ELK"
Write-Report "   - Implementar correlacion de eventos"
Write-Report ""

# Footer
Write-Report "---"
Write-Report ""
Write-Report "**Generado por:** Sistema de Monitorizacion DevSecOps"
Write-Report "**Fecha:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
Write-Report "**Proxima revision:** $(Get-Date (Get-Date).AddHours(1) -Format 'dd/MM/yyyy HH:mm:ss')"
Write-Report ""

# Finalizar
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "   MONITORIZACION COMPLETADA" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Informe guardado en: $reportFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resumen Final:" -ForegroundColor Yellow
Write-Host "   - Contenedores activos: $runningContainers" -ForegroundColor White
Write-Host "   - Endpoints disponibles: $endpointsUp/$($endpoints.Count)" -ForegroundColor White
Write-Host "   - Eventos de seguridad: $totalEvents" -ForegroundColor White
Write-Host "   - Score de seguridad: $securityChecks/$totalChecks" -ForegroundColor White
Write-Host "   - Estado general: $overallPercent% HEALTHY" -ForegroundColor $(if ($overallPercent -ge 80) { "Green" } elseif ($overallPercent -ge 60) { "Yellow" } else { "Red" })
Write-Host ""
Write-Host "Para ver el informe:" -ForegroundColor Yellow
Write-Host "  Get-Content $reportFile | more" -ForegroundColor Cyan
Write-Host ""
