# INFORME DE PRUEBAS DE SEGURIDAD
**Proyecto:** evaluacion3_ciberseguridad  
**Fecha:** 26 de Noviembre de 2025  
**Ejecutado por:** DevSecOps Team

---

## ÍNDICE
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Herramientas Utilizadas](#herramientas-utilizadas)
3. [Análisis Estático (SAST)](#análisis-estático-sast)
4. [Análisis de Dependencias](#análisis-de-dependencias)
5. [Análisis Dinámico (DAST)](#análisis-dinámico-dast)
6. [Vulnerabilidades Encontradas](#vulnerabilidades-encontradas)
7. [Mitigaciones Implementadas](#mitigaciones-implementadas)
8. [Recomendaciones](#recomendaciones)

---

## RESUMEN EJECUTIVO

Se realizaron pruebas de seguridad exhaustivas sobre la aplicación web Flask utilizando herramientas SAST y DAST. El análisis revela que el código de la aplicación está **bien protegido** contra vulnerabilidades comunes, sin embargo, se identificaron **vulnerabilidades críticas en dependencias de terceros** que requieren actualización inmediata.

### Métricas Generales
- **Líneas de código analizadas:** 192
- **Vulnerabilidades en código:** 0
- **Vulnerabilidades en dependencias:** 10 (críticas)
- **Alertas DAST Medium:** 6
- **Alertas DAST High/Critical:** 0

---

## HERRAMIENTAS UTILIZADAS

### 1. SAST (Static Application Security Testing)
- **Bandit v1.8.0:** Análisis de código Python
- **Resultado:** ✅ 0 vulnerabilidades detectadas

### 2. Dependency Scanning
- **Safety v3.7.0:** Análisis de dependencias Python
- **Resultado:** ⚠️ 10 vulnerabilidades encontradas en librerías

### 3. DAST (Dynamic Application Security Testing)
- **OWASP ZAP v2.16.1:** Escaneo completo de penetración
- **URLs analizadas:** 5
- **Pruebas ejecutadas:** 139
- **Resultado:** ⚠️ 6 advertencias de configuración (Medium)

---

## ANÁLISIS ESTÁTICO (SAST)

### Bandit - Análisis de Código Fuente

**Archivos Analizados:**
- `src/secure_app.py` (134 líneas)
- `src/secure_create_db.py` (58 líneas)

**Resultado:** ✅ **EXCELENTE - 0 vulnerabilidades**

```json
{
  "metrics": {
    "_totals": {
      "SEVERITY.HIGH": 0,
      "SEVERITY.MEDIUM": 0,
      "SEVERITY.LOW": 0,
      "loc": 192
    }
  },
  "results": []
}
```

**Interpretación:** El código fuente de la aplicación NO contiene vulnerabilidades detectables estáticamente. Las prácticas de codificación segura están correctamente implementadas.

---

## ANÁLISIS DE DEPENDENCIAS

### Safety - Vulnerabilidades en Librerías

**Paquetes Escaneados:** 9  
**Vulnerabilidades Encontradas:** 10 (CRÍTICAS)

### ⚠️ VULNERABILIDADES CRÍTICAS POR DEPENDENCIA

#### 1. **Gunicorn 21.2.0** (2 vulnerabilidades)

| CVE | Severidad | Descripción | Versión Segura |
|-----|-----------|-------------|----------------|
| **CVE-2024-1135** | ALTA | HTTP Request Smuggling - Validación incorrecta de Transfer-Encoding headers permitiendo bypass de restricciones de seguridad | ≥22.0.0 |
| **CVE-2024-6827** | ALTA | HTTP Request/Response Smuggling - Parser HTTP no valida correctamente mensajes con Transfer-Encoding y Content-Length conflictivos | ≥22.0.0 |

**Impacto:** Los atacantes pueden:
- Envenenar caché
- Manipular sesiones
- Acceder a endpoints restringidos
- Exposición de datos

**Recomendación:** Actualizar a `gunicorn==23.0.0`

---

#### 2. **Jinja2 3.1.4** (3 vulnerabilidades)

| CVE | Severidad | Descripción | Versión Segura |
|-----|-----------|-------------|----------------|
| **CVE-2024-56201** | CRÍTICA | Ejecución arbitraria de código Python - Bypass del sandbox cuando el atacante controla nombre y contenido del template | ≥3.1.5 |
| **CVE-2025-27516** | CRÍTICA | Bypass del sandbox vía filtro `\|attr` - Permite ejecutar código Python arbitrario | ≥3.1.6 |
| **CVE-2024-56326** | ALTA | Llamadas indirectas a str.format() evaden sandbox - Ejecución de código mediante referencias maliciosas | ≥3.1.5 |

**Impacto:** 
- Ejecución remota de código (RCE)
- Compromiso total del servidor
- Violación del sandbox de seguridad

**Recomendación:** Actualizar a `Jinja2==3.1.6`

---

#### 3. **Werkzeug 3.0.0** (5 vulnerabilidades)

| CVE | Severidad | Descripción | Versión Segura |
|-----|-----------|-------------|----------------|
| **CVE-2023-46136** | ALTA | Denegación de Servicio (DoS) - Parsing multipart sin límite de búfer agota CPU/memoria | ≥3.0.1 |
| **CVE-2024-49766** | MEDIA | Path Traversal en Windows - safe_join() no valida correctamente paths absolutos | ≥3.0.6 |
| **CVE-2024-49767** | CRÍTICA | Resource Exhaustion - Parser multipart consume 3-8x el tamaño de upload en RAM sin límite | ≥3.0.6 |
| **CVE-2024-34069** | MEDIA | Debugger vulnerable - Permite ejecución de código bajo ciertas circunstancias | ≥3.0.3 |
| **Sin CVE** | MEDIA | Slow multipart parsing - DoS por parsing lento de partes grandes | ≥3.0.1 |

**Impacto:**
- Denegación de servicio (DoS)
- Agotamiento de recursos (RAM/CPU)
- Path traversal en sistemas Windows
- Ejecución remota de código (en modo debug)

**Recomendación:** Actualizar a `Werkzeug==3.1.3`

---

## ANÁLISIS DINÁMICO (DAST)

### OWASP ZAP - Escaneo de Penetración Completo

**Target:** http://host.docker.internal:5000  
**Tipo de Escaneo:** Full Scan (Active + Passive)  
**Duración:** ~5 minutos  
**Fecha:** 26/11/2025 03:57:27 UTC

### Resultados Generales

```
Total URLs: 5
Pruebas Ejecutadas: 139
PASS: 133 (95.7%)
WARN: 6 (4.3%)
FAIL: 0 (0%)
```

### ⚠️ ADVERTENCIAS DETECTADAS (Medium Risk)

#### 1. Missing Anti-clickjacking Header (x2)
- **Plugin ID:** 10020
- **Severidad:** Medium
- **CWE:** CWE-1021
- **URLs Afectadas:** 
  - `http://host.docker.internal:5000/`
  - `http://host.docker.internal:5000`

**Descripción:** Falta el header `X-Frame-Options` o `Content-Security-Policy` con directiva `frame-ancestors`.

**Riesgo:** La aplicación puede ser embebida en un iframe malicioso permitiendo ataques de clickjacking.

**Solución:**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    return response
```

---

#### 2. X-Content-Type-Options Header Missing (x2)
- **Plugin ID:** 10021
- **Severidad:** Medium
- **CWE:** CWE-693

**Descripción:** El header `X-Content-Type-Options: nosniff` no está configurado.

**Riesgo:** El navegador puede interpretar erróneamente el tipo MIME, permitiendo ataques XSS.

**Solución:**
```python
response.headers['X-Content-Type-Options'] = 'nosniff'
```

---

#### 3. Content Security Policy (CSP) Header Not Set (x4)
- **Plugin ID:** 10038
- **Severidad:** Medium
- **CWE:** CWE-693
- **WASC:** 15

**Descripción:** No existe política CSP configurada.

**Riesgo:** Sin CSP, la aplicación es más vulnerable a XSS y ataques de inyección de datos.

**Solución:**
```python
response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)
```

---

#### 4. Permissions Policy Header Not Set (x4)
- **Plugin ID:** 10063
- **Severidad:** Medium

**Descripción:** El header `Permissions-Policy` no está configurado.

**Riesgo:** Funcionalidades del navegador (cámara, micrófono, geolocalización) no están explícitamente restringidas.

**Solución:**
```python
response.headers['Permissions-Policy'] = (
    "geolocation=(), microphone=(), camera=(), "
    "payment=(), usb=(), magnetometer=(), gyroscope=()"
)
```

---

#### 5. HTTP Only Site (x1)
- **Plugin ID:** 10106
- **Severidad:** Medium

**Descripción:** La aplicación se sirve únicamente sobre HTTP sin HTTPS.

**Riesgo:** 
- Interceptación de credenciales
- Man-in-the-Middle (MITM)
- Exposición de session cookies

**Solución:** Implementar HTTPS con certificado SSL/TLS válido en producción.

---

#### 6. Insufficient Site Isolation Against Spectre Vulnerability (x5)
- **Plugin ID:** 90004
- **Severidad:** Medium

**Descripción:** Falta configuración de aislamiento del sitio contra vulnerabilidades Spectre.

**Riesgo:** Posible fuga de información sensible a través de ataques de canal lateral.

**Solución:**
```python
response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
```

---

### ✅ PRUEBAS PASADAS (133 de 133)

**Categorías de pruebas exitosas:**
- ✅ SQL Injection (todas las variantes)
- ✅ Cross-Site Scripting (XSS) - Reflected, Persistent, DOM-based
- ✅ Path Traversal
- ✅ Remote Code Execution
- ✅ CSRF Protection
- ✅ Session Management
- ✅ Authentication
- ✅ Server-Side Request Forgery (SSRF)
- ✅ XML External Entity (XXE)
- ✅ Remote File Inclusion
- ✅ Command Injection
- ✅ LDAP Injection
- ✅ Template Injection
- ✅ Log4Shell
- ✅ Spring4Shell

---

## VULNERABILIDADES ENCONTRADAS

### Resumen por Categoría

| Categoría | Cantidad | Severidad Máxima | Estado |
|-----------|----------|------------------|--------|
| **Código Fuente** | 0 | N/A | ✅ SEGURO |
| **Dependencias** | 10 | CRÍTICA | ⚠️ REQUIERE ACCIÓN |
| **Configuración HTTP** | 6 | MEDIA | ⚠️ REQUIERE ACCIÓN |
| **Vulnerabilidades Aplicación** | 0 | N/A | ✅ SEGURO |

### Clasificación por Severidad

```
CRÍTICA:  3 (Jinja2 RCE x2, Werkzeug DoS x1)
ALTA:     4 (Gunicorn HTTP Smuggling x2, Jinja2 sandbox x1, Werkzeug DoS x1)
MEDIA:    9 (Headers HTTP x6, Werkzeug x3)
BAJA:     0
```

---

## MITIGACIONES IMPLEMENTADAS

### 1. Prevención de SQL Injection ✅

**Código:** `src/secure_app.py`

```python
# ANTES (Vulnerable):
# cursor.execute(f"SELECT * FROM users WHERE username='{username}'")

# DESPUÉS (Seguro):
cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
```

**Estado:** ✅ **IMPLEMENTADO**  
**Verificación:** Bandit y ZAP confirman ausencia de SQL Injection

---

### 2. Protección de Contraseñas con bcrypt ✅

**Código:** `src/secure_create_db.py`, `src/secure_app.py`

```python
# Hash seguro con bcrypt (12 rondas)
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')

# Verificación segura
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))
```

**Estado:** ✅ **IMPLEMENTADO**  
**Beneficios:**
- Protección contra rainbow tables
- Resistencia a fuerza bruta (12 rondas)
- Salt único por contraseña

---

### 3. Configuración Segura de Sesiones ✅

**Código:** `src/secure_app.py`

```python
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Solo HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # No accesible vía JavaScript
    SESSION_COOKIE_SAMESITE='Lax',   # Protección CSRF
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutos
)
```

**Estado:** ✅ **IMPLEMENTADO**  
**Verificación:** ZAP confirma cookies seguras (HttpOnly flag PASS)

---

### 4. Validación de Entrada con WTForms ✅

**Código:** `src/secure_app.py`

```python
class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=3, max=50),
        validators.Regexp('^[A-Za-z0-9_]+$',
            message='Solo caracteres alfanuméricos permitidos')
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=128)
    ])
