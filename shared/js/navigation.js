/**
 * Funciones de navegación hash para la aplicación SARC.
 */

import { state } from "./data.js";

/**
 * Navega a una ruta interna del sistema.
 * @param {string} route
 */
export function navigate(route) {
  window.location.hash = route;
}

/**
 * Abre el detalle de un curso específico.
 * @param {string} courseId
 */
export function openDetail(courseId) {
  state.currentDetailId = courseId;
  window.location.hash = `detalle/${courseId}`;
}
