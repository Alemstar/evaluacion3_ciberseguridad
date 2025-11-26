# Resumen de Revisiones y Monitorización de Seguridad

**Proyecto:** evaluacion3_ciberseguridad  
**Fecha:** 26 de Noviembre de 2025

---

## 1. Resumen General

Este documento resume las actividades de monitorización y pruebas de seguridad (SAST, DAST) realizadas. La monitorización continua identificó problemas de disponibilidad y configuración, mientras que las pruebas de seguridad encontraron **vulnerabilidades críticas en dependencias de terceros** y **fallos en la configuración de cabeceras HTTP**.

No se detectaron ataques activos. Las acciones de respuesta se centraron en corregir las vulnerabilidades y problemas de configuración encontrados.

---

## 2. Actividades de Monitorización

Se ejecutó un script (`monitor-security.ps1`) que realizó las siguientes comprobaciones:

- **Estado de Servicios:** Verificó 4 contenedores Docker activos.
- **Análisis de Logs:** No se encontraron eventos sospechosos en los logs de la aplicación.
- **Disponibilidad de Endpoints:** Se detectó que los endpoints de la aplicación (`/` y `/login`) estaban **caídos (DOWN)**.
- **Métricas de Prometheus:** Se identificó que el target `flask-app` estaba **DOWN** por falta de un endpoint `/metrics`.
- **Configuración de Seguridad:** Las verificaciones básicas (archivo `.env`, `SECRET_KEY`) pasaron correctamente.
- **Monitorización Continua:** El sistema se mostró estable y con bajo consumo de recursos durante 5 minutos.

---

## 3. Incidentes Detectados y Acciones de Respuesta

| Incidente | Descripción | Severidad | Acción de Respuesta Recomendada |
| :--- | :--- | :--- | :--- |
| **Vulnerabilidades en Dependencias** | 10 CVEs críticas en `gunicorn`, `Jinja2` y `Werkzeug`. | **CRÍTICA** | Actualizar las librerías usando `requirements-secure.txt` y reconstruir la imagen de Docker. |
| **Cabeceras HTTP Faltantes** | Ausencia de `Content-Security-Policy`, `X-Frame-Options`, etc. | **MEDIA** | Implementar las cabeceras de seguridad en `src/secure_app.py` usando el código provisto en `security_headers_implementation.py`. |
| **Falta de Endpoint de Métricas** | La aplicación no expone un endpoint `/metrics` para Prometheus. | **ALTA** | Añadir `prometheus-client` a los requisitos e implementar el endpoint en `src/secure_app.py`. |
| **Endpoints Inaccesibles** | La aplicación no es accesible desde fuera del contenedor. | **CRÍTICA** | Revisar y corregir la configuración de mapeo de puertos en `docker-compose.yml` y la configuración de red de Docker. |

---

## 4. Conclusión

La estrategia de monitorización fue efectiva para identificar proactivamente riesgos críticos. Aunque no se detectaron ataques, las vulnerabilidades y fallos de configuración encontrados requerían una acción de respuesta inmediata, la cual ha sido documentada y planificada.