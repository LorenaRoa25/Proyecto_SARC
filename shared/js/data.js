/**
 * Centraliza datos demo, estado global y persistencia Firebase de SARC.
 * Incluye actividades evaluativas, cálculo dinámico de notas y helpers académicos.
 */

// Polyfill para navegadores antiguos (Safari <15.4, Chrome <98)
if (typeof structuredClone !== "function") {
  self.structuredClone = function structuredClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  };
}

import {
  getCurrentFirebaseUser,
  initializeFirebase,
  loadUserData,
  logoutFirebaseUser,
  resetUserData,
  saveUserData,
  waitForAuthUser
} from "./firebase-service.js";
import { DEMO_USER_EMAIL, isAuthorizedDemoEmail } from "./user-profiles.js";

export const CORE_COURSE_IDS = ["matematicas", "programacion", "ingles"];

export const INSTITUTIONAL_DOMAIN = "@unisabaneta.edu.co";

const AVATAR_PLACEHOLDER =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="215" height="206" viewBox="0 0 215 206">
      <rect width="215" height="206" rx="8" fill="#FFFFFF"/>
      <rect x="16" y="16" width="183" height="174" rx="8" fill="#085394"/>
      <circle cx="107.5" cy="75" r="30" fill="#FFFFFF"/>
      <path d="M55 158c16-29 34-43 52.5-43S144 129 160 158" fill="#FFFFFF"/>
    </svg>
  `);

/**
 * Plantilla de actividades de seguimiento para conservar compatibilidad
 * con datos guardados en versiones anteriores.
 */
function buildDefaultActivities() {
  return [
    { id: "act1", name: "Parcial 1", percentage: 30, grade: 0, maxGrade: 5 },
    { id: "act2", name: "Talleres", percentage: 20, grade: 0, maxGrade: 5 },
    { id: "act3", name: "Proyecto", percentage: 25, grade: 0, maxGrade: 5 },
    { id: "act4", name: "Participación", percentage: 25, grade: 0, maxGrade: 5 }
  ];
}

/**
 * Calcula la nota final ponderada a partir de las actividades.
 * @param {Array<{percentage: number, grade: number}>} activities
 * @returns {number} Nota final en escala de 0 a 5
 */
export function calculateFinalGrade(activities) {
  if (!Array.isArray(activities) || activities.length === 0) return 0;
  const total = activities.reduce((sum, act) => {
    return sum + (Number(act.grade) || 0) * (Number(act.percentage) || 0) / 100;
  }, 0);
  return Math.round(total * 100) / 100;
}

/**
 * Determina el estado académico según la nota final.
 * @param {number} grade Nota final (0-5)
 * @returns {{label: string, color: string, icon: string}}
 */
export function getAcademicStatus(grade) {
  if (grade >= 4.5) return { label: "Excelente", color: "#1b8a3d", icon: "🏆" };
  if (grade >= 4.0) return { label: "Sobresaliente", color: "#2e7d32", icon: "⭐" };
  if (grade >= 3.5) return { label: "Aprobado", color: "#6aa84f", icon: "✅" };
  if (grade >= 3.0) return { label: "En riesgo", color: "#e67e22", icon: "⚠️" };
  return { label: "Reprobado", color: "#cf2a27", icon: "❌" };
}

/**
 * Genera recomendaciones academicas basadas en el avance de cursos inscritos.
 * @param {Array<object>} courses
 * @returns {Array<{label: string, type: string}>}
 */
export function generateAcademicRecommendations(courses) {
  const enrolled = courses.filter(c => c.enrolled);
  if (enrolled.length === 0) return [];
  const recs = [];
  const progressItems = enrolled.map(c => ({ name: c.name, progress: Number(c.progress) || 0, course: c }));
  const avg = progressItems.reduce((sum, item) => sum + item.progress, 0) / progressItems.length;

  if (avg >= 75) {
    recs.push({ label: `Tu avance general es ${avg.toFixed(0)}%. Puedes revisar nuevas opciones complementarias.`, type: "success" });
  } else if (avg >= 40) {
    recs.push({ label: `Tu avance general es ${avg.toFixed(0)}%. Conviene mantener constancia en los cursos inscritos.`, type: "warning" });
  } else {
    recs.push({ label: `Tu avance general es ${avg.toFixed(0)}%. Prioriza completar actividades pendientes antes de sumar mas cursos.`, type: "error" });
  }

  const pending = progressItems.sort((a, b) => a.progress - b.progress)[0];
  if (pending) {
    recs.push({ label: `El curso que requiere mas atencion es ${pending.name}, con ${pending.progress}% de avance.`, type: "warning" });
  }

  return recs;
}

export const defaultDatabase = {
  user: {
    email: DEMO_USER_EMAIL,
    name: "Lorena Roa Rivera",
    faculty: "Ingeniería Informática",
    career: "Ingeniería Informática",
    semester: "8",
    modality: "Virtual",
    avatar: AVATAR_PLACEHOLDER,
    habeasDataAccepted: false
  },
  courses: [
    {
      id: "matematicas",
      name: "Matemáticas Básicas",
      area: "Matemáticas",
      modality: "Virtual",
      seats: 6,
      description: "Curso orientado al fortalecimiento de los fundamentos matemáticos mediante el estudio de operaciones y conceptos esenciales.",
      duration: "4 Semanas",
      level: "Básico",
      enrolled: true,
      progress: 70,
      status: "En progreso",
      lastAccess: "Hoy",
      lessons: "7/10",
      timeSpent: "12 horas",
      average: "85%",
      recommendation: "Reforzar ejercicios prácticos",
      icon: "⊞",
      color: "blue",
      alternatives: ["Matemáticas intermedio", "Refuerzo álgebra"],
      registered: false,
      activities: [
        { id: "act1", name: "Parcial 1", percentage: 30, grade: 4.2, maxGrade: 5 },
        { id: "act2", name: "Talleres", percentage: 20, grade: 4.5, maxGrade: 5 },
        { id: "act3", name: "Proyecto", percentage: 25, grade: 3.8, maxGrade: 5 },
        { id: "act4", name: "Participación", percentage: 25, grade: 5.0, maxGrade: 5 }
      ]
    },
    {
      id: "programacion",
      name: "Programación",
      area: "Programación",
      modality: "Híbrido",
      seats: 0,
      description: "Curso para introducir al estudiante en los fundamentos de la programación y el pensamiento lógico-computacional.",
      duration: "6 Semanas",
      level: "Básico - Intermedio",
      enrolled: true,
      progress: 40,
      status: "En progreso",
      lastAccess: "Hace 2 días",
      lessons: "4/10",
      timeSpent: "5 horas",
      average: "35%",
      recommendation: "Continuar práctica",
      icon: "</>",
      color: "red",
      alternatives: ["Curso en Front-end", "Curso Python"],
      registered: false,
      activities: [
        { id: "act1", name: "Parcial 1", percentage: 30, grade: 2.0, maxGrade: 5 },
        { id: "act2", name: "Talleres", percentage: 20, grade: 3.5, maxGrade: 5 },
        { id: "act3", name: "Proyecto", percentage: 25, grade: 1.5, maxGrade: 5 },
        { id: "act4", name: "Participación", percentage: 25, grade: 3.0, maxGrade: 5 }
      ]
    },
    {
      id: "ingles",
      name: "Inglés Nivel A2",
      area: "Comunicación",
      modality: "Virtual",
      seats: 0,
      description: "Curso para el desarrollo de habilidades comunicativas básicas en inglés, fortaleciendo comprensión y expresión oral y escrita.",
      duration: "8 Semanas",
      level: "A2 - Básico Alto",
      enrolled: true,
      progress: 95,
      status: "En progreso",
      lastAccess: "Hace 1 día",
      lessons: "9/10",
      timeSpent: "18 horas",
      average: "80%",
      recommendation: "Practicar Listening",
      icon: "📖",
      color: "green",
      alternatives: ["Inglés Nivel A1", "Inglés Nivel B1"],
      registered: false,
      activities: [
        { id: "act1", name: "Parcial 1", percentage: 30, grade: 4.0, maxGrade: 5 },
        { id: "act2", name: "Talleres", percentage: 20, grade: 4.8, maxGrade: 5 },
        { id: "act3", name: "Proyecto", percentage: 25, grade: 4.2, maxGrade: 5 },
        { id: "act4", name: "Participación", percentage: 25, grade: 4.5, maxGrade: 5 }
      ]
    },
    {
      id: "derecho-constitucional",
      name: "Derecho Constitucional",
      area: "Derecho",
      modality: "Presencial",
      seats: 8,
      description: "Curso orientado al estudio de los principios constitucionales, derechos fundamentales y organización del Estado colombiano.",
      duration: "5 Semanas",
      level: "Básico",
      enrolled: false,
      progress: 0,
      status: "Disponible",
      lastAccess: "Sin acceso",
      lessons: "0/8",
      timeSpent: "0 horas",
      average: "0%",
      recommendation: "Iniciar con lectura guiada de la Constitución",
      icon: "D",
      color: "blue",
      alternatives: ["Introducción al Derecho", "Derechos Humanos"],
      registered: false,
      activities: JSON.parse(JSON.stringify(buildDefaultActivities()))
    },
    {
      id: "comunicacion-efectiva",
      name: "Comunicación Efectiva",
      area: "Comunicación",
      modality: "Híbrido",
      seats: 7,
      description: "Curso diseñado para fortalecer la expresión oral, escrita y la comunicación asertiva en contextos académicos y profesionales.",
      duration: "4 Semanas",
      level: "Básico",
      enrolled: false,
      progress: 0,
      status: "Disponible",
      lastAccess: "Sin acceso",
      lessons: "0/6",
      timeSpent: "0 horas",
      average: "0%",
      recommendation: "Practicar presentaciones breves y redacción académica",
      icon: "CE",
      color: "green",
      alternatives: ["Técnicas de Oratoria", "Redacción Académica"],
      registered: false,
      activities: JSON.parse(JSON.stringify(buildDefaultActivities()))
    },
    {
      id: "algebra-lineal",
      name: "Álgebra Lineal",
      area: "Matemáticas",
      modality: "Virtual",
      seats: 9,
      description: "Curso para comprender matrices, vectores, sistemas lineales y su aplicación en ingeniería y ciencia de datos.",
      duration: "6 Semanas",
      level: "Intermedio",
      enrolled: false,
      progress: 0,
      status: "Disponible",
      lastAccess: "Sin acceso",
      lessons: "0/10",
      timeSpent: "0 horas",
      average: "0%",
      recommendation: "Repasar operaciones matriciales antes de iniciar",
      icon: "AL",
      color: "blue",
      alternatives: ["Refuerzo Álgebra", "Pensamiento Lógico"],
      registered: false,
      activities: JSON.parse(JSON.stringify(buildDefaultActivities()))
    },
    {
      id: "proyectos",
      name: "Formulación y Evaluación de Proyectos",
      area: "Programación",
      modality: "Híbrido",
      seats: 6,
      description: "Curso para estructurar, evaluar y presentar proyectos académicos con enfoque técnico, financiero y de impacto.",
      duration: "5 Semanas",
      level: "Intermedio",
      enrolled: false,
      progress: 0,
      status: "Disponible",
      lastAccess: "Sin acceso",
      lessons: "0/7",
      timeSpent: "0 horas",
      average: "0%",
      recommendation: "Iniciar con identificación del problema y objetivos",
      icon: "FP",
      color: "red",
      alternatives: ["Gestión de Proyectos", "Metodología de la Investigación"],
      registered: false,
      activities: JSON.parse(JSON.stringify(buildDefaultActivities()))
    }
  ],
  assistantTasks: [
    { id: "a1", label: "Refuerza Matemáticas", done: true },
    { id: "a2", label: "Tomar curso Python", done: true },
    { id: "a3", label: "Completa el curso de Inglés A2", done: true }
  ]
};

export const state = {
  route: "login",
  currentDetailId: "matematicas",
  filters: {
    area: "",
    modality: ""
  },
  db: null,
  session: null
};

/**
 * Inicializa Firebase antes de renderizar la aplicación.
 */
export async function initializeState() {
  await initializeFirebase();
  const user = await waitForAuthUser();
  state.session = loadSession(user);
  state.db = user ? await loadDatabaseForUser(user) : structuredClone(defaultDatabase);
}

/**
 * Carga Firestore para el usuario autenticado y actualiza el estado global.
 * @param {object} user
 * @returns {Promise<object>}
 */
export async function loadDatabaseForUser(user = getCurrentFirebaseUser()) {
  state.db = user ? await loadUserData(user, defaultDatabase, normalizeDatabase) : structuredClone(defaultDatabase);
  return state.db;
}

/**
 * Guarda la base de datos actual en Firestore.
 */
export async function saveDatabase() {
  const user = getCurrentFirebaseUser();
  if (!user) return;
  await saveUserData(user.uid, state.db);
}

/**
 * Carga una sesión vigente o devuelve una sesión no autenticada.
 * @returns {{authenticated: boolean, email?: string, userId?: string, loginAt?: number}}
 */
export function loadSession(user = getCurrentFirebaseUser()) {
  if (!user) return { authenticated: false };
  return { authenticated: true, email: user.email, userId: user.uid, loginAt: Date.now() };
}

/**
 * Actualiza la sesión activa en memoria.
 * @param {{authenticated: boolean, email?: string, userId?: string, loginAt?: number}} session
 */
export function saveSession(session) {
  state.session = session;
}

/**
 * Mantiene compatibilidad entre datos guardados y la estructura actual.
 * @param {object} savedDb
 * @returns {object}
 */
export function normalizeDatabase(savedDb) {
  const db = structuredClone(defaultDatabase);
  const incoming = savedDb && typeof savedDb === "object" ? savedDb : {};

  db.user = { ...db.user, ...(incoming.user || {}) };

  if (Array.isArray(incoming.courses)) {
    db.courses = db.courses.map((course) => {
      const savedCourse = incoming.courses.find((item) => item.id === course.id);
      if (!savedCourse) return course;
      const merged = { ...course, ...savedCourse };
      if (Array.isArray(savedCourse.activities) && savedCourse.activities.length > 0) {
        merged.activities = savedCourse.activities;
      }
      return merged;
    });
  }

  if (Array.isArray(incoming.assistantTasks)) {
    db.assistantTasks = db.assistantTasks.map((task) => {
      const savedTask = incoming.assistantTasks.find((item) => item.id === task.id);
      return savedTask ? { ...task, ...savedTask } : task;
    });
  }

  return db;
}

/**
 * Reinicia la sesión solo si no hay una sesión autenticada activa.
 * Preserva la sesión de Firebase para usuarios ya autenticados.
 */
export async function resetStartupSession() {
  if (state.session?.authenticated) {
    return;
  }
  state.session = { authenticated: false };
  await logoutFirebaseUser();

  if (window.location.hash !== "#recuperar") {
    window.location.hash = "login";
  }
}

/**
 * Habilita cupos demo para evitar estados bloqueados entre recargas.
 */
export async function enableAllCourses() {
  state.db.courses = state.db.courses.map((course) => ({
    ...course,
    seats: Math.max(Number(course.seats) || 0, 5),
    registered: false
  }));
  await saveDatabase();
}

/**
 * Reinicia por completo la información del usuario autenticado.
 */
/**
 * Compatibilidad con versiones anteriores de app.js que iniciaban una
 * sincronizacion en tiempo real desde data.js.
 * La sincronizacion actual se maneja desde firebase-service.js por curso.
 * @returns {() => void} Funcion para cancelar la suscripcion.
 */
export function startRealtimeSync() {
  return () => {};
}

export async function resetSarcDemo() {
  const user = getCurrentFirebaseUser();
  if (!isAuthorizedDemoEmail(user?.email)) return;

  if (user) {
    await resetUserData(user, defaultDatabase);
    await logoutFirebaseUser();
  }

  state.db = structuredClone(defaultDatabase);
  state.session = { authenticated: false };
  window.location.hash = "login";
  window.location.reload();
}
