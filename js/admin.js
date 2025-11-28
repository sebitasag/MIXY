// ==================== VARIABLES GLOBALES ====================
let currentTab = 'artistas';

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔐 Admin Panel cargado');
    
    // Verificar sesión admin
    checkAdminSession();
    
    // Configurar navegación de tabs
    setupTabs();
    
    // Configurar formularios
    setupForms();
    
    // Cargar datos iniciales
    loadData();
    
    // Configurar previews de archivos
    setupFilePreviews();
});

// ==================== VERIFICAR SESIÓN ====================
async function checkAdminSession() {
    try {
        const response = await fetch('/api/perfil');
        const data = await response.json();
        
        if (!data.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error al verificar sesión:', error);
        window.location.href = '/';
    }
}

// ==================== NAVEGACIÓN DE TABS ====================
function setupTabs() {
    const navButtons = document.querySelectorAll('.admin-nav-item');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tab = button.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    currentTab = tab;
    
    // Actualizar botones activos
    document.querySelectorAll('.admin-nav-item').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // Actualizar tabs activos
    document.querySelectorAll('.admin-tab').forEach(t => {
        t.classList.remove('active');
    });
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    // Actualizar título
    const titles = {
        'artistas': 'Gestión de Artistas',
        'albumes': 'Gestión de Álbumes',
        'canciones': 'Gestión de Canciones',
        'estadisticas': 'Estadísticas'
    };
    document.getElementById('section-title').textContent = titles[tab];
    
    // Cargar datos del tab
    loadData();
}

// ==================== CONFIGURAR FORMULARIOS ====================
function setupForms() {
    // Formulario de artista
    document.getElementById('form-artista').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitArtista(e.target);
    });
    
    // Formulario de álbum
    document.getElementById('form-album').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitAlbum(e.target);
    });
    
    // Formulario de canción
    document.getElementById('form-cancion').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitCancion(e.target);
    });
}

// ==================== CARGAR DATOS ====================
async function loadData() {
    switch(currentTab) {
        case 'artistas':
            await loadArtistas();
            break;
        case 'albumes':
            await loadArtistasSelect();
            await loadGenerosSelect();
            await loadAlbumes();
            break;
        case 'canciones':
            await loadArtistasSelect();
            await loadAlbumesSelect();
            await loadCanciones();
            break;
        case 'estadisticas':
            await loadEstadisticas();
            break;
    }
}

// ==================== ARTISTAS ====================
async function loadArtistas() {
    try {
        const response = await fetch('/api/artistas');
        const data = await response.json();
        
        const container = document.getElementById('artists-list');
        
        if (data.ok && data.artistas && data.artistas.length > 0) {
            container.innerHTML = data.artistas.map(artista => `
                <div class="list-item">
                    <img src="${artista.avatar_url || 'https://via.placeholder.com/60/1a1a1a/6B5FCF?text=A'}" 
                         alt="${artista.nombre_artista}" 
                         class="list-item-image rounded">
                    <div class="list-item-info">
                        <h4>${artista.nombre_artista}</h4>
                        <p>${artista.num_canciones || 0} canciones</p>
                    </div>
                    ${artista.verificado ? '<span class="list-item-badge">Verificado</span>' : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="loading">No hay artistas registrados</p>';
        }
    } catch (error) {
        console.error('Error al cargar artistas:', error);
    }
}

async function submitArtista(form) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/admin/upload/artista', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Artista creado exitosamente', 'success');
            form.reset();
            await loadArtistas();
        } else {
            showNotification('Error: ' + data.mensaje, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al crear artista', 'error');
    }
}

// ==================== ÁLBUMES ====================
async function loadAlbumes() {
    try {
        const response = await fetch('/api/albumes');
        const data = await response.json();
        
        const container = document.getElementById('albums-list');
        
        if (data.ok && data.albumes && data.albumes.length > 0) {
            container.innerHTML = data.albumes.map(album => `
                <div class="list-item">
                    <img src="${album.cover_url || 'https://via.placeholder.com/60/1a1a1a/6B5FCF?text=A'}" 
                         alt="${album.titulo}" 
                         class="list-item-image">
                    <div class="list-item-info">
                        <h4>${album.titulo}</h4>
                        <p>${album.nombre_artista || 'Artista desconocido'}</p>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="loading">No hay álbumes registrados</p>';
        }
    } catch (error) {
        console.error('Error al cargar álbumes:', error);
    }
}

async function submitAlbum(form) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/admin/upload/album', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Álbum creado exitosamente', 'success');
            form.reset();
            await loadAlbumes();
        } else {
            showNotification('Error: ' + data.mensaje, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al crear álbum', 'error');
    }
}

