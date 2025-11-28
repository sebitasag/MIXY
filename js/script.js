// ==================== VARIABLES ====================
const btnSlide = document.getElementById("slide-btn");
const loginSection = document.getElementById("login-section");
const registroSection = document.getElementById("registro-section");
const slideTitle = document.querySelector("#slide-content h3");
const slideText = document.querySelector("#slide-content p");
let mostrando = "login";

// ==================== CAMBIO ENTRE LOGIN Y REGISTRO ====================
btnSlide.addEventListener("click", () => {
  if (mostrando === "login") {
    // Mostrar registro
    loginSection.classList.add("hidden");
    registroSection.classList.remove("hidden");
    
    btnSlide.innerHTML = '<i class="fas fa-right-to-bracket"></i> Iniciar Sesión';
    slideTitle.textContent = "¿Ya tienes cuenta?";
    slideText.textContent = "Inicia sesión para acceder a tu biblioteca musical";
    
    // Limpiar errores
    document.getElementById("login-error").classList.remove("show");
    document.getElementById("registro-error").classList.remove("show");
    
    mostrando = "registro";
  } else {
    // Mostrar login
    registroSection.classList.add("hidden");
    loginSection.classList.remove("hidden");
    
    btnSlide.innerHTML = '<i class="fas fa-user-plus"></i> Crear Cuenta';
    slideTitle.textContent = "¡Bienvenido a Mixy!";
    slideText.textContent = "Descubre, escucha y disfruta de tu música favorita";
    
    // Limpiar errores
    document.getElementById("login-error").classList.remove("show");
    document.getElementById("registro-error").classList.remove("show");
    
    mostrando = "login";
  }
});

// ==================== REGISTRO ====================
document.getElementById("registro-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const errorDiv = document.getElementById("registro-error");
  const submitBtn = e.target.querySelector('button[type="submit"]');
  
  // Limpiar error anterior
  errorDiv.classList.remove("show");
  errorDiv.textContent = "";
  
  // Deshabilitar botón
  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  const datos = {
    nombre: document.getElementById("nombre").value,
    apellido: document.getElementById("apellido").value,
    correo: document.getElementById("correo").value,
    nacimiento: document.getElementById("nacimiento").value,
    password: document.getElementById("password").value
  };

  try {
    const res = await fetch("/api/registro", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(datos)
    });

    const data = await res.json();

    if (data.ok) {
      // Registro exitoso - cambiar a login
      e.target.reset();
      registroSection.classList.add("hidden");
      loginSection.classList.remove("hidden");
      
      btnSlide.innerHTML = '<i class="fas fa-user-plus"></i> Crear Cuenta';
      slideTitle.textContent = "¡Bienvenido a Mixy!";
      slideText.textContent = "Descubre, escucha y disfruta de tu música favorita";
      
      mostrando = "login";
      
      // Mostrar mensaje de éxito en login
      const loginError = document.getElementById("login-error");
      loginError.style.background = "rgba(29, 215, 96, 0.1)";
      loginError.style.borderColor = "rgba(29, 215, 96, 0.3)";
      loginError.style.color = "#1ED760";
      loginError.textContent = "✓ Cuenta creada exitosamente. Inicia sesión";
      loginError.classList.add("show");
      
      setTimeout(() => {
        loginError.classList.remove("show");
        loginError.style.background = "";
        loginError.style.borderColor = "";
        loginError.style.color = "";
      }, 5000);
      
    } else {
      errorDiv.textContent = data.mensaje || "Error al registrar usuario";
      errorDiv.classList.add("show");
    }
  } catch (error) {
    console.error("Error:", error);
    errorDiv.textContent = "Error de conexión. Intenta nuevamente";
    errorDiv.classList.add("show");
  } finally {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
});

// ==================== LOGIN ====================
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const errorDiv = document.getElementById("login-error");
  const submitBtn = e.target.querySelector('button[type="submit"]');
  
  // Limpiar error anterior
  errorDiv.classList.remove("show");
  errorDiv.textContent = "";
  
  // Deshabilitar botón
  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  const datos = {
    correo: e.target.loginCorreo.value,
    password: e.target.loginClave.value
  };

  try {
    const res = await fetch("/api/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(datos)
    });

    const data = await res.json();

    if (data.ok) {
      // Login exitoso - redirigir a home
      window.location.href = "/home";
    } else {
      errorDiv.textContent = data.mensaje || "Correo o contraseña incorrectos";
      errorDiv.classList.add("show");
      submitBtn.classList.remove("loading");
      submitBtn.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
    errorDiv.textContent = "Error de conexión. Intenta nuevamente";
    errorDiv.classList.add("show");
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
});

console.log("✅ Script de login cargado");
