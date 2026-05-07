/**
 * Vista Inicio: muestra cursos sugeridos y tareas del asistente.
 */

import { CORE_COURSE_IDS, saveDatabase, state } from "../../shared/js/data.js";
import { bindCourseActions } from "../../shared/js/courses.js";
import { interpolate, loadTemplate } from "../../shared/js/template-loader.js";

/**
 * Renderiza la pantalla de inicio.
 * @param {HTMLElement} container
 */
export async function renderHome(container) {
  const template = await loadTemplate("pages/inicio/inicio.html");
  const visibleHomeCourses = state.db.courses.filter((course) => CORE_COURSE_IDS.includes(course.id));

  container.innerHTML = interpolate(template, {
    courseButtons: renderCourseButtons(visibleHomeCourses),
    assistantTasks: renderAssistantTasks()
  });

  bindHomeEvents(container);
}

/**
 * Crea los botones de cursos sugeridos.
 * @param {Array<object>} courses
 * @returns {string}
 */
function renderCourseButtons(courses) {
  return courses
    .map((course) => `<button type="button" data-detail="${course.id}">○ ${course.name}</button>`)
    .join("");
}

/**
 * Crea los checks del asistente virtual.
 * @returns {string}
 */
function renderAssistantTasks() {
  return state.db.assistantTasks
    .map((task) => `
      <label class="assistant-item">
        <input type="checkbox" data-task-id="${task.id}" ${task.done ? "checked" : ""}>
        <span>${task.label}</span>
      </label>
    `)
    .join("");
}

/**
 * Registra eventos de cursos y tareas del asistente.
 * @param {HTMLElement} container
 */
function bindHomeEvents(container) {
  bindCourseActions(container);

  container.querySelectorAll("[data-task-id]").forEach((checkbox) => {
    checkbox.addEventListener("change", async () => {
      const task = state.db.assistantTasks.find((item) => item.id === checkbox.dataset.taskId);
      if (!task) return;

      task.done = checkbox.checked;
      await saveDatabase();
    });
  });
}
