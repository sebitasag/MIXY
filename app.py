from flask import Flask, request, jsonify, send_file, session, redirect, url_for
from psycopg2 import connect, extras, sql
import bcrypt
import os


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cambia_esto_por_una_clave_muy_segura")


# Parámetros de conexión
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'proyecto_mixy'
DB_USER = 'postgres'
DB_PASS = '123456'


ADMIN_PASSWORD = 'mixy0005'


def get_connection():
    return connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)


# ==================== RUTAS PÚBLICAS ====================


@app.route('/')
def inicio():
    if session.get("usuario_id"):
        return redirect(url_for("home"))
    return send_file('templates/index.html')


@app.route('/home')
def home():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    return send_file('templates/home.html')


@app.route('/library')
def library():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    return send_file('templates/library.html')


@app.route('/favorites')
def favorites():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    return send_file('templates/favorites.html')


@app.route('/search')
def search():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    return send_file('templates/search.html')


@app.route('/create-playlist')
def create_playlist_page():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    return send_file('templates/create-playlist.html')


@app.route('/admin')
def admin():
    if not session.get("usuario_id"):
        return redirect(url_for("inicio"))
    if not session.get("is_admin"):
        return redirect(url_for("home"))
    return send_file('templates/admin.html')


# ==================== API: REGISTRO ====================