```

**Estado:** ✅ **IMPLEMENTADO**  
**Protecciones:**
- Regex contra caracteres especiales maliciosos
- Límites de longitud
- Validación del lado del servidor

---

### 5. Protección CSRF ✅

**Código:** `src/secure_app.py`

```python
app.config['WTF_CSRF_ENABLED'] = True

# En templates:
<form method="POST">
    {{ form.hidden_tag() }}  <!-- Token CSRF -->
    ...
</form>
```

**Estado:** ✅ **IMPLEMENTADO**  
**Verificación:** ZAP - "Absence of Anti-CSRF Tokens" = PASS

---

### 6. Logging Estructurado y Seguro ✅

**Código:** `src/secure_app.py`

```python
# Logging configurado para Docker (stdout)
if os.getenv('DOCKER_ENV') == 'true':
    log_handler = logging.StreamHandler(sys.stdout)
else:
    log_handler = RotatingFileHandler('app.log', maxBytes=10485760, backupCount=10)

log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
app.logger.setLevel(logging.INFO)
```

**Estado:** ✅ **IMPLEMENTADO**  
**Características:**
- Rotación de logs (10MB, 10 archivos)
- Sin información sensible en logs
- Compatible con contenedores Docker

---

### 7. Usuario No-Root en Docker ✅

**Código:** `Dockerfile`

```dockerfile
# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Cambiar permisos
COPY --chown=appuser:appuser src/secure_app.py .

