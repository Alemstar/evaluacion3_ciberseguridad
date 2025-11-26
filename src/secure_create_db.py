import sqlite3
import bcrypt
import os

# Conexión a base de datos
conn = sqlite3.connect('database.db')
c = conn.cursor()

def hash_password(password):
    """Hash seguro con bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')

# Crear tabla de usuarios con campos adicionales de seguridad
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
''')

# Crear tabla de tareas
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
''')

# Crear tabla de auditoría
c.execute('''
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Insertar usuarios de prueba con contraseñas hasheadas de forma idempotente
admin_password = hash_password('AdminPassword123!')
user_password = hash_password('UserPassword123!')

existing_users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]

if existing_users == 0:
    c.execute('''
    INSERT INTO users (username, password, role) VALUES
    (?, ?, 'admin'),
    (?, ?, 'user')
    ''', ('admin', admin_password, 'user', user_password))

    print("✅ Base de datos creada correctamente")
    print(f"   - Usuario admin hasheado con bcrypt")
    print(f"   - Usuario user hasheado con bcrypt")
    print(f"   - Tablas de auditoría implementadas")
else:
    print("ℹ️ Usuarios iniciales ya existen, no se vuelven a insertar")

conn.commit()
conn.close()