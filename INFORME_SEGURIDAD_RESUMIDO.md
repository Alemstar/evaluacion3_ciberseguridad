# INFORME DE PRUEBAS DE SEGURIDAD

**Proyecto:** evaluacion3_ciberseguridad  
**Fecha:** 26 de Noviembre de 2025

---

## 1. RESUMEN EJECUTIVO

Se realizaron pruebas de seguridad exhaustivas sobre la aplicación Flask utilizando herramientas SAST, análisis de dependencias y DAST.

### Métricas Generales
- **Líneas de código analizadas:** 192
- **Vulnerabilidades en código fuente:** 0
- **Vulnerabilidades en dependencias:** 10 (críticas)
- **Alertas DAST (Medium):** 6
- **Alertas DAST (High/Critical):** 0

---

## 2. HERRAMIENTAS UTILIZADAS

| Herramienta | Tipo | Resultado |
|-------------|------|-----------|
| **Bandit v1.8.0** | SAST | ✅ 0 vulnerabilidades |
| **Safety v3.7.0** | Dependencias | ⚠️ 10 vulnerabilidades |
| **OWASP ZAP v2.16.1** | DAST | ⚠️ 6 alertas Medium |

---

## 3. VULNERABILIDADES ENCONTRADAS

### 3.1 Código Fuente (Bandit)
**Resultado:** ✅ **EXCELENTE - 0 vulnerabilidades detectadas**

### 3.2 Dependencias (Safety)

| Paquete | Versión Actual | CVEs | Versión Segura |
|---------|----------------|------|----------------|
| **gunicorn** | 21.2.0 | 2 | 23.0.0 |
| **Jinja2** | 3.1.4 | 3 | 3.1.6 |
| **Werkzeug** | 3.0.0 | 5 | 3.1.3 |

**Vulnerabilidades Críticas Identificadas:**
- **CVE-2024-1135, CVE-2024-6827:** HTTP Request Smuggling en Gunicorn
- **CVE-2024-56201, CVE-2025-27516, CVE-2024-56326:** RCE y bypass del sandbox en Jinja2
- **CVE-2024-49767, CVE-2023-46136:** DoS y agotamiento de recursos en Werkzeug
- **CVE-2024-49766, CVE-2024-34069:** Path Traversal y debugger vulnerable en Werkzeug

### 3.3 Análisis Dinámico (OWASP ZAP)

**URLs analizadas:** 5 | **Pruebas ejecutadas:** 139 | **Exitosas:** 133 (95.7%)

**Alertas Medium (6):**
1. Missing Anti-clickjacking Header (X-Frame-Options)
2. X-Content-Type-Options Header Missing
3. Content Security Policy (CSP) Header Not Set
4. Permissions Policy Header Not Set
5. HTTP Only Site (sin HTTPS)
6. Insufficient Site Isolation Against Spectre

**Pruebas Exitosas (133):** ✅ SQL Injection, XSS, CSRF, Path Traversal, RCE, Session Management, Command Injection, XXE, SSRF, Template Injection

---

## 4. MITIGACIONES IMPLEMENTADAS

### 4.1 Prevención de SQL Injection ✅
```python
# Consultas parametrizadas
cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
```

### 4.2 Protección de Contraseñas ✅
```python
# bcrypt con 12 rondas
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode(), salt)
```

### 4.3 Sesiones Seguras ✅
```python
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
```

### 4.4 Validación de Entrada ✅
```python
username = StringField('Username', [
    validators.DataRequired(),
    validators.Regexp('^[A-Za-z0-9_]+$')
])
```

### 4.5 Protección CSRF ✅
```python
app.config['WTF_CSRF_ENABLED'] = True
```

---

## 5. RECOMENDACIONES

### 5.1 Críticas (Implementar Inmediatamente)

**Actualizar Dependencias Vulnerables:**
```python
# requirements.txt actualizado
Flask==3.0.0
Werkzeug==3.1.3     # Actualizado de 3.0.0
Jinja2==3.1.6       # Actualizado de 3.1.4
gunicorn==23.0.0    # Actualizado de 21.2.0
```

**Implementar Headers de Seguridad HTTP:**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Permissions-Policy'] = "geolocation=(), camera=()"
    return response
```

### 5.2 Altas (Antes de Producción)
- Implementar HTTPS/TLS con certificado válido
- Configurar HSTS (HTTP Strict Transport Security)

---

## 6. CONCLUSIONES

### Estado de Seguridad

| Aspecto | Estado | Comentario |
|---------|--------|------------|
| **Código Fuente** | ✅ Seguro | Sin vulnerabilidades detectadas |
| **Dependencias** | ⚠️ Requiere Acción | 10 CVEs críticos |
| **Configuración** | ⚠️ Mejorable | 6 headers faltantes |
| **Protecciones Implementadas** | ✅ Excelentes | SQL Injection, XSS, CSRF protegidos |

### Riesgo Global
- **Antes de mitigaciones:** 🔴 ALTO
- **Después de mitigaciones:** 🟢 BAJO

### Plan de Acción (25 minutos)
1. Actualizar dependencias (15 min)
2. Agregar headers HTTP (5 min)
3. Validar con ZAP (5 min)

---

**Preparado por:** DevSecOps Team  
**Fecha:** 26 de Noviembre de 2025  
**Versión:** 1.0 (Resumida)
