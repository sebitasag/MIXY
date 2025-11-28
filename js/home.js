// ==================== VARIABLES GLOBALES ====================
let currentTrack = null;
let isPlaying = false;
let audioPlayer = new Audio();
let playlist = [];
let currentTrackIndex = 0;

// ==================== ELEMENTOS DEL DOM ====================
const albumsContainer = document.getElementById('albums-container');
const playlistsContainer = document.getElementById('playlists-container');
const artistsContainer = document.getElementById('artists-container');
const queueList = document.getElementById('queue-list');
const btnPlay = document.getElementById('btn-play');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const progressBar = document.getElementById('progress-bar');
const volumeSlider = document.getElementById('volume-slider');
const trackTitle = document.getElementById('track-title');
const trackArtist = document.getElementById('track-artist');
const trackCover = document.getElementById('track-cover');
const timeCurrent = document.getElementById('time-current');
const timeTotal = document.getElementById('time-total');

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎵 Iniciando Mixy...');
    await loadUserInfo();
    await loadAlbums();
    await loadPlaylists();
    await loadArtists();
    setupPlayerEvents();
    console.log('✅ Mixy iniciado correctamente');
});

// ==================== CARGAR INFORMACIÓN DEL USUARIO ====================
async function loadUserInfo() {
    try {
        const response = await fetch('/api/perfil');
        const data = await response.json();
        
        if (data.ok) {
            const userName = data.correo.split('@')[0]; // Extraer nombre antes del @
            document.getElementById('user-name').textContent = userName;
            document.getElementById('user-greeting').textContent = `Hola, ${userName}`;
            console.log('✅ Perfil cargado:', userName);
        } else {
            console.error('❌ Error al cargar perfil');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('❌ Error al cargar perfil:', error);
        window.location.href = '/';
    }
}

// ==================== CARGAR ÁLBUMES ====================
async function loadAlbums() {
    try {
        const response = await fetch('/api/albumes');
        const data = await response.json();
        
        if (data.ok && data.albumes && data.albumes.length > 0) {
            albumsContainer.innerHTML = '';
            data.albumes.forEach(album => {
                const albumCard = createAlbumCard(album);
                albumsContainer.appendChild(albumCard);
            });
            console.log(`✅ ${data.albumes.length} álbumes cargados`);
        } else {
            albumsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #9693a5;">
                    <p style="font-size: 18px;">📀 No hay álbumes disponibles</p>
                    <p style="font-size: 14px; margin-top: 8px;">Sube tu primer álbum para empezar</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error al cargar álbumes:', error);
        albumsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                <p>❌ Error al cargar álbumes</p>
            </div>
        `;
    }
}

// ==================== CREAR TARJETA DE ÁLBUM ====================
function createAlbumCard(album) {
    const card = document.createElement('div');
    card.className = 'album-card';
    card.onclick = () => loadAlbumSongs(album.id);
    
    const artistName = album.artista_nombre || album.nombre_artista || 'Desconocido';
    const coverUrl = album.cover_url || '/static/images/default-album.png';
    
    card.innerHTML = `
        <div class="album-cover">
            <img src="${coverUrl}" alt="${album.titulo}" onerror="this.src='/static/images/default-album.png'">
            <div class="play-overlay">▶️</div>
        </div>
        <div class="album-info">
            <h3>${album.titulo}</h3>
            <p>${artistName}</p>
        </div>
    `;
    
    return card;
}

// ==================== CARGAR PLAYLISTS ====================
async function loadPlaylists() {
    try {
        const response = await fetch('/api/playlists');
        const data = await response.json();
        
        if (data.ok && data.playlists && data.playlists.length > 0) {
            playlistsContainer.innerHTML = '';
            data.playlists.forEach(playlist => {
                const playlistCard = createPlaylistCard(playlist);
                playlistsContainer.appendChild(playlistCard);
            });
            console.log(`✅ ${data.playlists.length} playlists cargadas`);
        } else {
            playlistsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #9693a5;">
                    <p style="font-size: 18px;">🎧 No hay playlists disponibles</p>
                    <p style="font-size: 14px; margin-top: 8px;">Crea tu primera playlist</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error al cargar playlists:', error);
        playlistsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                <p>❌ Error al cargar playlists</p>
            </div>
        `;
    }
}

// ==================== CREAR TARJETA DE PLAYLIST ====================
function createPlaylistCard(playlist) {
    const card = document.createElement('div');
    card.className = 'album-card';
    card.onclick = () => loadPlaylistSongs(playlist.id);
    
    const numCanciones = playlist.num_canciones || 0;
    const coverUrl = playlist.cover_url || '/static/images/default-playlist.png';
    
    card.innerHTML = `
        <div class="album-cover">
            <img src="${coverUrl}" alt="${playlist.nombre}" onerror="this.src='/static/images/default-playlist.png'">
            <div class="play-overlay">▶️</div>
        </div>
        <div class="album-info">
            <h3>${playlist.nombre}</h3>
            <p>${numCanciones} ${numCanciones === 1 ? 'canción' : 'canciones'}</p>
        </div>
    `;
    
    return card;
}

// ==================== CARGAR ARTISTAS ====================
async function loadArtists() {
    try {
        const response = await fetch('/api/artistas');
        const data = await response.json();
        
        if (data.ok && data.artistas && data.artistas.length > 0) {
            artistsContainer.innerHTML = '';
            data.artistas.forEach(artist => {
                const artistCard = createArtistCard(artist);
                artistsContainer.appendChild(artistCard);
            });
            console.log(`✅ ${data.artistas.length} artistas cargados`);
        } else {
            artistsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #9693a5;">
                    <p style="font-size: 18px;">🎤 No hay artistas disponibles</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error al cargar artistas:', error);
        artistsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                <p>❌ Error al cargar artistas</p>
            </div>
        `;
    }
}

// ==================== CREAR TARJETA DE ARTISTA ====================
function createArtistCard(artist) {
    const card = document.createElement('div');
    card.className = 'artist-card';
    card.onclick = () => loadArtistSongs(artist.id);
    
    const avatarUrl = artist.avatar_url || '/static/images/default-artist.png';
    const verificado = artist.verificado ? ' ✓' : '';
    
    card.innerHTML = `
        <div class="artist-avatar">
            <img src="${avatarUrl}" alt="${artist.nombre_artista}" onerror="this.src='/static/images/default-artist.png'">
        </div>
        <h3>${artist.nombre_artista}${verificado}</h3>
        <p>Artista</p>
    `;
    
    return card;
}

// ==================== CARGAR CANCIONES DE UN ÁLBUM ====================
async function loadAlbumSongs(albumId) {
    try {
        const response = await fetch(`/api/albumes/${albumId}/canciones`);
        const data = await response.json();
        
        if (data.ok && data.canciones && data.canciones.length > 0) {
            playlist = data.canciones;
            updateQueue();
            playTrack(0);
            console.log(`✅ ${data.canciones.length} canciones cargadas del álbum`);
        } else {
            alert('Este álbum no tiene canciones aún');
        }
    } catch (error) {
        console.error('❌ Error al cargar canciones del álbum:', error);
        alert('Error al cargar las canciones del álbum');
    }
}

// ==================== CARGAR CANCIONES DE UNA PLAYLIST ====================
async function loadPlaylistSongs(playlistId) {
    try {
        const response = await fetch(`/api/playlists/${playlistId}/canciones`);
        const data = await response.json();
        
        if (data.ok && data.canciones && data.canciones.length > 0) {
            playlist = data.canciones;
            updateQueue();
            playTrack(0);
            console.log(`✅ ${data.canciones.length} canciones cargadas de la playlist`);
        } else {
            alert('Esta playlist está vacía');
        }
    } catch (error) {
        console.error('❌ Error al cargar canciones de la playlist:', error);
        alert('Error al cargar las canciones de la playlist');
    }
}

// ==================== CARGAR CANCIONES DE UN ARTISTA ====================
async function loadArtistSongs(artistaId) {
    try {
        const response = await fetch(`/api/artistas/${artistaId}/canciones`);
        const data = await response.json();
        
        if (data.ok && data.canciones && data.canciones.length > 0) {
            playlist = data.canciones;
            updateQueue();
            playTrack(0);
            console.log(`✅ ${data.canciones.length} canciones cargadas del artista`);
        } else {
            alert('Este artista no tiene canciones aún');
        }
    } catch (error) {
        console.error('❌ Error al cargar canciones del artista:', error);
        alert('Error al cargar las canciones del artista');
    }
}

// ==================== REPRODUCIR UNA CANCIÓN ====================
function playTrack(index) {
    if (index < 0 || index >= playlist.length) {
        console.log('⚠️ Índice de canción inválido:', index);
        return;
    }
    
    currentTrackIndex = index;
    const track = playlist[index];
    
    console.log('▶️ Reproduciendo:', track.titulo);
    
    // Actualizar información visual
    trackTitle.textContent = track.titulo;
    trackArtist.textContent = track.artista_nombre || track.nombre_artista || 'Desconocido';
    trackCover.src = track.cover_url || '/static/images/default-cover.png';
    
    // Si no hay archivo de audio, mostrar error
    if (!track.archivo_url) {
        alert('Esta canción no tiene archivo de audio disponible');
        return;
    }
    
    // Cargar y reproducir audio
    audioPlayer.src = track.archivo_url;
    audioPlayer.play()
        .then(() => {
            isPlaying = true;
            btnPlay.textContent = '⏸️';
            console.log('✅ Reproducción iniciada');
            
            // Actualizar contador de reproducciones
            fetch(`/api/canciones/${track.id}/reproducir`, { method: 'POST' })
                .catch(err => console.error('Error al actualizar reproducciones:', err));
        })
        .catch(error => {
            console.error('❌ Error al reproducir:', error);
            alert('No se pudo reproducir la canción. Verifica que el archivo de audio exista.');
        });
    
    // Resaltar canción actual en la cola
    updateQueueHighlight();
}

// ==================== CONFIGURAR EVENTOS DEL REPRODUCTOR ====================
function setupPlayerEvents() {
    // Botones de control
    btnPlay.onclick = togglePlay;
    btnPrev.onclick = () => {
        if (currentTrackIndex > 0) {
            playTrack(currentTrackIndex - 1);
        }
    };
    btnNext.onclick = () => {
        if (currentTrackIndex < playlist.length - 1) {
            playTrack(currentTrackIndex + 1);
        }
    };
    
    // Actualizar barra de progreso
    audioPlayer.ontimeupdate = () => {
        if (audioPlayer.duration) {
            const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
            progressBar.value = progress;
            timeCurrent.textContent = formatTime(audioPlayer.currentTime);
            timeTotal.textContent = formatTime(audioPlayer.duration);
        }
    };
    
    // Cuando termina una canción, reproducir la siguiente
    audioPlayer.onended = () => {
        if (currentTrackIndex < playlist.length - 1) {
            playTrack(currentTrackIndex + 1);
        } else {
            isPlaying = false;
            btnPlay.textContent = '▶️';
            console.log('✅ Playlist terminada');
        }
    };
    
    // Cambiar posición de reproducción
    progressBar.oninput = () => {
        if (audioPlayer.duration) {
            const time = (progressBar.value / 100) * audioPlayer.duration;
            audioPlayer.currentTime = time;
        }
    };
    
    // Control de volumen
    volumeSlider.oninput = () => {
        audioPlayer.volume = volumeSlider.value / 100;
    };
    
    // Establecer volumen inicial
    audioPlayer.volume = 0.8;
    
    console.log('✅ Eventos del reproductor configurados');
}

// ==================== TOGGLE PLAY/PAUSE ====================
function togglePlay() {
    if (!audioPlayer.src) {
        alert('Selecciona una canción primero');
        return;
    }
    
    if (isPlaying) {
        audioPlayer.pause();
        btnPlay.textContent = '▶️';
        console.log('⏸️ Pausado');
    } else {
        audioPlayer.play()
            .then(() => {
                btnPlay.textContent = '⏸️';
                console.log('▶️ Reproduciendo');
            })
            .catch(error => {
                console.error('❌ Error al reproducir:', error);
            });
    }
    isPlaying = !isPlaying;
}

function updateQueue() {
    const queueList = document.getElementById('queue-list');
    if (currentPlaylist.length === 0) {
        queueList.innerHTML = `
            <div class="empty-queue">
                <i class="fas fa-music"></i>
                <p>Selecciona un álbum o playlist</p>
            </div>
        `;
        return;
    }
    
    // Mostrar solo las canciones desde la actual en adelante
    const remainingSongs = currentPlaylist.slice(currentTrackIndex);
    
    if (remainingSongs.length === 0) {
        queueList.innerHTML = `
            <div class="empty-queue">
                <i class="fas fa-music"></i>
                <p>No hay más canciones en la cola</p>
            </div>
        `;
        return;
    }
    
    queueList.innerHTML = remainingSongs.map((cancion, index) => {
        const actualIndex = currentTrackIndex + index;
        return `
            <div class="queue-item ${index === 0 ? 'active' : ''}" data-index="${actualIndex}">
                <div class="queue-item-cover">
                    <img src="${cancion.cover_url || 'https://via.placeholder.com/48x48/1a1a1a/6B5FCF?text=M'}" alt="${cancion.titulo}">
                </div>
                <div class="queue-item-info">
                    <h5>${cancion.titulo}</h5>
                    <p>${cancion.nombre_artista || 'Desconocido'}</p>
                </div>
                <button class="queue-item-remove" data-index="${actualIndex}" title="Eliminar de la cola">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }).join('');
    
    // Event listeners para hacer clic en las canciones
    queueList.querySelectorAll('.queue-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.queue-item-remove')) {
                const index = parseInt(item.dataset.index);
                currentTrackIndex = index;
                playTrack(currentPlaylist[index]);
            }
        });
    });
    
    // Event listeners para eliminar canciones
    queueList.querySelectorAll('.queue-item-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            removeFromQueue(index);
        });
    });
}

function removeFromQueue(index) {
    if (index === currentTrackIndex) {
        showNotification('No puedes eliminar la canción actual', 'info');
        return;
    }
    
    currentPlaylist.splice(index, 1);
    
    if (index < currentTrackIndex) {
        currentTrackIndex--;
    }
    
    updateQueue();
    showNotification('Canción eliminada de la cola', 'info');
}


// ==================== RESALTAR CANCIÓN ACTUAL EN LA COLA ====================
function updateQueueHighlight() {
    const items = queueList.querySelectorAll('.queue-item');
    items.forEach((item, index) => {
        if (index === currentTrackIndex) {
            item.style.background = 'rgba(97, 87, 149, 0.4)';
            item.style.borderLeft = '3px solid #615795';
        } else {
            item.style.background = '';
            item.style.borderLeft = '';
        }
    });
}

// ==================== FORMATEAR TIEMPO ====================
function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ==================== MANEJO DE ERRORES GLOBALES ====================
window.addEventListener('error', (event) => {
    console.error('❌ Error global:', event.error);
});

console.log('✅ Script home.js cargado correctamente');
