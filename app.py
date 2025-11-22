from flask import Flask, request, jsonify, send_file
from psycopg2 import connect, extras
import bcrypt

app = Flask(__name__)

# --- BASE DE DATOS ---
host = 'localhost'
port = 5432
dbname = 'proyecto_mixy'
username = 'postgres'
password = '123456'


def get_connection():
    return connect(host=host, port=port, dbname=dbname, user=username, password=password)


# ----------------------------------------
# RUTA PRINCIPAL
# ----------------------------------------

@app.route('/')
def inicio():
    return send_file('templates/index.html')


# ----------------------------------------
# REGISTRO (COINCIDE CON /api/registro)
# ----------------------------------------
@app.post('/api/registro')
def create_user():
    data = request.get_json()

    nombre = data['nombre']
    apellido = data['apellido']
    correo = data['correo']
    nacimiento = data['nacimiento']

    # encriptar contraseña
    password_plano = data['password'].encode('utf-8')
    password_hash = bcrypt.hashpw(password_plano, bcrypt.gensalt())

    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    try:
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, correo, nacimiento, password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nombre, apellido, correo;
        """, (nombre, apellido, correo, nacimiento, password_hash))

        nuevo_usuario = cur.fetchone()
        conn.commit()

        return jsonify({"ok": True, "usuario": nuevo_usuario}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"ok": False, "mensaje": "Error registrando usuario"}), 400
    
    finally:
        cur.close()
        conn.close()


# ----------------------------------------
# LOGIN (COINCIDE CON /api/login)
# ----------------------------------------
@app.post('/api/login')
def login():
    data = request.get_json()

    correo = data['correo']
    password = data['password'].encode('utf-8')

    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    try:
        cur.execute('SELECT * FROM usuarios WHERE correo = %s;', (correo,))
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({"ok": False, "error": "Correo no registrado"}), 404

        password_guardada = usuario['password'].tobytes()  # PostgreSQL BYTEA → bytes

        if not bcrypt.checkpw(password, password_guardada):
            return jsonify({"ok": False, "error": "Contraseña incorrecta"}), 401

        return jsonify({"ok": True, "mensaje": "Inicio de sesión exitoso"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
