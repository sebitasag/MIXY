-- Base de datos Mixy actualizada

-- Crear tablas
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    nacimiento DATE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artistas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    nombre_artista VARCHAR(150) NOT NULL,
    verificado BOOLEAN DEFAULT FALSE,
    avatar_url TEXT
);

CREATE TABLE IF NOT EXISTS generos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS albumes (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    artista_id INTEGER REFERENCES artistas(id),
    fecha_lanzamiento DATE,
    genero_id INTEGER REFERENCES generos(id),
    cover_url TEXT
);

CREATE TABLE IF NOT EXISTS canciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    artista_id INTEGER REFERENCES artistas(id),
    album_id INTEGER REFERENCES albumes(id),
    duracion_segundos INTEGER,
    archivo_url TEXT,
    cover_url TEXT,
    reproducciones INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS playlists (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id),
    publica BOOLEAN DEFAULT FALSE,
    fecha_creacion DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS playlist_canciones (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
    cancion_id INTEGER REFERENCES canciones(id) ON DELETE CASCADE,
    fecha_agregado DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    cancion_id INTEGER REFERENCES canciones(id) ON DELETE CASCADE,
    fecha_agregado DATE DEFAULT CURRENT_DATE,
    UNIQUE(usuario_id, cancion_id)
);

-- Insertar géneros por defecto
INSERT INTO generos (nombre) VALUES 
('Pop'), ('Rock'), ('Hip Hop'), ('Electrónica'), 
('Jazz'), ('Clásica'), ('Reggaeton'), ('Salsa'),
('Bachata'), ('R&B'), ('Country'), ('Metal')
ON CONFLICT DO NOTHING;
