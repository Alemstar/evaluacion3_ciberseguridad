# INFORME DE MONITORIZACION DE SEGURIDAD EN TIEMPO REAL

**Proyecto:** evaluacion3_ciberseguridad
**Fecha:** 26-11-2025 01:55:56
**Duracion:** 5 minutos de monitorizacion continua

---

## 1. ESTADO DE SERVICIOS

### 1.1 Contenedores Docker

```
NAMES                                        STATUS                     PORTS
evaluacion3_ciberseguridad-taskapp-1         Up 6 minutes (healthy)     5000/tcp
evaluacion3_ciberseguridad-postgres-1        Up 6 minutes (healthy)     5432/tcp
evaluacion3_ciberseguridad-prometheus-1      Up 6 minutes (unhealthy)   0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp
evaluacion3_ciberseguridad-node-exporter-1   Up 6 minutes               0.0.0.0:9100->9100/tcp, [::]:9100->9100/tcp
```

**Total de contenedores activos:** 4

---

## 2. ANALISIS DE LOGS DE SEGURIDAD

### 2.1 Logs de Aplicacion Flask (Ultimas 30 lineas)

```
127.0.0.1 - - [26/Nov/2025:04:49:44 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:50:14 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:50:44 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:51:14 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:51:44 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:52:14 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:52:44 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:53:14 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:53:45 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:54:15 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:54:45 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:55:15 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
127.0.0.1 - - [26/Nov/2025:04:55:45 +0000] "GET / HTTP/1.1" 200 64 "-" "curl/8.14.1"
```

### 2.2 Eventos Detectados en Logs

| Patron | Cantidad | Nivel |
|--------|----------|-------|
| Failed login | 0 | OK |
| 500 | 0 | OK |
| 403 | 0 | OK |
| error | 0 | OK |
| 404 | 0 | OK |
| warning | 0 | OK |

**No se detectaron eventos sospechosos**

---

## 3. PRUEBAS DE DISPONIBILIDAD

| Endpoint | Estado | Tiempo de Respuesta | Codigo HTTP |
|----------|--------|---------------------|-------------|
| Pagina principal | DOWN | N/A | Error |
| Login | DOWN | N/A | Error |
| Prometheus | UP | 51ms | 200 |
| Node Exporter | UP | 314ms | 200 |

**Disponibilidad:** 2/4 endpoints operativos (50%)

---

## 4. METRICAS DE PROMETHEUS

### 4.1 Targets Monitoreados

| Job Name | Health | Last Scrape | Scrape URL |
|----------|--------|-------------|------------|
| flask-app | DOWN | 2025-11-26T04:56:02.076725811Z | http://taskapp:5000/metrics |
| node-exporter | UP | 2025-11-26T04:56:08.150032881Z | http://node-exporter:9100/metrics |
| prometheus | UP | 2025-11-26T04:55:55.223818471Z | http://localhost:9090/metrics |

**Status:** 2/3 targets operativos

### 4.2 Metricas del Sistema (Node Exporter)

**Nota:** Node Exporter iniciando o metricas no disponibles

---

## 5. VERIFICACION DE CONFIGURACION DE SEGURIDAD

| Verificacion | Estado | Comentario |
|--------------|--------|------------|
| Archivo .env | Presente | Configuracion cargada |
| SECRET_KEY | Configurado | Longitud adecuada |
| GRAFANA_PASSWORD | Configurado | Proteccion activada |
| Docker Compose | Operativo | Stack activo |

**Score de Seguridad:** 4/4 verificaciones pasadas (100%)

---

## 6. MONITOREO CONTINUO (5 minutos)

**Inicio:** 01:56:13
**Intervalo de muestreo:** 30 segundos

| Hora | Containers | CPU% | Mem% | Eventos | Status |
|------|------------|------|------|---------|--------|
| 01:56:13 | 4 | 0.7 | 8.6 | 0 | OK |
