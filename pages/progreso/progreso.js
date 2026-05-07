/**
 * Vista Progreso: muestra avances y genera reportes por curso.
 */

import { state } from "../../shared/js/data.js";
import { getCourseById } from "../../shared/js/courses.js";
import { downloadReport } from "../../shared/js/pdf.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";
import { closeModal, showModal } from "../../shared/components/feedback.js";

/**
 * Renderiza la vista de progreso.
 * @param {HTMLElement} container
 */
export async function renderProgress(container) {
  const template = await loadTemplate("pages/progreso/progreso.html");
  const enrolledCourses = state.db.courses.filter((course) => course.enrolled);

  container.innerHTML = interpolate(template, {
    progressRows: renderProgressRows(enrolledCourses)
  });

  bindProgressEvents(container);
  animateProgressBars(container);
}

/**
 * Construye las filas de progreso.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderProgressRows(courses) {
  return courses
    .map((course) => `
      <div class="progress-row">
        <div class="progress-icon">${course.icon}</div>
        <div class="progress-info">
          <div class="progress-line-top">
            <span class="progress-title">${formatProgressTitle(course.name)}:</span>
            <span class="progress-track">
              <span class="progress-fill ${course.color}" data-width="${course.progress}%"></span>
            </span>
            <span>${course.progress}%</span>
          </div>
          <div><strong>Estado:</strong> ${course.status}</div>
          <div><strong>Último acceso:</strong> ${course.lastAccess}</div>
        </div>
        <button class="mock-btn blue progress-btn" type="button" data-report="${course.id}">Ver reporte detallado</button>
      </div>
    `)
    .join("");
}

/**
 * Ajusta el nombre visible del curso en la barra de progreso.
 * @param {string} name
 * @returns {string}
 */
function formatProgressTitle(name) {
  return name.replace(" Básicas", "").replace(" Nivel", "");
}

/**
 * Registra eventos de reportes detallados.
 * @param {HTMLElement} container
 */
function bindProgressEvents(container) {
  container.querySelectorAll("[data-report]").forEach((button) => {
    button.addEventListener("click", () => openReport(button.dataset.report));
  });
}

/**
 * Anima las barras después de pintar el DOM.
 * @param {HTMLElement} container
 */
function animateProgressBars(container) {
  requestAnimationFrame(() => {
    container.querySelectorAll(".progress-fill[data-width]").forEach((bar) => {
      bar.style.width = bar.dataset.width;
    });
  });
}

/**
 * Abre el modal con el reporte detallado del curso.
 * @param {string} courseId
 */
function openReport(courseId) {
  const course = getCourseById(courseId);
  if (!course) return;

  showModal({
    title: "Reporte detallado de progreso",
    icon: "none",
    className: "report-modal",
    customHtml: `
      <div class="modal-report-grid">
        <div class="report-line"><strong>Curso:</strong> ${course.name}</div>
        <div class="report-line"><strong>Lecciones completadas:</strong> ${course.lessons}</div>
        <div class="report-line"><strong>Tiempo invertido:</strong> ${course.timeSpent}</div>
        <div class="report-line"><strong>Evaluación promedio:</strong> ${course.average}</div>
        <div class="report-line"><strong>Recomendación:</strong> ${course.recommendation}</div>
      </div>
    `,
    actions: [
      { label: "Volver", className: "mini-btn", onClick: closeModal },
      { label: "Descargar", className: "mini-btn green", onClick: () => downloadReport(course) }
    ]
  });
}
