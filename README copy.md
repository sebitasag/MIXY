# 🎵 MIXY - Reproductor de Música Web

## Instalación

1. Instalar dependencias:
```bash
pip install flask psycopg2 bcrypt
```

2. Configurar base de datos PostgreSQL:
- Crear base de datos 'proyecto_mixy'
- Ejecutar DATABASE.SQL
- Ajustar credenciales en app.py

3. Crear carpetas necesarias:
```bash
mkdir -p static/uploads static/images
```

4. Ejecutar aplicación:
```bash
python app.py
```

5. Acceder a: http://localhost:5000

## Panel de Administración

- URL: http://localhost:5000/admin
- Contraseña: mixy0005

## Estructura del Proyecto

```
mixy/
├── app.py                 # Backend Flask
├── DATABASE.SQL           # Estructura de BD
├── templates/
│   ├── index.html        # Login/Registro
│   ├── home.html         # Página principal
│   ├── admin.html        # Panel admin
│   ├── library.html      # Biblioteca
│   ├── favorites.html    # Favoritos
│   ├── search.html       # Buscador
│   └── create-playlist.html  # Crear playlist
├── static/
│   ├── style.css         # Estilos login
│   ├── script.js         # JS login
│   ├── home.css          # Estilos principales
│   ├── home.js           # JS principales
│   ├── admin.css         # Estilos admin
│   ├── admin.js          # JS admin
│   ├── uploads/          # Archivos subidos
│   └── images/           # Imágenes
```

## Características

✅ Sistema de login/registro con bcrypt
✅ Reproductor de música funcional
✅ Panel de administración protegido
✅ Subida de canciones, álbumes y artistas
✅ Búsqueda en tiempo real
✅ Sistema de favoritos
✅ Creación de playlists
✅ Diseño moderno tipo Spotify 2025
✅ Responsive design

## Tecnologías

- Backend: Flask + PostgreSQL
- Frontend: HTML5, CSS3, JavaScript
- Tipografía: Inter + JetBrains Mono
- Colores: Negro/Gris con acentos morados

## Autor

Sebastian Guerrero - Mixy 2025
