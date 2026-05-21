/**
 * Carga y procesa fragmentos HTML externos por vista.
 */

const templateCache = new Map();

/**
 * Carga una plantilla HTML desde el proyecto y la almacena en memoria.
 * @param {string} path
 * @returns {Promise<string>}
 */
export async function loadTemplate(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`No se pudo cargar la plantilla: ${path}`);
  }

  const html = await response.text();
  templateCache.set(path, html);
  return html;
}

/**
 * Reemplaza llaves dobles simples en plantillas HTML.
 * @param {string} template
 * @param {Record<string, string|number>} values
 * @returns {string}
 */
export function interpolate(template, values = {}) {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return Object.prototype.hasOwnProperty.call(values, key) ? String(values[key]) : "";
  });
}
