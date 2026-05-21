/**
 * Vista Progreso: seguimiento academico automatico por curso inscrito.
 * El avance se presenta desde actividades completadas, recursos consultados
 * y datos de progreso almacenados en la base de datos.
 */

import { state } from "../../shared/js/data.js";
import { getCourseById } from "../../shared/js/courses.js";
import { downloadReport } from "../../shared/js/pdf.js";
import { getCourseProgressSummary } from "../../shared/js/progress-utils.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";
import { closeModal, showModal } from "../../shared/components/feedback.js";

/**
 * Renderiza la vista principal de progreso.
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
 * Construye tarjetas simples de avance para los cursos inscritos.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderProgressRows(courses) {
  if (!courses.length) {
    return `
      <div class="progress-empty">
        <strong>No tienes cursos inscritos.</strong>
        <span>Cuando te inscribas en un curso, SARC mostrara aqui tu avance academico.</span>
      </div>
    `;
  }

  return courses.map((course) => {
    const summary = getCourseProgressSummary(course);
    const courseId = escapeHtml(course.id);
    const courseName = escapeHtml(course.name);
    const courseArea = escapeHtml(course.area);
    const courseModality = escapeHtml(course.modality);
    const courseIcon = escapeHtml(course.icon);
    const lastAccess = escapeHtml(course.lastAccess);
    const colorClass = getColorClass(course.color);

    return `
      <article class="progress-course-card">
        <div class="progress-card-main">
          <div class="progress-icon ${colorClass}">${courseIcon}</div>

          <div class="progress-info">
            <div class="progress-card-header">
              <div>
                <h3>${courseName}</h3>
                <p>${courseArea} &middot; ${courseModality}</p>
              </div>
              <span class="status-pill ${summary.statusClass}">${escapeHtml(summary.statusLabel)}</span>
            </div>

            <div class="progress-meter-row">
              <span class="progress-track" aria-label="Avance del curso ${course.progress}%">
                <span class="progress-fill ${colorClass}" data-width="${summary.progress}%"></span>
              </span>
              <strong>${summary.progress}%</strong>
            </div>

            <div class="progress-metrics">
              <div class="metric-card">
                <span class="metric-label">Actividades completadas</span>
                <strong>${summary.completedLessons} de ${summary.totalLessons}</strong>
              </div>
              <div class="metric-card">
                <span class="metric-label">Contenido consultado</span>
                <strong>${summary.contentViewed}%</strong>
              </div>
              <div class="metric-card">
                <span class="metric-label">Ultimo acceso</span>
                <strong>${lastAccess}</strong>
              </div>
            </div>

            <div class="progress-explanation">
              <strong>Origen del avance:</strong>
              actividades completadas, recursos consultados y seguimiento academico automatico registrado por SARC.
            </div>
          </div>

          <button class="mock-btn blue progress-btn" type="button" data-report="${courseId}">Ver reporte detallado</button>
        </div>
      </article>`;
  }).join("");
}

/**
 * Evita que datos del curso se interpreten como marcado HTML.
 * @param {string|number} value
 * @returns {string}
 */
function escapeHtml(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * Restringe las clases visuales a la paleta definida por SARC.
 * @param {string} color
 * @returns {string}
 */
function getColorClass(color = "blue") {
  return ["blue", "red", "green"].includes(color) ? color : "blue";
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
 * Anima las barras despues de pintar el DOM.
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

  const summary = getCourseProgressSummary(course);

  showModal({
    title: "Reporte detallado de progreso",
    icon: "none",
    className: "report-modal progress-report-modal",
    customHtml: `
      <div class="modal-report-grid">
        <div class="report-line"><strong>Curso:</strong> ${escapeHtml(course.name)}</div>
        <div class="report-line"><strong>Estado:</strong> ${escapeHtml(summary.statusLabel)}</div>
        <div class="report-line"><strong>Avance general:</strong> ${summary.progress}%</div>
        <div class="report-line"><strong>Actividades completadas:</strong> ${summary.completedLessons} de ${summary.totalLessons}</div>
        <div class="report-line"><strong>Contenido consultado:</strong> ${summary.contentViewed}%</div>
        <div class="report-line"><strong>Tiempo invertido:</strong> ${escapeHtml(course.timeSpent)}</div>
        <div class="report-line"><strong>Ultimo acceso:</strong> ${escapeHtml(course.lastAccess)}</div>
        <div class="report-note">
          El porcentaje mostrado representa el avance general del estudiante en el curso
          segun actividades completadas, recursos consultados y progreso almacenado en la base de datos.
        </div>
      </div>
    `,
    actions: [
      { label: "Volver", className: "mini-btn", onClick: closeModal },
      { label: "Descargar PDF", className: "mini-btn green", onClick: () => downloadReport(course) }
    ]
  });
}
