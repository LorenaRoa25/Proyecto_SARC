/**
 * Servicio unico para Firebase Authentication y Firestore.
 * La UI conserva su estructura; este archivo reemplaza la persistencia local.
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
import {
  browserSessionPersistence,
  createUserWithEmailAndPassword,
  EmailAuthProvider,
  getAuth,
  onAuthStateChanged,
  reauthenticateWithCredential,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signOut,
  updatePassword
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";
import {
  collection,
  deleteDoc,
  doc,
  getDoc,
  getDocs,
  getFirestore,
  query,
  where,
  writeBatch
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

let app = null;
let auth = null;
let db = null;

export function isFirebaseConfigured() {
  return Boolean(
    firebaseConfig.apiKey &&
      firebaseConfig.projectId &&
      !firebaseConfig.apiKey.startsWith("TU_") &&
      !firebaseConfig.projectId.startsWith("TU_")
  );
}

export async function initializeFirebase() {
  if (!isFirebaseConfigured()) return false;
  if (app) return true;

  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  db = getFirestore(app);
  await setPersistence(auth, browserSessionPersistence);
  return true;
}

export function getCurrentFirebaseUser() {
  return auth?.currentUser || null;
}

export function waitForAuthUser() {
  return new Promise((resolve) => {
    if (!auth) {
      resolve(null);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      unsubscribe();
      resolve(user);
    });
  });
}

export async function loginWithEmail(email, password) {
  try {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    return credential.user;
  } catch (error) {
    if (error.code !== "auth/user-not-found") throw error;

    const credential = await createUserWithEmailAndPassword(auth, email, password);
    return credential.user;
  }
}

export async function logoutFirebaseUser() {
  if (auth) await signOut(auth);
}

export async function sendPasswordRecovery(email) {
  await sendPasswordResetEmail(auth, email);
}

export async function updateCurrentUserPassword(currentPassword, newPassword) {
  const user = getCurrentFirebaseUser();
  if (!user?.email) throw new Error("No hay usuario autenticado.");

  const credential = EmailAuthProvider.credential(user.email, currentPassword);
  await reauthenticateWithCredential(user, credential);
  await updatePassword(user, newPassword);
}

export async function loadUserData(user, defaultDatabase, normalizeDatabase) {
  if (!user) return normalizeDatabase(defaultDatabase);

  const userRef = doc(db, "usuarios", user.uid);
  const userSnap = await getDoc(userRef);
  if (!userSnap.exists()) {
    await seedUserData(user, defaultDatabase);
  } else if (shouldReplaceCopiedDemo(user, userSnap.data(), defaultDatabase)) {
    await deleteUserCollections(user.uid);
    await seedUserData(user, defaultDatabase);
  }

  const [profileSnap, courseSnap, taskSnap] = await Promise.all([
    getDoc(userRef),
    getDocs(query(collection(db, "cursos"), where("userId", "==", user.uid))),
    getDocs(query(collection(db, "tareasAsistente"), where("userId", "==", user.uid)))
  ]);

  return normalizeDatabase({
    user: profileSnap.exists() ? profileSnap.data() : {},
    courses: courseSnap.docs.map((item) => item.data()).sort(byOrder),
    assistantTasks: taskSnap.docs.map((item) => item.data()).sort(byOrder)
  });
}

export async function saveUserData(userId, database) {
  if (!userId || !database) return;

  const batch = writeBatch(db);
  const userData = cleanForFirestore({
    ...database.user,
    userId,
    email: database.user.email?.toLowerCase()
  });
  delete userData.password;

  batch.set(doc(db, "usuarios", userId), userData, { merge: true });

  database.courses.forEach((course, index) => {
    const courseDoc = cleanForFirestore({ ...course, userId, courseId: course.id, order: index });
    batch.set(doc(db, "cursos", `${userId}_${course.id}`), courseDoc, { merge: true });

    const recommendationDoc = cleanForFirestore({
      userId,
      courseId: course.id,
      courseName: course.name,
      recommendation: course.recommendation || "",
      alternatives: course.alternatives || [],
      order: index
    });
    batch.set(doc(db, "recomendaciones", `${userId}_${course.id}`), recommendationDoc, { merge: true });
  });

  database.assistantTasks.forEach((task, index) => {
    batch.set(
      doc(db, "tareasAsistente", `${userId}_${task.id}`),
      cleanForFirestore({ ...task, userId, taskId: task.id, order: index }),
      { merge: true }
    );
  });

  await batch.commit();
}

export async function resetUserData(user, defaultDatabase) {
  if (!user?.uid) return;
  await deleteUserCollections(user.uid);
  await seedUserData(user, defaultDatabase);
}

async function seedUserData(user, defaultDatabase) {
  const seeded = buildInitialDatabaseForUser(user, defaultDatabase);
  await saveUserData(user.uid, seeded);
}

function buildInitialDatabaseForUser(user, defaultDatabase) {
  const seeded = structuredClone(defaultDatabase);
  const email = (user.email || seeded.user.email).toLowerCase();
  const profile = getProfileSeed(email);

  seeded.user = {
    ...seeded.user,
    ...profile,
    email
  };

  seeded.courses = seeded.courses.map((course) => {
    const customCourse = profile.courses?.[course.id] || {};
    return { ...course, ...customCourse };
  });

  seeded.assistantTasks = profile.assistantTasks || buildGenericTasks(profile.name);
  return seeded;
}

function getProfileSeed(email) {
  const knownProfiles = {
    "lorena.roa.196@unisabaneta.edu.co": {
      name: "Lorena Roa Rivera",
      faculty: "Ingenieria Informatica",
      career: "Ingenieria Informatica",
      semester: "8",
      modality: "Virtual",
      courses: {
        matematicas: { enrolled: true, progress: 70, status: "En progreso", lessons: "7/10", average: "85%" },
        programacion: { enrolled: true, progress: 40, status: "En progreso", lessons: "4/10", average: "35%" },
        ingles: { enrolled: true, progress: 95, status: "En progreso", lessons: "9/10", average: "80%" }
      },
      assistantTasks: [
        { id: "a1", label: "Refuerza Matematicas", done: true },
        { id: "a2", label: "Tomar curso Python", done: true },
        { id: "a3", label: "Completa el curso de Ingles A2", done: true }
      ]
    },
    "juan@unisabaneta.edu.co": {
      name: "Juan Esteban Martinez",
      faculty: "Derecho",
      career: "Derecho",
      semester: "5",
      modality: "Presencial",
      courses: {
        matematicas: { enrolled: false, progress: 0, status: "Disponible", lastAccess: "Sin acceso", lessons: "0/10", average: "0%" },
        programacion: { enrolled: false, progress: 0, status: "Disponible", lastAccess: "Sin acceso", lessons: "0/10", average: "0%" },
        ingles: { enrolled: true, progress: 25, status: "En progreso", lastAccess: "Hace 3 dias", lessons: "2/10", average: "62%" },
        "derecho-constitucional": {
          enrolled: true,
          registered: true,
          progress: 55,
          status: "En progreso",
          lastAccess: "Hoy",
          lessons: "5/8",
          average: "78%"
        }
      },
      assistantTasks: [
        { id: "a1", label: "Revisar lectura constitucional", done: false },
        { id: "a2", label: "Completar practica de Ingles", done: true },
        { id: "a3", label: "Inscribirse a Comunicacion Efectiva", done: false }
      ]
    }
  };

  return knownProfiles[email] || buildGenericProfile(email);
}

function buildGenericProfile(email) {
  const name = email
    .split("@")[0]
    .split(/[._-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return {
    name: name || "Estudiante SARC",
    faculty: "Facultad por definir",
    career: "Programa academico",
    semester: "1",
    modality: "Virtual",
    courses: {
      matematicas: { enrolled: true, progress: 15, status: "En progreso", lastAccess: "Hoy", lessons: "1/10", average: "70%" },
      programacion: { enrolled: false, progress: 0, status: "Disponible", lastAccess: "Sin acceso", lessons: "0/10", average: "0%" },
      ingles: { enrolled: false, progress: 0, status: "Disponible", lastAccess: "Sin acceso", lessons: "0/10", average: "0%" }
    }
  };
}

function buildGenericTasks(name) {
  return [
    { id: "a1", label: `Completar diagnostico academico de ${name}`, done: false },
    { id: "a2", label: "Revisar cursos recomendados", done: false },
    { id: "a3", label: "Actualizar modalidad preferida", done: false }
  ];
}

function shouldReplaceCopiedDemo(user, profile, defaultDatabase) {
  const authEmail = user.email?.toLowerCase();
  const defaultEmail = defaultDatabase.user.email.toLowerCase();
  return (
    authEmail &&
    authEmail !== defaultEmail &&
    profile?.name === defaultDatabase.user.name
  );
}

async function deleteUserCollections(userId) {
  await Promise.all(
    ["cursos", "recomendaciones", "tareasAsistente"].map(async (name) => {
      const snapshot = await getDocs(query(collection(db, name), where("userId", "==", userId)));
      await Promise.all(snapshot.docs.map((item) => deleteDoc(item.ref)));
    })
  );
}

function cleanForFirestore(value) {
  return JSON.parse(JSON.stringify(value));
}

function byOrder(a, b) {
  return (Number(a.order) || 0) - (Number(b.order) || 0);
}
