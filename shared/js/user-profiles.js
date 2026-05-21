/**
 * Reglas compartidas para perfiles especiales del sistema.
 */

export const DEMO_USER_EMAIL = "lorena.roa@unisabaneta.edu.co";
export const DEMO_USER_EMAIL_ALIASES = [
  DEMO_USER_EMAIL,
  "lorena.roa.196@unisabaneta.edu.co"
];

/**
 * Identifica si el correo pertenece al usuario demo autorizado.
 * @param {string} email
 * @returns {boolean}
 */
export function isAuthorizedDemoEmail(email) {
  const normalizedEmail = String(email || "").trim().toLowerCase();
  return DEMO_USER_EMAIL_ALIASES.includes(normalizedEmail);
}
