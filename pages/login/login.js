/**
 * Vista Login: renderiza el acceso y valida credenciales con Firebase.
 */

import { loadDatabaseForUser, loadSession, saveSession } from "../../shared/js/data.js";
import { loginWithEmail } from "../../shared/js/firebase-service.js";
import { navigate } from "../../shared/js/navigation.js";
import { loadTemplate } from "../../shared/js/template-loader.js";
import { bindStaticLinks, closeModal, showModal } from "../../shared/components/feedback.js";

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
  container.querySelector("#loginForm").addEventListener("submit", handleLogin);
  container.querySelector("#loginRecoverLink").addEventListener("click", (event) => {
    event.preventDefault();
    navigate("recuperar");
  });
}

/**
 * Valida credenciales y abre la sesión de usuario.
 * @param {SubmitEvent} event
 */
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("loginEmail").value.trim().toLowerCase();
  const password = document.getElementById("loginPassword").value.trim();

  try {
    const user = await loginWithEmail(email, password);
    await loadDatabaseForUser(user);
    saveSession(loadSession(user));
    navigate("inicio");
  } catch (error) {
    showModal({
      title: getFirebaseLoginTitle(error),
      icon: "error",
      text: getFirebaseLoginMessage(error),
      actions: [{ label: "Reintentar", className: "mini-btn red", onClick: closeModal }]
    });
  }
}

/**
 * Traduce errores comunes de Firebase para diagnosticar la configuración.
 * @param {{code?: string}} error
 * @returns {string}
 */
function getFirebaseLoginMessage(error) {
  const code = error?.code || "error-desconocido";
  if (isCredentialError(code)) {
    return "";
  }

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
  return isCredentialError(error?.code) ? "Correo o contraseña incorrectos" : "No se pudo conectar con Firebase";
}

function isCredentialError(code) {
  return ["auth/invalid-credential", "auth/wrong-password", "auth/user-not-found", "auth/email-already-in-use"].includes(code);
}
