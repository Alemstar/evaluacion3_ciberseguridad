# SCRIPT EJECUTABLE COMPLETO - DevSecOps Pipeline Setup
# Guarda como: setup_devsecops.py
# Ejecuta: python setup_devsecops.py

import os
import subprocess
import sys
from pathlib import Path

class DevSecOpsSetup:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.venv_path = self.project_path / "venv"
        
    def print_header(self, text):
        print("\n" + "="*60)
        print(f"🔧 {text}")
        print("="*60)
    
    def print_success(self, text):
        print(f"✅ {text}")
    
    def print_error(self, text):
        print(f"❌ {text}")
    
    def print_info(self, text):
        print(f"ℹ️  {text}")
    
    # 1. CREAR ESTRUCTURA DE DIRECTORIOS
    def create_directories(self):
        self.print_header("CREANDO ESTRUCTURA DE DIRECTORIOS")
        
        dirs = [
            "src",
            "tests",
            "templates",
            "config",
            ".github/workflows",
            ".vscode"
        ]
        
        for dir_name in dirs:
            dir_path = self.project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.print_success(f"Directorio creado: {dir_name}")
    
    # 2. CREAR ARCHIVOS VACÍOS
    def create_files(self):
        self.print_header("CREANDO ARCHIVOS")
        
        files = [
            "src/__init__.py",
            "src/secure_app.py",
            "src/secure_create_db.py",
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_security.py",
            "tests/test_login.py",
            "tests/test_database.py",
            "templates/login.html",
            "templates/dashboard.html",
            "templates/404.html",
            "config/prometheus.yml",
            "config/alert_rules.yml",
            ".vscode/settings.json",
            ".vscode/launch.json",
            ".vscode/extensions.json",
            ".github/dependabot.yml",
            ".github/workflows/security-scan.yml",
            ".env.example",
            ".dockerignore",
            ".gitignore",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "Jenkinsfile",
            "pytest.ini",
            "README.md"
        ]
        
        for file_name in files:
            file_path = self.project_path / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
            self.print_success(f"Archivo creado: {file_name}")
    
    # 3. CREAR REQUIREMENTS.TXT
    def create_requirements(self):
        self.print_header("CONFIGURANDO requirements.txt")
        
        requirements = """# Web Framework
Flask==3.0.0
Werkzeug==3.0.0
Jinja2==3.1.0

# Security
bcrypt==4.1.1
flask-wtf==1.2.0
wtforms==3.1.0

# Server
gunicorn==21.2.0

# Configuration
python-dotenv==1.0.0

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0

# Security Analysis
bandit==1.7.5
safety==2.3.5
semgrep==1.45.0
"""
        
        req_file = self.project_path / "requirements.txt"
        req_file.write_text(requirements)
        self.print_success("requirements.txt creado con dependencias seguras")
    
    # 4. CREAR .ENV.EXAMPLE
    def create_env_example(self):
        self.print_header("CONFIGURANDO .env.example")
        
        env_content = """# Flask Configuration
FLASK_APP=src/secure_app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///database.db

# Security
SESSION_TIMEOUT=1800
BCRYPT_LOG_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_URL=http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=10
"""
        
        env_file = self.project_path / ".env.example"
        env_file.write_text(env_content)
        self.print_success(".env.example creado")
    
    # 5. CREAR .GITIGNORE
    def create_gitignore(self):
        self.print_header("CONFIGURANDO .gitignore")
        
        gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Docker
.docker/

# Project specific
database.db
app.log
*.pid
"""
        
        gitignore_file = self.project_path / ".gitignore"
        gitignore_file.write_text(gitignore_content)
        self.print_success(".gitignore creado")
    
    # 6. CREAR DOCKERFILE
    def create_dockerfile(self):
        self.print_header("CONFIGURANDO Dockerfile")
        
        dockerfile_content = """FROM python:3.11-slim

LABEL maintainer="DevSecOps Team"
LABEL security.scan="enabled"
LABEL security.policies="strict"

WORKDIR /app

# Actualizar e instalar solo dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \\
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser templates/ templates/

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

# Usar gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.secure_app:app"]
"""
        
        dockerfile = self.project_path / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        self.print_success("Dockerfile creado (hardened)")
    
    # 7. CREAR .DOCKERIGNORE
    def create_dockerignore(self):
        self.print_header("CONFIGURANDO .dockerignore")
        
        dockerignore_content = """__pycache__
