// ---- SLIDE ENTRE LOGIN Y REGISTRO ----
const btnSlide = document.getElementById("slide-btn");
const slideTitle = document.getElementById("slide-title");
const slideText = document.getElementById("slide-text");
const registroSection = document.getElementById("registro-section");
const loginSection = document.getElementById("login-section");
const slidePanel = document.getElementById("slide-panel");
let panelState = "login"; // login / registro

btnSlide.addEventListener('click', ()=>{
  if(panelState==="login"){
    // Mostrar registro
    loginSection.classList.add('hidden');
    registroSection.classList.remove('hidden');
    slideTitle.textContent = "¡Hola!";
    slideText.textContent = "¿Ya tienes cuenta? Ingresa tus datos para acceder a todas las funciones.";
    btnSlide.textContent = "Iniciar Sesión";
    panelState = "registro";
    slidePanel.style.background = "linear-gradient(120deg,#3AB397 40%,#53e0c6 100%)";
  }else{
    // Mostrar login
    registroSection.classList.add('hidden');
    loginSection.classList.remove('hidden');
    slideTitle.textContent = "¡Bienvenido!";
    slideText.textContent = "¿Eres nuevo aquí? Regístrate para usar todas las funciones del sitio.";
    btnSlide.textContent = "Registrarse";
    panelState = "login";
    slidePanel.style.background = "linear-gradient(120deg,#3AA8AD 70%,#53e0c6 100%)";
  }
});