# Ejecutar como no-root
USER appuser
```

**Estado:** ✅ **IMPLEMENTADO**  
**Beneficio:** Reducción de superficie de ataque en caso de compromiso del contenedor

---

### 8. Manejo Seguro de Errores ✅

**Código:** `src/secure_app.py`

```python
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f'Server Error: {e}')
    return render_template('500.html'), 500
```

**Estado:** ✅ **IMPLEMENTADO**  
**Protección:** No expone stack traces ni información sensible al usuario

---

## RECOMENDACIONES

### 🔴 CRÍTICAS (Implementar Inmediatamente)

#### 1. Actualizar Dependencias Vulnerables

**Acción Requerida:**

```bash
# requirements.txt - ACTUALIZADO
Flask==3.0.0
Werkzeug==3.1.3        # ACTUALIZADO de 3.0.0 (5 CVEs corregidos)
Jinja2==3.1.6          # ACTUALIZADO de 3.1.4 (3 CVEs corregidos)
bcrypt==4.1.1
flask-wtf==1.2.0
wtforms==3.1.0
gunicorn==23.0.0       # ACTUALIZADO de 21.2.0 (2 CVEs corregidos)
python-dotenv==1.0.0
prometheus-client==0.19.0
```

**Impacto:** Elimina 10 vulnerabilidades críticas y altas  
**Prioridad:** 🔴 URGENTE  
**Esfuerzo:** 15 minutos

---

#### 2. Implementar Headers de Seguridad HTTP

**Código a agregar en `src/secure_app.py`:**

```python
@app.after_request
def set_security_headers(response):
    """Configurar headers de seguridad HTTP"""
    # Anti-clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevenir MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=(), gyroscope=()"
    )
    
    # Protección Spectre
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

