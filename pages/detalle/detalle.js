/**
 * Vista Detalle: muestra datos de un curso y permite inscripción.
 */

import { state } from "../../shared/js/data.js";
import { bindCourseActions, getCourseById } from "../../shared/js/courses.js";
import { navigate } from "../../shared/js/navigation.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";

/**
 * Renderiza el detalle del curso actual.
 * @param {HTMLElement} container
 */
export async function renderDetail(container) {
  const template = await loadTemplate("pages/detalle/detalle.html");
  const course = getCourseById(state.currentDetailId) || state.db.courses[0];

  container.innerHTML = interpolate(template, {
    courseId: course.id,
    courseName: course.name,
    description: course.description,
    duration: course.duration,
    level: course.level,
    enrollClass: course.registered ? "gray" : "green",
    enrollLabel: course.registered ? "INSCRITO" : "INSCRIBIRSE",
    disabled: course.registered ? "disabled" : ""
  });

  bindDetailEvents(container);
}

/**
 * Registra eventos de volver e inscripción.
 * @param {HTMLElement} container
 */
function bindDetailEvents(container) {
  container.querySelector("#detailBackButton").addEventListener("click", () => navigate("recomendaciones"));
  bindCourseActions(container);
}