// ==================== CANCIONES ====================
async function loadCanciones() {
    try {
        const response = await fetch('/api/albumes');
        const data = await response.json();
        
        const container = document.getElementById('songs-list');
        
        // Aquí deberías tener un endpoint específico para canciones
        // Por ahora mostramos un mensaje
        container.innerHTML = '<p class="loading">Las canciones subidas aparecerán aquí</p>';
    } catch (error) {
        console.error('Error al cargar canciones:', error);
    }
}

async function submitCancion(form) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/admin/upload/cancion', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Canción subida exitosamente', 'success');
            form.reset();
            await loadCanciones();
        } else {
            showNotification('Error: ' + data.mensaje, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al subir canción', 'error');
    }
}

// ==================== SELECTS ====================
async function loadArtistasSelect() {
    try {
        const response = await fetch('/api/artistas');
        const data = await response.json();
        
        if (data.ok && data.artistas) {
            const selects = document.querySelectorAll('#artista-album, #artista-cancion');
            selects.forEach(select => {
                select.innerHTML = '<option value="">Seleccionar artista</option>' +
                    data.artistas.map(a => `<option value="${a.id}">${a.nombre_artista}</option>`).join('');
            });
        }
    } catch (error) {
        console.error('Error al cargar artistas:', error);
    }
}

async function loadGenerosSelect() {
    // Géneros predefinidos
    const generos = [
        { id: 1, nombre: 'Pop' },
        { id: 2, nombre: 'Rock' },
        { id: 3, nombre: 'Hip Hop' },
        { id: 4, nombre: 'Electrónica' },
        { id: 5, nombre: 'Jazz' },
        { id: 6, nombre: 'Clásica' },
        { id: 7, nombre: 'Reggaeton' },
        { id: 8, nombre: 'Salsa' }
    ];
    
    const select = document.getElementById('genero-album');
    select.innerHTML = '<option value="">Seleccionar género</option>' +
        generos.map(g => `<option value="${g.id}">${g.nombre}</option>`).join('');
}

async function loadAlbumesSelect() {
    try {
        const response = await fetch('/api/albumes');
        const data = await response.json();
        
        if (data.ok && data.albumes) {
            const select = document.getElementById('album-cancion');
            select.innerHTML = '<option value="">Seleccionar álbum</option>' +
                data.albumes.map(a => `<option value="${a.id}">${a.titulo}</option>`).join('');
        }
    } catch (error) {
        console.error('Error al cargar álbumes:', error);
    }
}

// ==================== ESTADÍSTICAS ====================
async function loadEstadisticas() {
    // Cargar estadísticas básicas
    try {
        const [artistas, albumes] = await Promise.all([
            fetch('/api/artistas').then(r => r.json()),
            fetch('/api/albumes').then(r => r.json())
        ]);
        
        document.getElementById('stat-artistas').textContent = artistas.artistas?.length || 0;
        document.getElementById('stat-albumes').textContent = albumes.albumes?.length || 0;
        document.getElementById('stat-canciones').textContent = '0'; // Implementar endpoint
        document.getElementById('stat-usuarios').textContent = '0'; // Implementar endpoint
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// ==================== PREVIEWS DE ARCHIVOS ====================
function setupFilePreviews() {
    // Avatar artista
    document.getElementById('avatar-artista')?.addEventListener('change', (e) => {
        previewFile(e.target, 'preview-avatar');
    });
    
    // Cover álbum
    document.getElementById('cover-album')?.addEventListener('change', (e) => {
        previewFile(e.target, 'preview-cover-album');
    });
    
    // Cover canción
    document.getElementById('cover-cancion')?.addEventListener('change', (e) => {
        previewFile(e.target, 'preview-cover-cancion');
    });
    
    // Archivo canción
    document.getElementById('archivo-cancion')?.addEventListener('change', (e) => {
        previewAudioFile(e.target, 'preview-audio');
    });
}

function previewFile(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const file = input.files[0];
        preview.textContent = `✓ ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    }
}

function previewAudioFile(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const file = input.files[0];
        preview.textContent = `🎵 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    }
}

// ==================== NOTIFICACIONES ====================
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

console.log('✅ Admin.js cargado');