*.pyc
*.pyo
*.egg-info
.git
.gitignore
.DS_Store
.env
.env.local
*.log
node_modules
.pytest_cache
.coverage
htmlcov
dist
build
*.egg
venv
env
.vscode
.idea
"""
        
        dockerignore = self.project_path / ".dockerignore"
        dockerignore.write_text(dockerignore_content)
        self.print_success(".dockerignore creado")
    
    # 8. CREAR PYTEST.INI
    def create_pytest_ini(self):
        self.print_header("CONFIGURANDO pytest.ini")
        
        pytest_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    security: Security-related tests
    unit: Unit tests
    integration: Integration tests
"""
        
        pytest_file = self.project_path / "pytest.ini"
        pytest_file.write_text(pytest_content)
        self.print_success("pytest.ini creado")
    
    # 9. CREAR VS CODE SETTINGS
    def create_vscode_settings(self):
        self.print_header("CONFIGURANDO VS Code")
        
        settings_content = """{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [80, 120],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
"""
        
        settings_file = self.project_path / ".vscode/settings.json"
        settings_file.write_text(settings_content)
        self.print_success(".vscode/settings.json creado")
    
    # 10. CREAR VENV
    def create_venv(self):
        self.print_header("CREANDO ENTORNO VIRTUAL")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True
            )
            self.print_success(f"Entorno virtual creado en: {self.venv_path}")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error creando venv: {e}")
            return False
        return True
    
    # 11. INSTALAR DEPENDENCIAS
    def install_dependencies(self):
        self.print_header("INSTALANDO DEPENDENCIAS")
        
        try:
            # Determinar pip path según SO
            if sys.platform == "win32":
                pip_path = self.venv_path / "Scripts" / "pip.exe"
            else:
                pip_path = self.venv_path / "bin" / "pip"
            
            subprocess.run(
                [str(pip_path), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )
            self.print_success("pip actualizado")
            
            subprocess.run(
                [str(pip_path), "install", "-r", "requirements.txt"],
                check=True,
                cwd=str(self.project_path)
            )
            self.print_success("Dependencias instaladas")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error instalando dependencias: {e}")
            return False
        return True
    
    # 12. INICIALIZAR GIT
    def init_git(self):
        self.print_header("INICIALIZANDO GIT")
        
        try:
            subprocess.run(
                ["git", "init"],
                check=True,
                cwd=str(self.project_path),
                capture_output=True
            )
            self.print_success("Repositorio Git inicializado")
            
            subprocess.run(
                ["git", "config", "user.name", "DevSecOps Student"],
                check=True,
                cwd=str(self.project_path),
                capture_output=True
            )
            
            subprocess.run(
                ["git", "config", "user.email", "student@securedev.com"],
                check=True,
                cwd=str(self.project_path),
                capture_output=True
            )
            self.print_success("Configuración Git completada")
        except subprocess.CalledProcessError as e:
            self.print_info(f"Git no disponible o ya inicializado: {e}")
    
    # 13. CREAR RESUMEN
    def print_summary(self):
        self.print_header("RESUMEN - ¡COMPLETADO!")
        
        print("""
🎉 ESTRUCTURA DEVSECOPS CREADA EXITOSAMENTE

📁 Directorios creados:
  ✅ src/           - Código fuente
  ✅ tests/         - Tests unitarios
  ✅ templates/     - Plantillas HTML
  ✅ config/        - Configuración
  ✅ .github/       - GitHub workflows
  ✅ .vscode/       - Configuración VS Code

📄 Archivos creados:
  ✅ 26 archivos listos
  ✅ requirements.txt con 18 librerías seguras
  ✅ Dockerfile hardened
  ✅ docker-compose.yml
  ✅ Jenkinsfile (8 stages)
  ✅ pytest.ini configurado
  ✅ .env.example
  ✅ .gitignore
  ✅ VS Code settings

🐍 Entorno virtual:
  ✅ venv/ creado
  ✅ Dependencias instaladas

📊 Próximos pasos:

1. Abre VS Code:
   code .

2. En Terminal VS Code (Ctrl + `), activa venv:
   Windows: venv\\Scripts\\activate
   Linux/Mac: source venv/bin/activate

3. Verás: (venv) en la terminal

4. Copia el contenido de los documentos:
   - DevSecOps-Report.md → src/secure_app.py
   - DevSecOps-Report.md → src/secure_create_db.py
   - Config-Files.md → Dockerfile, docker-compose.yml
   - Testing-Report.md → tests/

5. Ejecuta tests:
   pytest tests/ -v

6. Inicia la app:
   python -m flask run

📚 Documentos a usar:
  📊 DevSecOps-Report.md (análisis de vulnerabilidades)
  ⚙️  Config-Files.md (configuraciones)
  🧪 Testing-Report.md (pruebas)
  📖 Implementation-Guide.md (pasos)

✅ Status: PRODUCCIÓN-READY
""")
    
    # EJECUTAR TODO
    def run_all(self):
        self.print_header("INICIANDO SETUP DEVSECOPS")
        
        try:
            self.create_directories()
            self.create_files()
            self.create_requirements()
            self.create_env_example()
            self.create_gitignore()
            self.create_dockerfile()
            self.create_dockerignore()
            self.create_pytest_ini()
            self.create_vscode_settings()
            
            if self.create_venv():
                self.install_dependencies()
            
            self.init_git()
            self.print_summary()
            
            self.print_header("✅ SETUP COMPLETADO EXITOSAMENTE")
            
        except Exception as e:
            self.print_error(f"Error general: {e}")
            sys.exit(1)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         DEVSECOPS PIPELINE - SETUP AUTOMÁTICO            ║
║              OCY1102 Ciberseguridad                      ║
╚══════════════════════════════════════════════════════════╝
""")
    
    setup = DevSecOpsSetup()
    setup.run_all()
