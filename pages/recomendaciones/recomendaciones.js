/**
 * Vista Recomendaciones: catálogo con filtros e inscripción.
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

  container.innerHTML = interpolate(template, {
    courseList: renderCourseList(getFilteredCourses()),
    areaMatematicas: selected(state.filters.area, "Matemáticas"),
    areaProgramacion: selected(state.filters.area, "Programación"),
    areaDerecho: selected(state.filters.area, "Derecho"),
    areaComunicacion: selected(state.filters.area, "Comunicación"),
    areaTodas: selected(state.filters.area, "Todas las áreas"),
    modalityVirtual: selected(state.filters.modality, "Virtual"),
    modalityPresencial: selected(state.filters.modality, "Presencial"),
    modalityHibrido: selected(state.filters.modality, "Híbrido")
  });

  bindRecommendationEvents(container);
}

/**
 * Renderiza las filas de cursos filtrados.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderCourseList(courses) {
  return courses
    .map((course) => `
      <div class="course-item">
        <div class="course-name"><strong>Curso:</strong> ${course.name}</div>
        <div class="course-actions">
          <button class="mock-btn blue" type="button" data-detail="${course.id}">Ver detalles</button>
          <button class="mock-btn ${course.registered ? "gray" : "green"}" type="button" data-enroll="${course.id}" ${course.registered ? "disabled" : ""}>
            ${course.registered ? "INSCRITO" : "INSCRIBIRSE"}
          </button>
        </div>
      </div>
    `)
    .join("");
}

/**
 * Devuelve selected si la opción coincide con el filtro.
 * @param {string} current
 * @param {string} expected
 * @returns {string}
 */
function selected(current, expected) {
  return current === expected ? "selected" : "";
}

/**
 * Enlaza filtros y botones del catálogo.
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
