/**
 * Utilidades compartidas para mostrar progreso academico de forma coherente
 * en pantalla, modal y reporte PDF.
 */

/**
 * Resume los datos de seguimiento disponibles para un curso.
 * @param {object} course
 * @returns {{progress:number, completedLessons:number, totalLessons:number, contentViewed:number, statusLabel:string, statusClass:string}}
 */
export function getCourseProgressSummary(course = {}) {
  const { completed, total } = parseLessons(course.lessons);
  const progress = clampPercent(course.progress);
  const contentViewed = total > 0 ? Math.round((completed / total) * 100) : progress;
  const visualStatus = getVisualStatus(progress, course.status);

  return {
    progress,
    completedLessons: completed,
    totalLessons: total || 1,
    contentViewed: clampPercent(contentViewed),
    statusLabel: visualStatus.label,
    statusClass: visualStatus.className
  };
}

/**
 * Interpreta textos como "7/10" sin exponer calculos de notas.
 * @param {string} lessons
 * @returns {{completed: number, total: number}}
 */
export function parseLessons(lessons = "0/1") {
  const match = String(lessons).match(/(\d+)\s*\/\s*(\d+)/);
  if (!match) return { completed: 0, total: 1 };

  const completed = Number(match[1]) || 0;
  const total = Number(match[2]) || 1;
  return { completed: Math.min(completed, total), total };
}

/**
 * Normaliza valores de avance para que la interfaz siempre sea estable.
 * @param {number|string} value
 * @returns {number}
 */
export function clampPercent(value) {
  return Math.max(0, Math.min(100, Math.round(Number(value) || 0)));
}

/**
 * Define etiquetas visuales de estado sin depender de notas manuales.
 * @param {number} progress
 * @param {string} fallbackStatus
 * @returns {{label: string, className: string}}
 */
export function getVisualStatus(progress, fallbackStatus) {
  if (progress >= 100) return { label: "Completado", className: "completed" };
  if (progress >= 70) return { label: "Avance alto", className: "high" };
  if (progress >= 35) return { label: fallbackStatus || "En progreso", className: "active" };
  return { label: "Inicio del curso", className: "starting" };
}