**Impacto:** Elimina 6 alertas Medium de ZAP  
**Prioridad:** 🔴 ALTA  
**Esfuerzo:** 5 minutos

---

### 🟡 ALTAS (Implementar Antes de Producción)

#### 3. Implementar HTTPS/TLS

**Opciones:**

**A) Desarrollo Local:**
```bash
# Generar certificado autofirmado
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Ejecutar con SSL
gunicorn --certfile=cert.pem --keyfile=key.pem \
  --bind 0.0.0.0:5000 secure_app:app
```

**B) Producción (Recomendado):**
- Usar reverse proxy (Nginx/Apache) con Let's Encrypt
- Implementar HSTS (HTTP Strict Transport Security)
- Configurar redirect automático HTTP → HTTPS

```python
# Forzar HTTPS en Flask
@app.before_request
def before_request():
    if not request.is_secure and not app.debug:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

**Impacto:** Elimina alerta "HTTP Only Site"  
**Prioridad:** 🟡 ALTA  
**Esfuerzo:** 30-60 minutos

---

#### 4. Actualizar Jenkinsfile con Imagen ZAP Correcta

**Cambio en `Jenkinsfile` línea 78:**

```groovy
// ANTES:
docker run --rm -v $(pwd)/zap-reports:/zap/reports owasp/zap2docker-stable \
    zap-full-scan.py -t http://host.docker.internal:5000 ...

