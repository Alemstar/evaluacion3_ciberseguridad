"""
Implementación de Headers de Seguridad HTTP
============================================

Este archivo muestra cómo agregar la función set_security_headers() 
a secure_app.py para mitigar las advertencias de OWASP ZAP.

Agrega este código después de la configuración de la app y antes de las rutas.
"""

from flask import Flask, response

app = Flask(__name__)

# ... configuración existente ...

@app.after_request
def set_security_headers(response):
    """
    Configura headers de seguridad HTTP para proteger contra ataques comunes.
    
    Mitiga las siguientes alertas de OWASP ZAP:
    - 10020: Missing Anti-clickjacking Header
    - 10021: X-Content-Type-Options Header Missing
    - 10038: Content Security Policy (CSP) Header Not Set
    - 10063: Permissions Policy Header Not Set
    - 90004: Insufficient Site Isolation Against Spectre Vulnerability
    
    Returns:
        response: Objeto de respuesta Flask con headers de seguridad agregados
    """
    
    # 1. Anti-clickjacking - Previene que la página sea embebida en iframe
    response.headers['X-Frame-Options'] = 'DENY'
    
    # 2. Prevenir MIME sniffing - Fuerza al navegador a respetar Content-Type
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 3. XSS Protection (Legacy pero útil para navegadores antiguos)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 4. Content Security Policy - Política estricta de contenido
    # Permite solo recursos del mismo origen excepto estilos inline necesarios para Bootstrap
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "                    # Por defecto solo mismo origen
        "script-src 'self'; "                      # Scripts solo del mismo origen
        "style-src 'self' 'unsafe-inline'; "      # Estilos del mismo origen + inline (para Bootstrap)
        "img-src 'self' data:; "                   # Imágenes del mismo origen + data URIs
        "font-src 'self'; "                        # Fuentes del mismo origen
        "connect-src 'self'; "                     # XHR/WebSocket solo mismo origen
        "frame-ancestors 'none'; "                 # No permitir ser embebido en frames
        "base-uri 'self'; "                        # Restringir <base> tag
        "form-action 'self'; "                     # Forms solo pueden enviarse al mismo origen
        "upgrade-insecure-requests"                # Actualizar HTTP a HTTPS automáticamente
    )
    
    # 5. Permissions Policy - Restricción de APIs del navegador
    # Deshabilita funciones sensibles del navegador
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "          # Sin geolocalización
        "microphone=(), "           # Sin micrófono
        "camera=(), "               # Sin cámara
        "payment=(), "              # Sin API de pagos
        "usb=(), "                  # Sin USB
        "magnetometer=(), "         # Sin magnetómetro
        "gyroscope=(), "            # Sin giroscopio
        "accelerometer=(), "        # Sin acelerómetro
        "ambient-light-sensor=(), " # Sin sensor de luz
        "autoplay=(), "             # Sin autoplay de media
        "encrypted-media=(), "      # Sin DRM
        "fullscreen=(self), "       # Fullscreen solo en mismo origen
        "picture-in-picture=()"     # Sin picture-in-picture
    )
    
    # 6. Protección contra vulnerabilidades Spectre
    # Aislamiento de origen cruzado
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    
    # 7. Referrer Policy - Controla información enviada en header Referer
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # 8. Strict-Transport-Security (HSTS) - Solo para producción con HTTPS
    # Descomentar cuando HTTPS esté configurado:
    # if not app.debug and request.is_secure:
    #     response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    return response


# ALTERNATIVA: Configuración menos estricta para desarrollo
@app.after_request
def set_security_headers_dev(response):
    """
    Versión menos estricta de headers para desarrollo.
    Permite recursos externos comunes (CDNs, etc.)
    """
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Permite iframe del mismo origen
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # CSP más permisivo para desarrollo
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' https:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'"
    )
    
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    
    return response


# EJEMPLO DE USO EN secure_app.py:
"""
from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
# ... otros imports ...

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,
    WTF_CSRF_ENABLED=True
)

# AGREGAR AQUÍ LA FUNCIÓN set_security_headers()
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none'"
    )
    response.headers['Permissions-Policy'] = (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    )
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ... resto del código ...

@app.route('/')
def index():
    return render_template('login.html')

# ... más rutas ...
"""
