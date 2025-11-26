# Informe de Seguridad

## Alcance

Aplicación Flask `secure_app.py` y script de base de datos `secure_create_db.py`, construidos y desplegados mediante Docker y pipeline de Jenkins.

## Pipeline CI/CD de Seguridad

- **Construcción**: creación de entorno Python, compilación de `src/secure_app.py` y `src/secure_create_db.py`, build de imagen Docker.
- **Pruebas**: ejecución de `pytest` con cobertura sobre `src/`.
- **Despliegue**: construcción y publicación de imagen Docker para rama `main`.
- **SAST**: Bandit y Semgrep sobre el código en `src/`.
- **Análisis de dependencias**: Safety sobre `requirements.txt`.
- **DAST**: escaneo baseline de OWASP ZAP contra la aplicación dockerizada.

## Revisiones de Seguridad Realizadas

1. **Revisión manual del código**
   - Archivo `src/secure_app.py`:
     - Comprobación de uso de consultas SQL parametrizadas.
     - Verificación de hashing de contraseñas con `bcrypt`.
     - Validación de formularios y configuración de sesiones.
   - Archivo `src/secure_create_db.py`:
     - Creación de tablas `users`, `tasks`, `audit_log`.
     - Inserción de usuarios iniciales con contraseñas hasheadas.

2. **SAST automatizado**
   - `bandit -r src` para detectar patrones de código inseguros.
   - `semgrep --config=p/security-audit src` para reglas de seguridad adicionales.

3. **Análisis de dependencias**
   - `safety check --file requirements.txt` para vulnerabilidades conocidas en librerías.

4. **Pruebas unitarias**
   - `pytest` sobre `tests/` (lista para ampliar casos de login, BD y permisos).

5. **DAST / pruebas dinámicas**
   - OWASP ZAP baseline contra la aplicación en Docker, comprobando rutas principales (`/`, `/login`, `/dashboard`).

## Vulnerabilidades Revisadas y Mitigaciones

### 1. SQL Injection (CWE-89)

- **Riesgo**: uso inseguro de concatenación de strings en consultas SQL.
- **Revisión**:
  - Login: `SELECT * FROM users WHERE username = ?`.
  - Dashboard: `SELECT * FROM tasks WHERE user_id = ?`.
- **Mitigación**:
  - Todas las consultas usan placeholders `?` y parámetros separados.
  - Los datos de usuario nunca se interpolan directamente en SQL.

### 2. Gestión de contraseñas (CWE-256 / CWE-327)

- **Riesgo**: almacenamiento de contraseñas en texto plano o con hashing débil.
- **Revisión**:
  - `secure_create_db.py` usa `bcrypt.gensalt(rounds=12)`.
  - `secure_app.hash_password` y `secure_app.verify_password` usan `bcrypt`.
- **Mitigación**:
  - Contraseñas nunca se almacenan en claro.
  - Factor de coste suficientemente alto (12 rondas) para dificultar ataques de fuerza bruta.

### 3. Validación de entrada (CWE-20)

- **Riesgo**: parámetros sin validar que pueden provocar inyecciones o errores.
- **Revisión**:
  - Formulario `LoginForm` con validaciones de longitud y regex para `username`.
  - `password` con longitud mínima y máxima.
- **Mitigación**:
  - Rechazo de entradas con caracteres no permitidos.
  - Reducción de vectores de inyección y errores de tipo.

### 4. Gestión de sesión (CWE-384)

- **Riesgo**: robo o fijación de sesión, cookies inseguras.
- **Revisión**:
  - `SESSION_COOKIE_SECURE=True`.
  - `SESSION_COOKIE_HTTPONLY=True`.
  - `SESSION_COOKIE_SAMESITE='Lax'`.
  - Tiempo de vida limitado de sesión.
- **Mitigación**:
  - Cookies protegidas frente a acceso por JS y envío a dominios no esperados.
  - Sesiones expiran de forma controlada.

### 5. Gestión de SECRET_KEY

- **Riesgo**: clave de sesión generada de forma no controlada en producción.
- **Revisión y cambio aplicado**:
  - Antes: `SECRET_KEY` podía generarse aleatoriamente en cada arranque.
  - Ahora: en entornos no desarrollo ni pruebas, se exige `SECRET_KEY` por entorno; de lo contrario se lanza excepción.
- **Mitigación**:
  - Clave consistente y gestionada de forma segura en producción.

### 6. Idempotencia en creación de usuarios iniciales

- **Riesgo**: errores por `UNIQUE` al ejecutar varias veces `secure_create_db.py`.
- **Revisión y cambio aplicado**:
  - Se comprueba número de usuarios existentes antes de insertar.
- **Mitigación**:
  - Script idempotente, sin afectar al modelo de seguridad.

## Conclusiones

- El pipeline de Jenkins realiza revisiones de seguridad continuas en las fases de construcción, pruebas y despliegue.
- Las vulnerabilidades típicas de aplicaciones web (SQLi, gestión de contraseñas, sesiones inseguras, entradas no validadas) están mitigadas en el código actual.
- Los cambios recientes endurecen la gestión de `SECRET_KEY` y mejoran la robustez del script de base de datos.
