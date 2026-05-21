/**
 * Vista Detalle: muestra datos de un curso y permite inscripción.
 */

import { state } from "../../shared/js/data.js";
import { bindCourseActions, getCourseById, isCourseAlreadyEnrolled } from "../../shared/js/courses.js";
import { navigate } from "../../shared/js/navigation.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";

/**
 * Renderiza el detalle del curso actual.
 * @param {HTMLElement} container
 */
export async function renderDetail(container) {
  const template = await loadTemplate("pages/detalle/detalle.html");
  const course = getCourseById(state.currentDetailId) || state.db.courses[0];
  const alreadyEnrolled = isCourseAlreadyEnrolled(course);

  container.innerHTML = interpolate(template, {
    courseId: course.id,
    courseName: course.name,
    description: course.description,
    duration: course.duration,
    level: course.level,
    enrollClass: alreadyEnrolled ? "gray" : "green",
    enrollLabel: alreadyEnrolled ? "INSCRITO" : "INSCRIBIRSE",
    disabled: alreadyEnrolled ? "disabled" : ""
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
