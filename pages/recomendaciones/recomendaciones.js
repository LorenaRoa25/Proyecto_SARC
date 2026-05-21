/**
 * Vista Recomendaciones: catalogo personalizado con filtros e inscripcion.
 */

import { state } from "../../shared/js/data.js";
import { bindCourseActions, getFilteredCourses } from "../../shared/js/courses.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";

/**
 * Renderiza la vista de recomendaciones.
 * @param {HTMLElement} container
 */
export async function renderRecommendations(container) {
  const template = await loadTemplate("pages/recomendaciones/recomendaciones.html");
  const courses = getFilteredCourses();

  container.innerHTML = interpolate(template, {
    courseList: renderCourseList(courses),
    areaMatematicas: selected(state.filters.area, "MatemÃ¡ticas"),
    areaProgramacion: selected(state.filters.area, "ProgramaciÃ³n"),
    areaDerecho: selected(state.filters.area, "Derecho"),
    areaComunicacion: selected(state.filters.area, "ComunicaciÃ³n"),
    areaTodas: selected(state.filters.area, "Todas las Ã¡reas"),
    modalityVirtual: selected(state.filters.modality, "Virtual"),
    modalityPresencial: selected(state.filters.modality, "Presencial"),
    modalityHibrido: selected(state.filters.modality, "HÃ­brido")
  });

  bindRecommendationEvents(container);
}

/**
 * Renderiza tarjetas de cursos filtrados.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderCourseList(courses) {
  if (!courses.length) {
    return `
      <div class="recommendation-empty">
        <strong>No hay nuevos cursos para esos filtros.</strong>
        <span>Prueba otra area o modalidad para ver alternativas disponibles.</span>
      </div>
    `;
  }

  return courses
    .map((course) => `
      <article class="course-card">
        <div class="course-card-head">
          <div class="course-icon ${getColorClass(course.color)}">${escapeHtml(course.icon)}</div>
          <div>
            <h3>${escapeHtml(course.name)}</h3>
            <p>${escapeHtml(course.area)} &middot; ${escapeHtml(course.modality)}</p>
          </div>
        </div>

        <p class="course-description">${escapeHtml(course.description)}</p>

        <div class="course-meta">
          <span>${escapeHtml(course.duration)}</span>
          <span>${escapeHtml(course.level)}</span>
          <span>${Number(course.seats) > 0 ? `${course.seats} cupos` : "Sin cupos"}</span>
        </div>

        <div class="course-progress-hint">
          <span>Recomendado segun tu perfil academico</span>
        </div>

        <div class="course-actions">
          <button class="mock-btn blue" type="button" data-detail="${escapeHtml(course.id)}">Ver detalles</button>
          <button class="mock-btn ${Number(course.seats) > 0 ? "green" : "gray"}" type="button" data-enroll="${escapeHtml(course.id)}">
            ${Number(course.seats) > 0 ? "INSCRIBIRSE" : "SIN CUPOS"}
          </button>
        </div>
      </article>
    `)
    .join("");
}

/**
 * Devuelve selected si la opcion coincide con el filtro.
 * @param {string} current
 * @param {string} expected
 * @returns {string}
 */
function selected(current, expected) {
  return current === expected ? "selected" : "";
}

/**
 * Enlaza filtros y botones del catalogo.
 * @param {HTMLElement} container
 */
function bindRecommendationEvents(container) {
  container.querySelector("#filterArea").addEventListener("change", (event) => {
    state.filters.area = event.target.value;
    renderRecommendations(container);
  });

  container.querySelector("#filterModality").addEventListener("change", (event) => {
    state.filters.modality = event.target.value;
    renderRecommendations(container);
  });

  bindCourseActions(container);
}

/**
 * Evita que datos del curso se interpreten como HTML.
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
