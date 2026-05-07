/**
 * Vista Recuperar: solicita restablecimiento de contrasena con Firebase.
 */

import { state } from "../../shared/js/data.js";
import { sendPasswordRecovery } from "../../shared/js/firebase-service.js";
import { navigate } from "../../shared/js/navigation.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";
import { bindStaticLinks, showToast } from "../../shared/components/feedback.js";

/**
 * Renderiza la pantalla de recuperacion.
 * @param {HTMLElement} container
 */
export async function renderRecovery(container) {
  const template = await loadTemplate("pages/recuperar/recuperar.html");
  container.innerHTML = interpolate(template, { email: state.db.user.email });
  bindRecoveryEvents(container);
  bindStaticLinks(container);
}

/**
 * Registra eventos del formulario de recuperacion.
 * @param {HTMLElement} container
 */
function bindRecoveryEvents(container) {
  container.querySelector("#recoveryForm").addEventListener("submit", handleRecovery);
  container.querySelector("#recoverBackButton").addEventListener("click", () => navigate("login"));
}

/**
 * Valida los datos y envia el correo oficial de Firebase Authentication.
 * @param {SubmitEvent} event
 */
async function handleRecovery(event) {
  event.preventDefault();

  const email = document.getElementById("recoveryEmail").value.trim().toLowerCase();
  const newPassword = document.getElementById("newPassword").value.trim();
  const confirmPassword = document.getElementById("confirmPassword").value.trim();

  if (!email) {
    showToast("error", "Correo invalido", "Ingresa el correo institucional.");
    return;
  }

  if (!newPassword || newPassword.length < 6) {
    showToast("error", "ContraseÃ±a invÃ¡lida", "La nueva contraseÃ±a debe tener al menos 6 caracteres.");
    return;
  }

  if (newPassword !== confirmPassword) {
    showToast("error", "ConfirmaciÃ³n incorrecta", "Las contraseÃ±as no coinciden.");
    return;
  }

  try {
    await sendPasswordRecovery(email);
    showToast("success", "Solicitud enviada", "Firebase enviÃ³ un enlace seguro para actualizar la contraseÃ±a.");
    navigate("login");
  } catch (error) {
    showToast("error", "No fue posible enviar el correo", "Verifica el correo institucional e intenta nuevamente.");
  }
}

