from flask import Flask, request, jsonify, send_file, session, redirect, url_for
from psycopg2 import connect, extras, sql, Binary
import bcrypt
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
# Cambia esto en producción por una variable de entorno segura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cambia_esto_por_una_clave_muy_segura")

# Parámetros de conexión (ajusta según tu entorno)
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'proyecto_mixy'
DB_USER = 'postgres'
DB_PASS = '123456'


def get_connection():
    return connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)


# ---------- RUTAS PÚBLICAS ----------

# Si estás probando rapido localmente con el index que subiste, puedes usar la ruta directa:
# Nota: archivo subido en el entorno: /mnt/data/index.html
@app.route('/')
def inicio():
    # Si moviste index.html a templates/index.html usa send_file("templates/index.html")
    # Si quieres usar el archivo que subiste temporalmente:
    uploaded_path = "/mnt/data/index.html"
    if os.path.exists(uploaded_path):
        return send_file(uploaded_path)
    # fallback si no existe el archivo subido
    return send_file('templates/index.html')


@app.route('/dashboard.html')
def dashboard_public():
    # página protegida: si no hay sesión redirige al login
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    # si existe, servimos el dashboard
    return send_file('templates/dashboard.html')


# ---------- API: REGISTRO ----------
@app.post('/api/registro')
def api_registro():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    correo = (data.get("correo") or "").strip().lower()
    nacimiento = data.get("nacimiento")  # formatea o valida si quieres
    password_plain = (data.get("password") or "").strip()

    if not (nombre and apellido and correo and password_plain):
        return jsonify({"ok": False, "mensaje": "Faltan campos obligatorios"}), 400

    # Hash de contraseña con bcrypt
    password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt())

    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        # prevenir duplicados por correo
        cur.execute('SELECT id FROM usuarios WHERE correo = %s', (correo,))
        if cur.fetchone():
            return jsonify({"ok": False, "mensaje": "El correo ya está registrado"}), 409

        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, correo, nacimiento, password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nombre, apellido, correo;
        """, (nombre, apellido, correo, nacimiento, Binary(password_hash)))

        nuevo = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "usuario": nuevo}), 201

    except Exception as e:
        app.logger.exception("Error al registrar usuario")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ---------- API: LOGIN ----------
@app.post('/api/login')
def api_login():
    data = request.get_json(silent=True) or {}
    correo = (data.get("correo") or "").strip().lower()
    password_plain = (data.get("password") or "").strip()

    if not (correo and password_plain):
        return jsonify({"ok": False, "mensaje": "Correo y contraseña son requeridos"}), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
        user = cur.fetchone()
        if not user:
            return jsonify({"ok": False, "mensaje": "Correo o contraseña incorrectos"}), 401

        # password almacenado puede venir como memoryview/bytes/text; normalizamos a bytes
        password_db = user.get("password")
        password_db_bytes = None

        # distintos tipos posibles según cómo esté guardado:
        if password_db is None:
            return jsonify({"ok": False, "mensaje": "Error de autenticación"}), 500

        # Si viene como memoryview (BYTEA), convertimos a bytes
        try:
            # memoryview o bytea -> tobytes() o bytes()
            if hasattr(password_db, "tobytes"):
                password_db_bytes = password_db.tobytes()
            elif isinstance(password_db, (bytes, bytearray)):
                password_db_bytes = bytes(password_db)
            elif isinstance(password_db, memoryview):
                password_db_bytes = password_db.tobytes()
            else:
                # si está en texto (varchar/text) lo convertimos a bytes
                password_db_bytes = str(password_db).encode("utf-8")
        except Exception:
            password_db_bytes = str(password_db).encode("utf-8")

        # Verificamos con bcrypt
        if bcrypt.checkpw(password_plain.encode("utf-8"), password_db_bytes):
            # login correcto -> guardamos sesión
            session["usuario_id"] = user["id"]
            session["usuario_correo"] = user["correo"]
            return jsonify({"ok": True, "mensaje": "Inicio de sesión exitoso"}), 200

        # también permitir comparacion directa (solo si quieras soportar contraseñas no encriptadas
        # descomentando la siguiente línea — NO recomendado en producción)
        # if password_plain == str(user.get("password")): ...

        return jsonify({"ok": False, "mensaje": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        app.logger.exception("Error en login")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ---------- LOGOUT ----------
@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for("inicio"))


# ---------- PROTECCIÓN SIMPLE (ejemplo de uso si haces APIs privadas) ----------
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return jsonify({"ok": False, "mensaje": "No autorizado"}), 401
        return fn(*args, **kwargs)
    return wrapper


# Ejemplo de API privada
@app.get('/api/perfil')
@login_required
def perfil():
    return jsonify({"ok": True, "usuario_id": session.get("usuario_id"), "correo": session.get("usuario_correo")})


if __name__ == '__main__':
    app.run(debug=True)
