/**
 * Vista Login: renderiza el acceso con validación institucional,
 * seguridad de contraseña y cumplimiento de Habeas Data.
 */

import {
  INSTITUTIONAL_DOMAIN,
  loadDatabaseForUser,
  loadSession,
  saveSession,
  state
} from "../../shared/js/data.js";
import {
  checkHabeasDataAcceptance,
  loginWithEmail,
  saveHabeasDataAcceptance
} from "../../shared/js/firebase-service.js";
import { navigate } from "../../shared/js/navigation.js";
import { loadTemplate } from "../../shared/js/template-loader.js";
import { bindStaticLinks, closeModal, showModal } from "../../shared/components/feedback.js";

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

/**
 * Renderiza la pantalla de login.
 * @param {HTMLElement} container
 */
export async function renderLogin(container) {
  container.innerHTML = await loadTemplate("pages/login/login.html");
  bindLoginEvents(container);
  bindStaticLinks(container);
}

/**
 * Registra eventos principales del login.
 * @param {HTMLElement} container
 */
function bindLoginEvents(container) {
  document.getElementById("loginEmail").addEventListener("input", validateEmailRealTime);
  document.getElementById("loginPassword").addEventListener("input", validatePasswordRealTime);
  document.getElementById("togglePassword").addEventListener("click", togglePasswordVisibility);
  document.getElementById("habeasDataCheck").addEventListener("change", updateSubmitButton);
  document.getElementById("showHabeasModal").addEventListener("click", (e) => { e.preventDefault(); showHabeasDataModal(); });
  container.querySelector("#loginForm").addEventListener("submit", handleLogin);
  container.querySelector("#loginRecoverLink").addEventListener("click", (event) => {
    event.preventDefault();
    navigate("recuperar");
  });
}

/**
 * Alterna la visibilidad de la contrasena sin afectar validaciones.
 */
function togglePasswordVisibility() {
  const passwordInput = document.getElementById("loginPassword");
  const toggleButton = document.getElementById("togglePassword");
  const shouldShow = passwordInput.type === "password";

  passwordInput.type = shouldShow ? "text" : "password";
  toggleButton.classList.toggle("is-visible", shouldShow);
  toggleButton.setAttribute("aria-label", shouldShow ? "Ocultar contrasena" : "Mostrar contrasena");
  toggleButton.setAttribute("title", shouldShow ? "Ocultar contrasena" : "Mostrar contrasena");
}

/**
 * Valida el correo institucional internamente (sin feedback visual).
 */
function validateEmailRealTime() {
  updateSubmitButton();
}

/**
 * Valida la contraseña internamente (sin feedback visual).
 */
function validatePasswordRealTime() {
  updateSubmitButton();
}

/**
 * Habilita/deshabilita el botón de ingreso según validaciones.
 */
function updateSubmitButton() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const habeasAccepted = document.getElementById("habeasDataCheck").checked;

  const emailValid = EMAIL_REGEX.test(email) && email.toLowerCase().endsWith(INSTITUTIONAL_DOMAIN);
  const passwordValid = password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /\d/.test(password) &&
    /[!@#$%^&*(),.?":{}|<>_\-+=[\]\\;'`~]/.test(password);

  document.getElementById("loginSubmitBtn").disabled = !(emailValid && passwordValid && habeasAccepted);
}

/**
 * Muestra el modal de Habeas Data con los términos institucionales.
 */
function showHabeasDataModal() {
  showModal({
    title: "Protección de Datos",
    icon: "none",
    className: "habeas-modal",
    customHtml: `
      <div class="habeas-content">
        <p><strong>Finalidad académica:</strong> Tus datos serán utilizados únicamente con fines académicos, incluyendo recomendación de cursos, seguimiento de progreso y generación de reportes de rendimiento.</p>
        <p><strong>Protección de información:</strong> La información está protegida bajo políticas institucionales de seguridad y confidencialidad, en cumplimiento de la Ley 1581 de 2012 (Habeas Data).</p>
        <p><strong>Asistente virtual:</strong> El asistente virtual analiza tu perfil, cursos inscritos y progreso para ofrecer recomendaciones academicas personalizadas.</p>
        <p><strong>Confidencialidad:</strong> Tus datos no serán compartidos con terceros sin tu consentimiento explícito, excepto cuando la ley lo requiera.</p>
        <p><strong>Derechos del estudiante:</strong> Puedes solicitar en cualquier momento la actualización, rectificación o eliminación de tus datos personales.</p>
      </div>
    `,
    actions: [
      { label: "Entendido", className: "mini-btn", onClick: closeModal }
    ]
  });
}

/**
 * Valida credenciales, verifica Habeas Data y abre la sesión de usuario.
 * @param {SubmitEvent} event
 */
async function handleLogin(event) {
  event.preventDefault();

  const emailInput = document.getElementById("loginEmail");
  const passwordInput = document.getElementById("loginPassword");
  const email = emailInput.value.trim().toLowerCase();
  const password = passwordInput.value;

  if (!email.toLowerCase().endsWith(INSTITUTIONAL_DOMAIN)) {
    showToast("error", "Acceso denegado", `Solo se permite el ingreso con correo institucional ${INSTITUTIONAL_DOMAIN}.`);
    return;
  }

  try {
    const user = await loginWithEmail(email, password);
    await loadDatabaseForUser(user);

    if (!state.db.user.habeasDataAccepted) {
      const alreadyAccepted = await checkHabeasDataAcceptance(user.uid);
      if (!alreadyAccepted) {
        await saveHabeasDataAcceptance(user.uid, email);
      }
      state.db.user.habeasDataAccepted = true;
    }

    saveSession(loadSession(user));
    navigate("inicio");
  } catch (error) {
    const code = error?.code || "";
    if (isCredentialError(code)) {
      showToast("error", "Credenciales incorrectas", "El correo o la contraseña no coinciden con nuestros registros institucionales.");
    } else {
      showModal({
        title: getFirebaseLoginTitle(error),
        icon: "error",
        text: getFirebaseLoginMessage(error),
        actions: [{ label: "Reintentar", className: "mini-btn red", onClick: closeModal }]
      });
    }
  }
}

/**
 * Traduce errores comunes de Firebase para diagnosticar la configuración.
 * @param {{code?: string}} error
 * @returns {string}
 */
function getFirebaseLoginMessage(error) {
  const code = error?.code || "error-desconocido";
  if (isCredentialError(code)) return "";

  const messages = {
    "auth/configuration-not-found": "Revisa que Authentication esté activado en este proyecto Firebase.",
    "auth/operation-not-allowed": "Activa el proveedor Correo electrónico/Contraseña en Authentication.",
    "auth/unauthorized-domain": "Agrega localhost y 127.0.0.1 en Authentication > Settings > Authorized domains.",
    "auth/api-key-not-valid.-please-pass-a-valid-api-key.": "La apiKey no corresponde a este proyecto.",
    "permission-denied": "Firestore rechazó la escritura. Revisa reglas y que el usuario esté autenticado."
  };

  return `${messages[code] || "Revisa la consola del navegador para ver el detalle."} Código: ${code}`;
}

function getFirebaseLoginTitle(error) {
  return isCredentialError(error?.code) ? "Credenciales incorrectas" : "Error de conexión con Firebase";
}

function isCredentialError(code) {
  return ["auth/invalid-credential", "auth/wrong-password", "auth/user-not-found", "auth/email-already-in-use"].includes(code);
}

/**
 * Toast temporal (definición local para evitar dependencia circular).
 */
function showToast(type, title, text) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<strong>${title}</strong><span>${text}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}
