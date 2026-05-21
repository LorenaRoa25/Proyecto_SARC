/**
 * Consultas y reglas de negocio relacionadas con cursos.
 */

import { saveDatabase, state } from "./data.js";
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
 * Filtra cursos sugeridos segun area, modalidad y estado de inscripcion.
 * Si un filtro queda sin resultados, conserva contenido visible con cursos
 * disponibles para no dejar la seccion vacia.
 * @returns {Array<object>}
 */
export function getFilteredCourses() {
  const suggestions = getPersonalizedCourseSuggestions();
  const filtered = suggestions.filter((course) => {
    const areaOk = isAllAreasFilter(state.filters.area) || sameAcademicValue(course.area, state.filters.area);
    const modalityOk = !state.filters.modality || sameAcademicValue(course.modality, state.filters.modality);
    return areaOk && modalityOk;
  });

  if (filtered.length) return filtered;

  const areaFallback = suggestions.filter((course) => {
    return isAllAreasFilter(state.filters.area) || sameAcademicValue(course.area, state.filters.area);
  });

  if (areaFallback.length) return areaFallback;
  return suggestions;
}

/**
 * Devuelve recomendaciones personalizadas sin cursos ya inscritos.
 * @param {number} limit
 * @returns {Array<object>}
 */
export function getPersonalizedCourseSuggestions(limit = Infinity) {
  const enrolledCourses = state.db.courses.filter(isCourseAlreadyEnrolled);
  const enrolledAreas = new Set(enrolledCourses.map((course) => course.area));
  const lowProgressAreas = new Set(
    enrolledCourses
      .filter((course) => Number(course.progress) < 70)
      .map((course) => course.area)
  );

  return state.db.courses
    .filter((course) => !isCourseAlreadyEnrolled(course))
    .map((course) => ({
      course,
      score: getSuggestionScore(course, enrolledAreas, lowProgressAreas)
    }))
    .sort((a, b) => b.score - a.score || a.course.name.localeCompare(b.course.name))
    .slice(0, limit)
    .map((item) => item.course);
}

/**
 * Indica si un curso ya forma parte del progreso del estudiante.
 * @param {object} course
 * @returns {boolean}
 */
export function isCourseAlreadyEnrolled(course) {
  return Boolean(course?.enrolled || course?.registered);
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
 * Controla la inscripcion de un curso y sus mensajes de resultado.
 * @param {string} courseId
 */
export async function handleEnrollment(courseId) {
  const course = getCourseById(courseId);
  if (!course) return;

  if (isCourseAlreadyEnrolled(course)) {
    showToast("info", "Curso ya inscrito", "Este curso ya forma parte de tu progreso academico.");
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
  course.lessons = course.lessons && course.lessons !== "0/0" ? course.lessons : "0/10";
  course.seats -= 1;
  await saveDatabase();
  refreshDashboard();
  playSuccessSound();

  showModal({
    title: "Inscripcion exitosa",
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
 * Enlaza botones de detalle e inscripcion dentro de una vista.
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

/**
 * Prioriza cursos relacionados con el estudiante autenticado.
 * @param {object} course
 * @param {Set<string>} enrolledAreas
 * @param {Set<string>} lowProgressAreas
 * @returns {number}
 */
function getSuggestionScore(course, enrolledAreas, lowProgressAreas) {
  const profileText = normalizeAcademicText([
    state.db.user.career,
    state.db.user.faculty,
    state.db.user.modality
  ].join(" "));

  let score = 0;
  if (sameAcademicValue(course.modality, state.db.user.modality)) score += 3;
  if (profileText.includes(normalizeAcademicText(course.area))) score += 3;
  if (hasAcademicValue(enrolledAreas, course.area)) score += 2;
  if (hasAcademicValue(lowProgressAreas, course.area)) score += 2;
  if (Number(course.seats) > 0) score += 1;
  return score;
}

/**
 * Revisa si un conjunto contiene un valor equivalente.
 * @param {Set<string>} values
 * @param {string} target
 * @returns {boolean}
 */
function hasAcademicValue(values, target) {
  return Array.from(values).some((value) => sameAcademicValue(value, target));
}

/**
 * Compara valores academicos tolerando acentos y textos con codificacion distinta.
 * @param {string} left
 * @param {string} right
 * @returns {boolean}
 */
function sameAcademicValue(left = "", right = "") {
  return normalizeAcademicText(left) === normalizeAcademicText(right) ||
    getAcademicToken(left) === getAcademicToken(right);
}

/**
 * Reconoce el filtro global de areas aunque venga con acentos o codificacion.
 * @param {string} value
 * @returns {boolean}
 */
function isAllAreasFilter(value = "") {
  const normalized = normalizeAcademicText(value);
  return !normalized || normalized.includes("todaslasareas");
}

/**
 * Obtiene una categoria estable para filtros conocidos.
 * @param {string} value
 * @returns {string}
 */
function getAcademicToken(value = "") {
  const normalized = normalizeAcademicText(value);
  if (normalized.includes("matem")) return "matematicas";
  if (normalized.includes("program")) return "programacion";
  if (normalized.includes("derecho")) return "derecho";
  if (normalized.includes("comunic")) return "comunicacion";
  if (normalized.includes("virtual")) return "virtual";
  if (normalized.includes("presencial")) return "presencial";
  if (normalized.includes("hibr")) return "hibrido";
  return normalized;
}

/**
 * Normaliza textos de filtros guardados en el estado o provenientes del HTML.
 * @param {string} value
 * @returns {string}
 */
function normalizeAcademicText(value = "") {
  return String(value)
    .replace(/ÃƒÂ¡|Ã¡/g, "a")
    .replace(/ÃƒÂ©|Ã©/g, "e")
    .replace(/ÃƒÂ­|Ã­/g, "i")
    .replace(/ÃƒÂ³|Ã³/g, "o")
    .replace(/ÃƒÂº|Ãº/g, "u")
    .replace(/ÃƒÂ±|Ã±/g, "n")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
}
