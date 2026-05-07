/**
 * Consultas y reglas de negocio relacionadas con cursos.
 */

import { CORE_COURSE_IDS, saveDatabase, state } from "./data.js";
import { openDetail } from "./navigation.js";
import { playSuccessSound } from "./sound.js";
import { closeModal, showModal, showToast } from "../components/feedback.js";

let refreshDashboard = () => {};

/**
 * Registra el callback de renderizado del dashboard.
 * @param {Function} callback
 */
export function setDashboardRefresh(callback) {
  refreshDashboard = callback;
}

/**
 * Filtra cursos sugeridos según área y modalidad.
 * @returns {Array<object>}
 */
export function getFilteredCourses() {
  return state.db.courses.filter((course) => {
    if (!CORE_COURSE_IDS.includes(course.id)) return false;

    const areaOk =
      !state.filters.area ||
      state.filters.area === "Todas las áreas" ||
      course.area === state.filters.area;
    const modalityOk = !state.filters.modality || course.modality === state.filters.modality;

    return areaOk && modalityOk;
  });
}

/**
 * Busca un curso por identificador.
 * @param {string} id
 * @returns {object|undefined}
 */
export function getCourseById(id) {
  return state.db.courses.find((course) => course.id === id);
}

/**
 * Controla la inscripción de un curso y sus mensajes de resultado.
 * @param {string} courseId
 */
export async function handleEnrollment(courseId) {
  const course = getCourseById(courseId);
  if (!course) return;

  if (course.registered) {
    showToast("info", "Curso ya inscrito", "Este curso ya aparece como inscrito.");
    return;
  }

  if (course.seats <= 0) {
    showModal({
      title: "No hay cupos disponibles",
      icon: "error",
      text: "Cursos alternativos:",
      list: course.alternatives,
      actions: [{ label: "Volver a cursos", className: "wide-btn", onClick: closeModal }]
    });
    return;
  }

  course.enrolled = true;
  course.registered = true;
  course.progress = 5;
  course.status = "En progreso";
  course.lastAccess = "Hoy";
  course.seats -= 1;
  await saveDatabase();
  refreshDashboard();
  playSuccessSound();

  showModal({
    title: "Inscripción exitosa",
    icon: "success",
    text: "Te has inscrito correctamente",
    actions: [
      {
        label: "Volver al Inicio",
        className: "mini-btn",
        onClick: () => {
          closeModal();
          window.location.hash = "inicio";
        }
      },
      {
        label: "Ir a Mi progreso",
        className: "mini-btn green",
        onClick: () => {
          closeModal();
          window.location.hash = "progreso";
        }
      }
    ]
  });
}

/**
 * Enlaza botones de detalle e inscripción dentro de una vista.
 * @param {ParentNode} container
 */
export function bindCourseActions(container) {
  container.querySelectorAll("[data-detail]").forEach((button) => {
    button.addEventListener("click", () => openDetail(button.dataset.detail));
  });

  container.querySelectorAll("[data-enroll]").forEach((button) => {
    button.addEventListener("click", () => handleEnrollment(button.dataset.enroll));
  });
}