@app.post('/api/registro')
def api_registro():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    correo = (data.get("correo") or "").strip().lower()
    nacimiento = data.get("nacimiento")
    password_plain = (data.get("password") or "").strip()

    if not (nombre and apellido and correo and password_plain):
        return jsonify({"ok": False, "mensaje": "Faltan campos obligatorios"}), 400

    password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute('SELECT id FROM usuarios WHERE correo = %s', (correo,))
        if cur.fetchone():
            return jsonify({"ok": False, "mensaje": "El correo ya está registrado"}), 409

        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, correo, nacimiento, password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nombre, apellido, correo;
        """, (nombre, apellido, correo, nacimiento, password_hash))
        
        nuevo = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "usuario": nuevo}), 201
    except Exception as e:
        app.logger.exception("Error al registrar usuario")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: LOGIN ====================


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

        password_db = user.get("password")
        
        if not password_db:
            return jsonify({"ok": False, "mensaje": "Error de autenticación"}), 500

        if bcrypt.checkpw(password_plain.encode("utf-8"), password_db.encode("utf-8")):
            session["usuario_id"] = user["id"]
            session["usuario_correo"] = user["correo"]
            session["usuario_nombre"] = user["nombre"]
            return jsonify({"ok": True, "mensaje": "Inicio de sesión exitoso"}), 200

        return jsonify({"ok": False, "mensaje": "Correo o contraseña incorrectos"}), 401

    except Exception as e:
        app.logger.exception("Error en login")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: ADMIN ====================


@app.post('/api/admin/verify')
def verify_admin():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    
    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({"ok": True, "mensaje": "Acceso concedido"})
    return jsonify({"ok": False, "mensaje": "Contraseña incorrecta"}), 401


@app.post('/api/admin/upload/album')
def upload_album():
    if not session.get("is_admin"):
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 401
    
    from werkzeug.utils import secure_filename
    UPLOAD_FOLDER = 'static/uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    titulo = request.form.get('titulo')
    artista_id = request.form.get('artista_id')
    fecha_lanzamiento = request.form.get('fecha_lanzamiento')
    genero_id = request.form.get('genero_id')
    
    cover_url = None
    if 'cover' in request.files:
        cover = request.files['cover']
        if cover.filename:
            filename = secure_filename(cover.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            cover.save(filepath)
            cover_url = f'/static/uploads/{filename}'
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO albumes (titulo, artista_id, fecha_lanzamiento, genero_id, cover_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (titulo, artista_id, fecha_lanzamiento, genero_id, cover_url))
        album = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "album": album}), 201
    except Exception as e:
        app.logger.exception("Error al crear álbum")
        return jsonify({"ok": False, "mensaje": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/admin/upload/cancion')
def upload_cancion_admin():
    if not session.get("is_admin"):
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 401
    
    from werkzeug.utils import secure_filename
    UPLOAD_FOLDER = 'static/uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    titulo = request.form.get('titulo')
    artista_id = request.form.get('artista_id')
    album_id = request.form.get('album_id')
    duracion = request.form.get('duracion_segundos', 0)
    
    archivo_url = None
    if 'archivo' in request.files:
        archivo = request.files['archivo']
        if archivo.filename:
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            archivo.save(filepath)
            archivo_url = f'/static/uploads/{filename}'
    
    cover_url = None
    if 'cover' in request.files:
        cover = request.files['cover']
        if cover.filename:
            filename = secure_filename(cover.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            cover.save(filepath)
            cover_url = f'/static/uploads/{filename}'
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO canciones (titulo, artista_id, album_id, duracion_segundos, archivo_url, cover_url, reproducciones)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
            RETURNING *
        """, (titulo, artista_id, album_id if album_id else None, duracion, archivo_url, cover_url))
        cancion = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "cancion": cancion}), 201
    except Exception as e:
        app.logger.exception("Error al subir canción")
        return jsonify({"ok": False, "mensaje": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/admin/upload/artista')
def upload_artista():
    if not session.get("is_admin"):
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 401
    
    from werkzeug.utils import secure_filename
    UPLOAD_FOLDER = 'static/uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    nombre_artista = request.form.get('nombre_artista')
    verificado = request.form.get('verificado') == 'true'
    
    avatar_url = None
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar.filename:
            filename = secure_filename(avatar.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            avatar.save(filepath)
            avatar_url = f'/static/uploads/{filename}'
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO artistas (nombre_artista, verificado, avatar_url)
            VALUES (%s, %s, %s)
            RETURNING *
        """, (nombre_artista, verificado, avatar_url))
        artista = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "artista": artista}), 201
    except Exception as e:
        app.logger.exception("Error al crear artista")
        return jsonify({"ok": False, "mensaje": str(e)}), 500
    finally:
        cur.close()
        conn.close()


# ==================== LOGOUT ====================


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for("inicio"))


# ==================== PROTECCIÓN ====================


def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return jsonify({"ok": False, "mensaje": "No autorizado"}), 401
        return fn(*args, **kwargs)
    return wrapper


# ==================== API: PERFIL ====================


@app.get('/api/perfil')
@login_required
def perfil():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute('SELECT id, nombre, apellido, correo, nacimiento FROM usuarios WHERE id = %s', 
                   (session.get("usuario_id"),))
        usuario = cur.fetchone()
        return jsonify({
            "ok": True, 
            "usuario_id": usuario["id"],
            "correo": usuario["correo"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"]
        })
    except Exception as e:
        app.logger.exception("Error al obtener perfil")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: ÁLBUMES ====================


@app.get('/api/albumes')
@login_required
def get_albumes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT a.*, ar.nombre_artista, g.nombre as genero_nombre
            FROM albumes a
            LEFT JOIN artistas ar ON a.artista_id = ar.id
            LEFT JOIN generos g ON a.genero_id = g.id
            ORDER BY a.fecha_lanzamiento DESC
            LIMIT 20
        """)
        albumes = cur.fetchall()
        return jsonify({"ok": True, "albumes": albumes})
    except Exception as e:
        app.logger.exception("Error al obtener álbumes")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/albumes/<int:album_id>/canciones')
@login_required
def get_album_canciones(album_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT c.*, ar.nombre_artista, a.titulo as album_titulo
            FROM canciones c
            LEFT JOIN artistas ar ON c.artista_id = ar.id
            LEFT JOIN albumes a ON c.album_id = a.id
            WHERE c.album_id = %s
            ORDER BY c.id
        """, (album_id,))
        canciones = cur.fetchall()
        return jsonify({"ok": True, "canciones": canciones})
    except Exception as e:
        app.logger.exception("Error al obtener canciones")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: PLAYLISTS ====================


@app.get('/api/playlists')
@login_required
def get_playlists():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        cur.execute("""
            SELECT p.*, 
                   COUNT(pc.cancion_id) as num_canciones,
                   u.nombre as creador_nombre
            FROM playlists p
            LEFT JOIN playlist_canciones pc ON p.id = pc.playlist_id
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.usuario_id = %s OR p.publica = true
            GROUP BY p.id, u.nombre
            ORDER BY p.fecha_creacion DESC
        """, (usuario_id,))
        playlists = cur.fetchall()
        return jsonify({"ok": True, "playlists": playlists})
    except Exception as e:
        app.logger.exception("Error al obtener playlists")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/playlists/<int:playlist_id>/canciones')
@login_required
def get_playlist_canciones(playlist_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT c.*, ar.nombre_artista, pc.fecha_agregado
            FROM playlist_canciones pc
            INNER JOIN canciones c ON pc.cancion_id = c.id
            LEFT JOIN artistas ar ON c.artista_id = ar.id
            WHERE pc.playlist_id = %s
            ORDER BY pc.fecha_agregado DESC
        """, (playlist_id,))
        canciones = cur.fetchall()
        return jsonify({"ok": True, "canciones": canciones})
    except Exception as e:
        app.logger.exception("Error al obtener canciones de playlist")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/playlists/crear')
@login_required
def crear_playlist():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    publica = data.get("publica", False)
    
    if not nombre:
        return jsonify({"ok": False, "mensaje": "El nombre es requerido"}), 400
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        cur.execute("""
            INSERT INTO playlists (nombre, usuario_id, publica, fecha_creacion)
            VALUES (%s, %s, %s, CURRENT_DATE)
            RETURNING *
        """, (nombre, usuario_id, publica))
        playlist = cur.fetchone()
        conn.commit()
        return jsonify({"ok": True, "playlist": playlist, "mensaje": "Playlist creada"}), 201
    except Exception as e:
        app.logger.exception("Error al crear playlist")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/playlists/<int:playlist_id>/agregar')
@login_required
def agregar_cancion_playlist(playlist_id):
    data = request.get_json(silent=True) or {}
    cancion_id = data.get("cancion_id")
    
    if not cancion_id:
        return jsonify({"ok": False, "mensaje": "Falta ID de canción"}), 400
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        usuario_id = session.get("usuario_id")
        cur.execute('SELECT id FROM playlists WHERE id = %s AND usuario_id = %s', 
                   (playlist_id, usuario_id))
        if not cur.fetchone():
            return jsonify({"ok": False, "mensaje": "Playlist no encontrada"}), 404
        
        cur.execute('SELECT id FROM playlist_canciones WHERE playlist_id = %s AND cancion_id = %s',
                   (playlist_id, cancion_id))
        if cur.fetchone():
            return jsonify({"ok": False, "mensaje": "La canción ya está en la playlist"}), 409
        
        cur.execute("""
            INSERT INTO playlist_canciones (playlist_id, cancion_id, fecha_agregado)
            VALUES (%s, %s, CURRENT_DATE)
        """, (playlist_id, cancion_id))
        conn.commit()
        return jsonify({"ok": True, "mensaje": "Canción agregada a la playlist"})
    except Exception as e:
        app.logger.exception("Error al agregar canción a playlist")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/playlists/<int:playlist_id>/agregar-cancion')
@login_required
def agregar_cancion_a_playlist(playlist_id):
    data = request.get_json(silent=True) or {}
    cancion_id = data.get("cancion_id")
    
    if not cancion_id:
        return jsonify({"ok": False, "mensaje": "Falta ID de canción"}), 400
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        usuario_id = session.get("usuario_id")
        
        # Verificar que la playlist pertenece al usuario
        cur.execute('SELECT id FROM playlists WHERE id = %s AND usuario_id = %s', 
                   (playlist_id, usuario_id))
        if not cur.fetchone():
            return jsonify({"ok": False, "mensaje": "Playlist no encontrada"}), 404
        
        # Verificar si ya está en la playlist
        cur.execute('SELECT id FROM playlist_canciones WHERE playlist_id = %s AND cancion_id = %s',
                   (playlist_id, cancion_id))
        if cur.fetchone():
            return jsonify({"ok": False, "mensaje": "La canción ya está en la playlist"}), 409
        
        # Agregar
        cur.execute("""
            INSERT INTO playlist_canciones (playlist_id, cancion_id, fecha_agregado)
            VALUES (%s, %s, CURRENT_DATE)
        """, (playlist_id, cancion_id))
        conn.commit()
        return jsonify({"ok": True, "mensaje": "Canción agregada a la playlist"})
    except Exception as e:
        app.logger.exception("Error al agregar canción a playlist")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: ARTISTAS ====================


@app.get('/api/artistas')
@login_required
def get_artistas():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT a.*, COUNT(c.id) as num_canciones
            FROM artistas a
            LEFT JOIN canciones c ON a.id = c.artista_id
            GROUP BY a.id
            ORDER BY a.verificado DESC, num_canciones DESC, a.nombre_artista
            LIMIT 20
        """)
        artistas = cur.fetchall()
        return jsonify({"ok": True, "artistas": artistas})
    except Exception as e:
        app.logger.exception("Error al obtener artistas")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/artistas/<int:artista_id>/canciones')
@login_required
def get_artista_canciones(artista_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT c.*, ar.nombre_artista, a.titulo as album_titulo
            FROM canciones c
            LEFT JOIN artistas ar ON c.artista_id = ar.id
            LEFT JOIN albumes a ON c.album_id = a.id
            WHERE c.artista_id = %s
            ORDER BY c.reproducciones DESC, c.id
        """, (artista_id,))
        canciones = cur.fetchall()
        return jsonify({"ok": True, "canciones": canciones})
    except Exception as e:
        app.logger.exception("Error al obtener canciones del artista")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: CANCIONES ====================


@app.post('/api/canciones/<int:cancion_id>/reproducir')
@login_required
def reproducir_cancion(cancion_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE canciones 
            SET reproducciones = COALESCE(reproducciones, 0) + 1
            WHERE id = %s
        """, (cancion_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Exception as e:
        app.logger.exception("Error al actualizar reproducciones")
        return jsonify({"ok": False}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/search')
@login_required
def search_content():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"ok": True, "canciones": [], "albumes": [], "artistas": []})
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        search_pattern = f'%{query}%'
        
        cur.execute("""
            SELECT c.*, ar.nombre_artista
            FROM canciones c
            LEFT JOIN artistas ar ON c.artista_id = ar.id
            WHERE LOWER(c.titulo) LIKE LOWER(%s)
            LIMIT 10
        """, (search_pattern,))
        canciones = cur.fetchall()
        
        cur.execute("""
            SELECT a.*, ar.nombre_artista
            FROM albumes a
            LEFT JOIN artistas ar ON a.artista_id = ar.id
            WHERE LOWER(a.titulo) LIKE LOWER(%s)
            LIMIT 10
        """, (search_pattern,))
        albumes = cur.fetchall()
        
        cur.execute("""
            SELECT * FROM artistas
            WHERE LOWER(nombre_artista) LIKE LOWER(%s)
            LIMIT 10
        """, (search_pattern,))
        artistas = cur.fetchall()
        
        return jsonify({
            "ok": True,
            "canciones": canciones,
            "albumes": albumes,
            "artistas": artistas
        })
    except Exception as e:
        app.logger.exception("Error en búsqueda")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: FAVORITOS DE CANCIONES ====================


@app.post('/api/canciones/<int:cancion_id>/favorito')
@login_required
def toggle_cancion_favorito(cancion_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        # Verificar si ya existe en favoritos
        cur.execute(
            "SELECT * FROM favoritos WHERE usuario_id = %s AND cancion_id = %s",
            (usuario_id, cancion_id)
        )
        favorito = cur.fetchone()
        
        if favorito:
            # Eliminar de favoritos
            cur.execute("DELETE FROM favoritos WHERE usuario_id = %s AND cancion_id = %s", 
                       (usuario_id, cancion_id))
            conn.commit()
            return jsonify({'ok': True, 'added': False, 'mensaje': 'Eliminado de favoritos'})
        else:
            # Agregar a favoritos
            cur.execute("""
                INSERT INTO favoritos (usuario_id, cancion_id, fecha_agregado) 
                VALUES (%s, %s, CURRENT_DATE)
            """, (usuario_id, cancion_id))
            conn.commit()
            return jsonify({'ok': True, 'added': True, 'mensaje': 'Añadido a favoritos'})
    except Exception as e:
        app.logger.exception("Error al toggle favorito canción")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/canciones/<int:cancion_id>/favorito/check')
@login_required
def check_cancion_favorito(cancion_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        cur.execute(
            "SELECT * FROM favoritos WHERE usuario_id = %s AND cancion_id = %s",
            (usuario_id, cancion_id)
        )
        favorito = cur.fetchone()
        
        return jsonify({'ok': True, 'is_favorite': favorito is not None})
    except Exception as e:
        app.logger.exception("Error al verificar favorito")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.post('/api/favoritos/agregar')
@login_required
def agregar_favorito():
    data = request.get_json(silent=True) or {}
    cancion_id = data.get("cancion_id")
    
    if not cancion_id:
        return jsonify({"ok": False, "mensaje": "Falta ID de canción"}), 400
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        usuario_id = session.get("usuario_id")
        
        cur.execute('SELECT id FROM favoritos WHERE usuario_id = %s AND cancion_id = %s', 
                   (usuario_id, cancion_id))
        if cur.fetchone():
            return jsonify({"ok": False, "mensaje": "Ya está en favoritos"}), 409
        
        cur.execute("""
            INSERT INTO favoritos (usuario_id, cancion_id, fecha_agregado)
            VALUES (%s, %s, CURRENT_DATE)
        """, (usuario_id, cancion_id))
        conn.commit()
        return jsonify({"ok": True, "mensaje": "Agregado a favoritos"})
    except Exception as e:
        app.logger.exception("Error al agregar favorito")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.delete('/api/favoritos/eliminar/<int:cancion_id>')
@login_required
def eliminar_favorito(cancion_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        usuario_id = session.get("usuario_id")
        cur.execute('DELETE FROM favoritos WHERE usuario_id = %s AND cancion_id = %s', 
                   (usuario_id, cancion_id))
        conn.commit()
        return jsonify({"ok": True, "mensaje": "Eliminado de favoritos"})
    except Exception as e:
        app.logger.exception("Error al eliminar favorito")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/favoritos')
@login_required
def get_favoritos():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        cur.execute("""
            SELECT c.*, ar.nombre_artista, f.fecha_agregado
            FROM favoritos f
            INNER JOIN canciones c ON f.cancion_id = c.id
            LEFT JOIN artistas ar ON c.artista_id = ar.id
            WHERE f.usuario_id = %s
            ORDER BY f.fecha_agregado DESC
        """, (usuario_id,))
        favoritos = cur.fetchall()
        return jsonify({"ok": True, "favoritos": favoritos})
    except Exception as e:
        app.logger.exception("Error al obtener favoritos")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: FAVORITOS DE ÁLBUMES ====================


@app.post('/api/albumes/<int:album_id>/favorito')
@login_required
def toggle_album_favorito(album_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        # Verificar si ya existe en favoritos
        cur.execute(
            "SELECT * FROM favoritos_albumes WHERE usuario_id = %s AND album_id = %s",
            (usuario_id, album_id)
        )
        favorito = cur.fetchone()
        
        if favorito:
            # Eliminar de favoritos
            cur.execute("DELETE FROM favoritos_albumes WHERE usuario_id = %s AND album_id = %s", 
                       (usuario_id, album_id))
            conn.commit()
            return jsonify({'ok': True, 'added': False, 'mensaje': 'Eliminado de favoritos'})
        else:
            # Agregar a favoritos
            cur.execute("""
                INSERT INTO favoritos_albumes (usuario_id, album_id, fecha_agregado) 
                VALUES (%s, %s, CURRENT_DATE)
            """, (usuario_id, album_id))
            conn.commit()
            return jsonify({'ok': True, 'added': True, 'mensaje': 'Añadido a favoritos'})
    except Exception as e:
        app.logger.exception("Error al toggle favorito álbum")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/albumes/<int:album_id>/favorito/check')
@login_required
def check_album_favorito(album_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        cur.execute(
            "SELECT * FROM favoritos_albumes WHERE usuario_id = %s AND album_id = %s",
            (usuario_id, album_id)
        )
        favorito = cur.fetchone()
        
        return jsonify({'ok': True, 'is_favorite': favorito is not None})
    except Exception as e:
        app.logger.exception("Error al verificar favorito")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== API: FAVORITOS DE PLAYLISTS ====================


@app.post('/api/playlists/<int:playlist_id>/favorito')
@login_required
def toggle_playlist_favorito(playlist_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        # Verificar si ya existe en favoritos
        cur.execute(
            "SELECT * FROM favoritos_playlists WHERE usuario_id = %s AND playlist_id = %s",
            (usuario_id, playlist_id)
        )
        favorito = cur.fetchone()
        
        if favorito:
            # Eliminar de favoritos
            cur.execute("DELETE FROM favoritos_playlists WHERE usuario_id = %s AND playlist_id = %s", 
                       (usuario_id, playlist_id))
            conn.commit()
            return jsonify({'ok': True, 'added': False, 'mensaje': 'Eliminado de favoritos'})
        else:
            # Agregar a favoritos
            cur.execute("""
                INSERT INTO favoritos_playlists (usuario_id, playlist_id, fecha_agregado) 
                VALUES (%s, %s, CURRENT_DATE)
            """, (usuario_id, playlist_id))
            conn.commit()
            return jsonify({'ok': True, 'added': True, 'mensaje': 'Añadido a favoritos'})
    except Exception as e:
        app.logger.exception("Error al toggle favorito playlist")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


@app.get('/api/playlists/<int:playlist_id>/favorito/check')
@login_required
def check_playlist_favorito(playlist_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        usuario_id = session.get("usuario_id")
        
        cur.execute(
            "SELECT * FROM favoritos_playlists WHERE usuario_id = %s AND playlist_id = %s",
            (usuario_id, playlist_id)
        )
        favorito = cur.fetchone()
        
        return jsonify({'ok': True, 'is_favorite': favorito is not None})
    except Exception as e:
        app.logger.exception("Error al verificar favorito")
        return jsonify({"ok": False, "mensaje": "Error interno"}), 500
    finally:
        cur.close()
        conn.close()


# ==================== INICIAR SERVIDOR ====================


if __name__ == '__main__':
    print("🎵 Iniciando servidor Mixy...")
    print("🌐 Accede a: http://localhost:5000")
    print("🔐 Admin panel: http://localhost:5000/admin")
    app.run(debug=True, host='0.0.0.0', port=5000)
