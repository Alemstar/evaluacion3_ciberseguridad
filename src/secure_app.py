from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import bcrypt
import sys

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv('SECRET_KEY')
if not secret_key and os.getenv('FLASK_ENV') not in ('development', 'testing'):
    raise RuntimeError('SECRET_KEY must be set in environment for non-development environments')

app.secret_key = secret_key or os.urandom(32)

# Configuración segura de sesiones
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,
    WTF_CSRF_ENABLED=True
)

# Configurar logging (para Docker usar StreamHandler en lugar de archivo)
if os.getenv('DOCKER_ENV') == 'true':
    log_handler = logging.StreamHandler(sys.stdout)
else:
    log_handler = RotatingFileHandler('app.log', maxBytes=10485760, backupCount=10)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

def get_db_connection():
    """Obtener conexión segura a base de datos"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash seguro usando bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verificación segura de contraseña"""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))
    except Exception as e:
        app.logger.error(f"Error verificando contraseña: {str(e)}")
        return False

class LoginForm(FlaskForm):
    """Formulario de login con validaciones"""
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=3, max=50),
        validators.Regexp('^[A-Za-z0-9_]+$',
            message='Solo caracteres alfanuméricos y underscore permitidos')
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=128)
    ])

@app.route('/')
def index():
    return 'Bienvenido a la Aplicación de Gestión de Tareas - Task Manager'

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint de login seguro"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            conn = get_db_connection()
            # CONSULTA PARAMETRIZADA - Previene SQL Injection
            query = "SELECT * FROM users WHERE username = ?"
            user = conn.execute(query, (username,)).fetchone()
            conn.close()
            
            if user and verify_password(password, user['password']):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                app.logger.info(f"Login exitoso: {username}")
                return redirect(url_for('dashboard'))
            else:
                app.logger.warning(f"Intento de login fallido: {username}")
                flash('Credenciales inválidas', 'error')
        
        except Exception as e:
            app.logger.error(f"Error en login: {str(e)}", exc_info=True)
            flash('Error en el servidor. Intente más tarde.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    """Dashboard seguro - Solo usuarios autenticados"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        username = session.get('username', 'Usuario')
        
        conn = get_db_connection()
        # CONSULTA PARAMETRIZADA
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        conn.close()
        
        return render_template('dashboard.html', 
            tasks=tasks, 
            username=username
        )
    
    except Exception as e:
        app.logger.error(f"Error en dashboard: {str(e)}", exc_info=True)
        flash('Error al cargar dashboard', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout seguro - Limpiar sesión"""
    username = session.get('username', 'Usuario')
    session.clear()
    app.logger.info(f"Logout: {username}")
    flash('Ha cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    app.logger.warning(f"404 Error: {request.path}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    app.logger.error(f"500 Error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # NO usar debug=True en producción
    app.run(
        host='127.0.0.1',  # No exponer públicamente sin HTTPS
        port=5000,
        debug=False  # CRÍTICO: False en producción
    )

