/**
 * Componentes de feedback: enlaces estáticos, modales y notificaciones.
 */

const modalRoot = document.getElementById("modalRoot");
const toastContainer = document.getElementById("toastContainer");

/**
 * Muestra un aviso para enlaces visuales del prototipo.
 * @param {Event} event
 */
export function handleStaticLink(event) {
  event.preventDefault();
  showToast("info", "Enlace visual", "Este enlace forma parte del mockup del sistema.");
}

/**
 * Enlaza todos los links estáticos dentro de un contenedor.
 * @param {ParentNode} container
 */
export function bindStaticLinks(container = document) {
  container.querySelectorAll("[data-static-link]").forEach((link) => {
    link.onclick = handleStaticLink;
  });
}

/**
 * Abre un modal reutilizable con acciones configurables.
 * @param {object} config
 */
export function showModal({
  title,
  icon = "info",
  text = "",
  list = [],
  customHtml = "",
  actions = [],
  onRender,
  className = ""
}) {
  const iconText = icon === "success" ? "✓" : icon === "error" ? "" : icon === "none" ? "" : "✎";

  modalRoot.innerHTML = `
    <div class="modal-overlay">
      <div class="modal-card ${className}">
        <div class="modal-head">
          <span class="modal-inline-icon ${icon}">${iconText}</span>
          <h3>${title}</h3>
          <button class="modal-close-compact" type="button" aria-label="Cerrar">×</button>
        </div>
        <div class="modal-body">
          ${text ? `<div class="modal-copy">${text}</div>` : ""}
          ${customHtml}
          ${list.length ? `<ul class="modal-list">${list.map((item) => `<li>${item}</li>`).join("")}</ul>` : ""}
        </div>
        <div class="modal-actions">
          ${actions.map((action, index) => `<button class="${action.className}" type="button" data-action-index="${index}">${action.label}</button>`).join("")}
        </div>
      </div>
    </div>
  `;

  modalRoot.querySelector(".modal-close-compact").addEventListener("click", closeModal);
  modalRoot.querySelectorAll("[data-action-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const action = actions[Number(button.dataset.actionIndex)];
      if (action?.onClick) action.onClick();
    });
  });

  if (typeof onRender === "function") onRender();
}

/**
 * Cierra el modal activo.
 */
export function closeModal() {
  modalRoot.innerHTML = "";
}

/**
 * Muestra una notificación temporal.
 * @param {"success"|"error"|"info"} type
 * @param {string} title
 * @param {string} text
 */
export function showToast(type, title, text) {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<strong>${title}</strong><span>${text}</span>`;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 2800);
}
