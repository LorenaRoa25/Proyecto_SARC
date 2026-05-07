/**
 * Centraliza datos demo, estado global y persistencia Firebase de SARC.
 */

import {
  getCurrentFirebaseUser,
  initializeFirebase,
  loadUserData,
  logoutFirebaseUser,
  resetUserData,
  saveUserData,
  waitForAuthUser
} from "./firebase-service.js";

export const CORE_COURSE_IDS = ["matematicas", "programacion", "ingles"];

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

export const defaultDatabase = {
  user: {
    email: "lorena.roa.196@unisabaneta.edu.co",
    name: "Lorena Roa Rivera",
    faculty: "Ingeniería Informática",
    career: "Ingeniería Informática",
    semester: "8",
    modality: "Virtual",
    avatar: AVATAR_PLACEHOLDER
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
      registered: false
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
      registered: false
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
      registered: false
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
      registered: false
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
      registered: false
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
      registered: false
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
      registered: false
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
      return savedCourse ? { ...course, ...savedCourse } : course;
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
 * Reinicia la sesión al cargar la demo, conservando el comportamiento original.
 */
export async function resetStartupSession() {
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
export async function resetSarcDemo() {
  const user = getCurrentFirebaseUser();
  if (user) {
    await resetUserData(user, defaultDatabase);
    await logoutFirebaseUser();
  }

  state.db = structuredClone(defaultDatabase);
  state.session = { authenticated: false };
  window.location.hash = "login";
  window.location.reload();
}
