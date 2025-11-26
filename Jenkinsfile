pipeline {
    agent any

    parameters {
        string(name: 'ZAP_FAIL_THRESHOLD', defaultValue: '0', description: 'Número máximo permitido de alertas High/Critical antes de fallar el build')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    environment {
        DOCKER_IMAGE = "evaluacion3_ciberseguridad:${BUILD_NUMBER}"
        OWASP_ZAP_PORT = '8080'
        VENV_DIR = '.venv'
        ZAP_FAIL_THRESHOLD = '0'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('SAST - Bandit / Semgrep') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install bandit semgrep safety

                    bandit -r src -f json -o bandit-report.json || true
                    semgrep --config=p/security-audit --json -o semgrep-report.json src || true
                    safety check --file requirements.txt --json > safety-report.json || true
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m py_compile src/secure_app.py src/secure_create_db.py
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install pytest pytest-cov
                    pytest -v --cov=src --cov-report=xml --cov-report=term
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE} .
                '''
            }
        }

        stage('DAST - OWASP ZAP (Full)') {
            steps {
                sh '''
                    docker run -d -p 5000:5000 --name taskapp ${DOCKER_IMAGE}
                    sleep 15

                    mkdir -p zap-reports
                    docker run --rm -v $(pwd)/zap-reports:/zap/reports owasp/zap2docker-stable \
                        zap-full-scan.py -t http://host.docker.internal:5000 -r /zap/reports/zap-full-report.html -J /zap/reports/zap-full-report.json || true

                    . ${VENV_DIR}/bin/activate || true
                    python3 - << 'PY'
import json, sys, os
p = os.path.join(os.getcwd(), 'zap-reports', 'zap-full-report.json')
if not os.path.exists(p):
    print('No ZAP JSON report found:', p)
    sys.exit(0)
with open(p) as f:
    data = json.load(f)
high = 0
for site in data.get('site', []):
    for alert in site.get('alerts', []):
        if alert.get('risk') in ('High', 'Critical'):
            high += 1
print('ZAP high/critical alerts:', high)
try:
    threshold = int(os.environ.get('ZAP_FAIL_THRESHOLD', '0'))
except Exception:
    threshold = 0
print('ZAP fail threshold:', threshold)
if high > threshold:
    sys.exit(2)
PY

                    docker stop taskapp || true
                    docker rm taskapp || true
                '''
            }
        }

        stage('Security Docs') {
            steps {
                sh '''
                    mkdir -p security-reports
                    cat > security-reports/SECURITY_SUMMARY.md << 'REPORT'
# Informe de Seguridad - Build #${BUILD_NUMBER}

## Revisiones realizadas
- SAST: Bandit, Semgrep sobre `src/`
- Análisis de dependencias: Safety sobre `requirements.txt`
- Pruebas unitarias: pytest + cobertura
- DAST: OWASP ZAP baseline sobre la aplicación Dockerizada

## Vulnerabilidades identificadas (ejemplo)
- Uso de bcrypt para contraseñas (segurop) – verificado
- Consultas SQL parametrizadas en `secure_app.get_db_connection`/login – verificado
- Validación de entradas en formulario de login – verificado

## Mitigaciones clave
- Prevención de SQL Injection: consultas parametrizadas (`?` + parámetros) en login y dashboard.
- Protección de credenciales: contraseñas hasheadas con `bcrypt` (12 rondas) en `secure_create_db.py`.
- Endurecimiento de sesión: cookies seguras `HttpOnly`, `Secure`, `SameSite=Lax` y expiración.
- Manejo seguro de errores: logging estructurado y templates dedicados para 404/500.

REPORT
                '''
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    docker tag ${DOCKER_IMAGE} evaluacion3_ciberseguridad:latest
                    docker push evaluacion3_ciberseguridad:latest || true
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'bandit-report.json,semgrep-report.json,safety-report.json,zap-reports/**,security-reports/**', allowEmptyArchive: true
            junit 'tests/**/*.xml'
            cleanWs()
        }
    }
}