/**
 * Vista Inicio: muestra cursos sugeridos y asistente virtual personalizado.
 */

import { state } from "../../shared/js/data.js";
import { bindCourseActions, getPersonalizedCourseSuggestions } from "../../shared/js/courses.js";
import { getCourseProgressSummary } from "../../shared/js/progress-utils.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";

/**
 * Renderiza la pantalla de inicio.
 * @param {HTMLElement} container
 */
export async function renderHome(container) {
  const template = await loadTemplate("pages/inicio/inicio.html");
  const visibleHomeCourses = getPersonalizedCourseSuggestions(3);

  container.innerHTML = interpolate(template, {
    studentName: state.db.user.name || "Estudiante",
    courseButtons: renderCourseButtons(visibleHomeCourses),
    assistantRecommendations: renderAssistantRecommendations()
  });

  bindHomeEvents(container);
}

/**
 * Crea los botones de cursos sugeridos.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderCourseButtons(courses) {
  if (!courses.length) {
    return `<div class="home-empty">No hay nuevos cursos disponibles para tu perfil en este momento.</div>`;
  }

  return courses
    .map((course) => `
      <button class="home-course-button" type="button" data-detail="${escapeHtml(course.id)}">
        <span class="home-course-icon ${getColorClass(course.color)}">${escapeHtml(course.icon)}</span>
        <span>
          <strong>${escapeHtml(course.name)}</strong>
          <small>${escapeHtml(course.area)} &middot; ${escapeHtml(course.modality)}</small>
        </span>
      </button>
    `)
    .join("");
}

/**
 * Genera mensajes del asistente basados en el perfil y progreso del usuario.
 * @returns {string}
 */
function renderAssistantRecommendations() {
  const messages = buildAssistantMessages();

  return `
    <div class="assistant-chat">
      ${messages.map((message) => `
        <div class="assistant-message ${message.type}">
          <span class="assistant-badge">${message.badge}</span>
          <p>${escapeHtml(message.text)}</p>
        </div>
      `).join("")}
    </div>
  `;
}

/**
 * Construye mensajes personalizados sin repetir exactamente lo mismo para todos.
 * @returns {Array<{type:string,badge:string,text:string}>}
 */
function buildAssistantMessages() {
  const user = state.db.user;
  const enrolledCourses = state.db.courses.filter((course) => course.enrolled || course.registered);
  const suggestions = getPersonalizedCourseSuggestions(2);
  const messages = [];

  messages.push({
    type: "profile",
    badge: "Perfil",
    text: `Hola ${user.name || "estudiante"}. Revisare tus cursos de ${user.career || "tu programa"} en modalidad ${user.modality || "registrada"}.`
  });

  if (enrolledCourses.length) {
    const lowest = enrolledCourses
      .map((course) => ({ course, summary: getCourseProgressSummary(course) }))
      .sort((a, b) => a.summary.progress - b.summary.progress)[0];

    messages.push({
      type: "progress",
      badge: "Avance",
      text: `Tu seguimiento mas importante ahora es ${lowest.course.name}: ${lowest.summary.progress}% de avance y ${lowest.summary.completedLessons} de ${lowest.summary.totalLessons} actividades completadas.`
    });
  } else {
    messages.push({
      type: "progress",
      badge: "Avance",
      text: "Aun no tienes cursos inscritos. Inscribirte en un curso permitira activar tu seguimiento academico."
    });
  }

  if (suggestions.length) {
    messages.push({
      type: "suggestion",
      badge: "Sugerencia",
      text: `Segun tu perfil, puedes revisar ${suggestions.map((course) => course.name).join(" o ")} como nueva opcion academica.`
    });
  }

  return messages;
}

/**
 * Registra eventos de cursos y tareas del asistente.
 * @param {HTMLElement} container
 */
function bindHomeEvents(container) {
  bindCourseActions(container);
}

/**
 * Evita que datos del usuario o curso se interpreten como HTML.
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
