/**
 * Vista Perfil: edición de modalidad, contraseña, avatar y sesión.
 */

import { resetSarcDemo, saveDatabase, saveSession, state } from "../../shared/js/data.js";
import { logoutFirebaseUser, updateCurrentUserPassword } from "../../shared/js/firebase-service.js";
import { navigate } from "../../shared/js/navigation.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";
import { closeModal, showModal, showToast } from "../../shared/components/feedback.js";

let refreshProfile = () => {};

/**
 * Renderiza la pantalla de perfil.
 * @param {HTMLElement} container
 */
export async function renderProfile(container) {
  const template = await loadTemplate("pages/perfil/perfil.html");
  const user = state.db.user;
  refreshProfile = () => renderProfile(container);

  container.innerHTML = interpolate(template, {
    name: user.name,
    faculty: user.faculty,
    career: user.career,
    semester: user.semester,
    modality: user.modality,
    avatar: user.avatar
  });

  bindProfileEvents(container);
}

/**
 * Registra eventos de perfil, demo y cierre de sesión.
 * @param {HTMLElement} container
 */
function bindProfileEvents(container) {
  container.querySelector("#editProfileButton").addEventListener("click", openProfileEditor);
  container.querySelector("#resetDemoButton").addEventListener("click", confirmResetDemo);
  container.querySelector("#logoutButton").addEventListener("click", logout);
}

/**
 * Solicita confirmación antes de reiniciar la demo.
 */
function confirmResetDemo() {
  showModal({
    title: "Reiniciar demo",
    icon: "none",
    text: "Se borrarán las inscripciones simuladas, el perfil editado y la sesión actual.",
    actions: [
      { label: "Cancelar", className: "mini-btn", onClick: closeModal },
      {
        label: "Reiniciar",
        className: "mini-btn red",
        onClick: async () => {
          closeModal();
          await resetSarcDemo();
        }
      }
    ]
  });
}

/**
 * Abre el modal de edición de perfil.
 */
function openProfileEditor() {
  const user = state.db.user;

  showModal({
    title: "Editar Perfil",
    icon: "info",
    customHtml: `
      <div class="edit-grid">
        <div class="field-row">
          <strong>Cambiar imagen:</strong>
          <div class="file-row">
            <button class="file-select-btn" type="button" id="avatarFileButton">Seleccionar archivo</button>
            <span id="avatarFileLabel">Sin archivo</span>
            <input id="avatarFileInput" type="file" accept="image/*" hidden>
          </div>
        </div>
        <div class="field-row"><strong>Actualizar contraseña</strong></div>
        <div class="field-row">
          <label for="currentPassword">Contraseña actual:</label>
          <input id="currentPassword" type="password">
        </div>
        <div class="field-row">
          <label for="newProfilePassword">Contraseña nueva:</label>
          <input id="newProfilePassword" type="password">
        </div>
        <div class="field-row">
          <label for="confirmProfilePassword">Confirmar contraseña:</label>
          <input id="confirmProfilePassword" type="password">
        </div>
        <div class="field-row">
          <strong>Modalidad:</strong>
          <div class="radio-stack">
            ${["Virtual", "Presencial", "Híbrido"].map((option) => `
              <label>
                <input type="radio" name="profileModality" value="${option}" ${user.modality === option ? "checked" : ""}>
                <span>${option}</span>
              </label>
            `).join("")}
          </div>
        </div>
      </div>
    `,
    actions: [
      { label: "Cancelar", className: "mini-btn", onClick: closeModal },
      { label: "Actualizar", className: "mini-btn green", onClick: submitProfileUpdate }
    ],
    onRender: bindProfileModalEvents
  });
}

/**
 * Enlaza el selector visual de archivo para avatar.
 */
function bindProfileModalEvents() {
  const trigger = document.getElementById("avatarFileButton");
  const input = document.getElementById("avatarFileInput");
  const label = document.getElementById("avatarFileLabel");

  trigger.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    label.textContent = file ? file.name : "Sin archivo";
  });
}

/**
 * Valida y guarda los cambios del perfil.
 */
async function submitProfileUpdate() {
  const currentPassword = document.getElementById("currentPassword").value.trim();
  const newPassword = document.getElementById("newProfilePassword").value.trim();
  const confirmPassword = document.getElementById("confirmProfilePassword").value.trim();
  const selectedModality =
    document.querySelector('input[name="profileModality"]:checked')?.value || state.db.user.modality;
  const avatarInput = document.getElementById("avatarFileInput");

  if ((newPassword || confirmPassword) && !currentPassword) {
    showToast("error", "Error de validación", "La contraseña actual no es correcta.");
    return;
  }

  if ((newPassword || confirmPassword) && newPassword !== confirmPassword) {
    showToast("error", "Error de validación", "Las nuevas contraseñas no coinciden.");
    return;
  }

  if (newPassword && newPassword.length < 6) {
    showToast("error", "Error de validación", "La nueva contraseña debe tener mínimo 6 caracteres.");
    return;
  }

  state.db.user.modality = selectedModality;
  if (newPassword) {
    try {
      await updateCurrentUserPassword(currentPassword, newPassword);
    } catch (error) {
      showToast("error", "Error de validación", "La contraseña actual no es correcta.");
      return;
    }
  }

  const file = avatarInput?.files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = () => {
      state.db.user.avatar = String(reader.result);
      finalizeProfileUpdate();
    };
    reader.readAsDataURL(file);
    return;
  }

  finalizeProfileUpdate();
}

/**
 * Persiste los cambios y refresca la vista de perfil.
 */
async function finalizeProfileUpdate() {
  await saveDatabase();
  closeModal();
  refreshProfile();
  showToast("success", "Perfil actualizado", "Los cambios fueron guardados correctamente.");
}

/**
 * Cierra la sesión actual y vuelve al login.
 */
async function logout() {
  saveSession({ authenticated: false });
  await logoutFirebaseUser();
  closeModal();
  navigate("login");
}