// DESPUÉS:
docker run --rm -v $(pwd)/zap-reports:/zap/wrk:rw -t \
    ghcr.io/zaproxy/zaproxy:stable \
    zap-full-scan.py -t http://host.docker.internal:5000 \
    -r zap-full-report.html -J zap-full-report.json
```

**Impacto:** Pipeline de Jenkins funcionará correctamente  
**Prioridad:** 🟡 ALTA  
**Esfuerzo:** 2 minutos

---

### 🟢 MEDIAS (Mejoras Opcionales)

#### 5. Implementar Rate Limiting

**Librería:** Flask-Limiter

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    ...
```

**Beneficio:** Protección contra fuerza bruta  
**Prioridad:** 🟢 MEDIA

---

#### 6. Agregar Monitoreo de Seguridad

**Herramientas:**
- **Prometheus + Grafana:** Métricas de rendimiento
- **ELK Stack:** Análisis de logs
- **Sentry:** Tracking de errores

**Prioridad:** 🟢 MEDIA

---

#### 7. Implementar WAF (Web Application Firewall)

**Opciones:**
- ModSecurity (Open Source)
- AWS WAF
- Cloudflare

**Beneficio:** Capa adicional de protección  
**Prioridad:** 🟢 BAJA

---

## CONCLUSIONES

### Estado Actual de Seguridad

**Fortalezas:**
- ✅ Código fuente libre de vulnerabilidades (Bandit: 0 issues)
- ✅ Protecciones contra ataques comunes implementadas (SQL Injection, XSS, CSRF)
- ✅ Gestión segura de contraseñas con bcrypt
- ✅ Validación robusta de entrada de datos
- ✅ Configuración segura de sesiones
- ✅ Contenedor Docker con usuario no-root

**Debilidades Identificadas:**
- ⚠️ **10 vulnerabilidades críticas en dependencias** (requiere actualización inmediata)
- ⚠️ **6 headers de seguridad HTTP faltantes** (Medium risk)
- ⚠️ Falta HTTPS/TLS en configuración actual

### Riesgo Global

**Antes de Mitigaciones:** 🔴 ALTO  
**Después de Mitigaciones Recomendadas:** 🟢 BAJO

### Plan de Acción Inmediata

1. ✅ **Completado:** Análisis SAST con Bandit
2. ✅ **Completado:** Análisis de dependencias con Safety
3. ✅ **Completado:** Escaneo DAST con OWASP ZAP
4. 🔴 **PENDIENTE:** Actualizar dependencias vulnerables (15 min)
5. 🔴 **PENDIENTE:** Implementar headers de seguridad (5 min)
6. 🟡 **PENDIENTE:** Configurar HTTPS/TLS (60 min)
7. 🟡 **PENDIENTE:** Actualizar Jenkinsfile (2 min)

### Próximos Pasos

1. Aplicar actualizaciones de dependencias en `requirements.txt`
2. Implementar función `set_security_headers()` en `secure_app.py`
3. Configurar certificado SSL/TLS para producción
4. Re-ejecutar pruebas DAST para validar mitigaciones
5. Documentar cambios en SECURITY_REPORT.md

---

## ANEXOS

### A. Comandos de Verificación

```bash
# Ejecutar Bandit
python -m bandit -r src -f json -o bandit-report.json

# Ejecutar Safety
python -m safety check --file requirements.txt --output json

# Ejecutar OWASP ZAP
powershell -File .\scripts\run_zap_scan.ps1 -Target 'http://host.docker.internal:5000'

# Verificar actualizaciones de dependencias
pip list --outdated
```

### B. Referencias

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/3.0.x/security/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

### C. Historial de Cambios

| Fecha | Cambio | Responsable |
|-------|--------|-------------|
| 2025-11-26 | Análisis inicial de seguridad | DevSecOps Team |
| 2025-11-26 | Identificación de 10 CVEs en dependencias | Safety Scanner |
| 2025-11-26 | Escaneo DAST completo con ZAP | OWASP ZAP |
| 2025-11-26 | Documentación de mitigaciones | DevSecOps Team |

---

**Documento generado automáticamente el 26 de Noviembre de 2025**  
**Clasificación:** INTERNO - Uso DevSecOps  
**Versión:** 1.0
