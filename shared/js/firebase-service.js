/**
 * Servicio unico para Firebase Authentication y Firestore.
 * Usa importacion dinamica para que la app funcione incluso sin conexion a Firebase CDN.
 * La UI conserva su estructura; este archivo reemplaza la persistencia local.
 */

import { firebaseConfig } from "./firebase-config.js";
import { isAuthorizedDemoEmail } from "./user-profiles.js";

let app = null;
let auth = null;
let db = null;
let firebaseModules = null;

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

  try {
    const [{ initializeApp }, { browserSessionPersistence, EmailAuthProvider, getAuth, onAuthStateChanged, reauthenticateWithCredential, sendPasswordResetEmail, setPersistence, signInWithEmailAndPassword, signOut, updatePassword }, { collection, deleteDoc, doc, getDoc, getDocs, getFirestore, onSnapshot, query, setDoc, where, writeBatch }] = await Promise.all([
      import("https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"),
      import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js"),
      import("https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js")
    ]);

    firebaseModules = { initializeApp, browserSessionPersistence, EmailAuthProvider, getAuth, onAuthStateChanged, reauthenticateWithCredential, sendPasswordResetEmail, setPersistence, signInWithEmailAndPassword, signOut, updatePassword, collection, deleteDoc, doc, getDoc, getDocs, getFirestore, onSnapshot, query, setDoc, where, writeBatch };

    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    await setPersistence(auth, browserSessionPersistence);
    return true;
  } catch (error) {
    console.warn("Firebase CDN no disponible, usando datos demo locales:", error.message);
    return false;
  }
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

    const unsubscribe = firebaseModules.onAuthStateChanged(auth, (user) => {
      unsubscribe();
      resolve(user);
    });
  });
}

export async function loginWithEmail(email, password) {
  if (!auth || !firebaseModules) {
    throw { code: "auth/firebase-not-available", message: "Firebase no está disponible en este momento." };
  }
  const credential = await firebaseModules.signInWithEmailAndPassword(auth, email, password);
  return credential.user;
}

export async function saveHabeasDataAcceptance(userId, email) {
  if (!userId || !email || !db) return;
  const habeasRef = firebaseModules.doc(db, "habeasData", userId);
  await firebaseModules.setDoc(habeasRef, {
    userId,
    email: email.toLowerCase(),
    acceptedAt: new Date().toISOString(),
    userAgent: navigator.userAgent || ""
  }, { merge: true });
}

export async function checkHabeasDataAcceptance(userId) {
  if (!userId || !db) return false;
  const habeasRef = firebaseModules.doc(db, "habeasData", userId);
  const snap = await firebaseModules.getDoc(habeasRef);
  return snap.exists();
}

export function subscribeToCourseActivities(userId, courseId, callback) {
  if (!db || !firebaseModules) return () => {};
  const ref = firebaseModules.doc(db, "cursos", `${userId}_${courseId}`);
  return firebaseModules.onSnapshot(ref, (snap) => {
    if (snap.exists()) {
      const data = snap.data();
      callback(data.activities || []);
    }
  }, () => {});
}

export async function logoutFirebaseUser() {
  if (auth && firebaseModules) await firebaseModules.signOut(auth);
}

export async function sendPasswordRecovery(email) {
  if (!auth || !firebaseModules) throw new Error("Firebase no disponible.");
  await firebaseModules.sendPasswordResetEmail(auth, email);
}

export async function updateCurrentUserPassword(currentPassword, newPassword) {
  if (!auth || !firebaseModules) throw new Error("Firebase no disponible.");
  const user = getCurrentFirebaseUser();
  if (!user?.email) throw new Error("No hay usuario autenticado.");

  const credential = firebaseModules.EmailAuthProvider.credential(user.email, currentPassword);
  await firebaseModules.reauthenticateWithCredential(user, credential);
  await firebaseModules.updatePassword(user, newPassword);
}

export async function loadUserData(user, defaultDatabase, normalizeDatabase) {
  if (!user || !db || !firebaseModules) return normalizeDatabase(defaultDatabase);

  const userRef = firebaseModules.doc(db, "usuarios", user.uid);
  const userSnap = await firebaseModules.getDoc(userRef);
  if (!userSnap.exists()) {
    await seedUserData(user, defaultDatabase);
  } else if (shouldReplaceCopiedDemo(user, userSnap.data(), defaultDatabase)) {
    await deleteUserCollections(user.uid);
    await seedUserData(user, defaultDatabase);
  }

  const [profileSnap, courseSnap, taskSnap] = await Promise.all([
    firebaseModules.getDoc(userRef),
    firebaseModules.getDocs(firebaseModules.query(firebaseModules.collection(db, "cursos"), firebaseModules.where("userId", "==", user.uid))),
    firebaseModules.getDocs(firebaseModules.query(firebaseModules.collection(db, "tareasAsistente"), firebaseModules.where("userId", "==", user.uid)))
  ]);

  return normalizeDatabase({
    user: profileSnap.exists() ? profileSnap.data() : {},
    courses: courseSnap.docs.map((item) => item.data()).sort(byOrder),
    assistantTasks: taskSnap.docs.map((item) => item.data()).sort(byOrder)
  });
}

export async function saveUserData(userId, database) {
  if (!userId || !database || !db || !firebaseModules) return;

  const batch = firebaseModules.writeBatch(db);
  const userData = cleanForFirestore({
    ...database.user,
    userId,
    email: database.user.email?.toLowerCase()
  });
  delete userData.password;

  batch.set(firebaseModules.doc(db, "usuarios", userId), userData, { merge: true });

  database.courses.forEach((course, index) => {
    const courseDoc = cleanForFirestore({ ...course, userId, courseId: course.id, order: index });
    batch.set(firebaseModules.doc(db, "cursos", `${userId}_${course.id}`), courseDoc, { merge: true });

    const recommendationDoc = cleanForFirestore({
      userId,
      courseId: course.id,
      courseName: course.name,
      recommendation: course.recommendation || "",
      alternatives: course.alternatives || [],
      order: index
    });
    batch.set(firebaseModules.doc(db, "recomendaciones", `${userId}_${course.id}`), recommendationDoc, { merge: true });
  });

  database.assistantTasks.forEach((task, index) => {
    batch.set(
      firebaseModules.doc(db, "tareasAsistente", `${userId}_${task.id}`),
      cleanForFirestore({ ...task, userId, taskId: task.id, order: index }),
      { merge: true }
    );
  });

  await batch.commit();
}

export async function resetUserData(user, defaultDatabase) {
  if (!user?.uid || !db || !firebaseModules) return;
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
  if (isAuthorizedDemoEmail(email)) {
    return buildLorenaDemoProfile();
  }

  const knownProfiles = {
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

function buildLorenaDemoProfile() {
  return {
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
  };
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
    career: "Programa académico",
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
    { id: "a1", label: `Completar diagnóstico académico de ${name}`, done: false },
    { id: "a2", label: "Revisar cursos recomendados", done: false },
    { id: "a3", label: "Actualizar modalidad preferida", done: false }
  ];
}

function shouldReplaceCopiedDemo(user, profile, defaultDatabase) {
  const authEmail = user.email?.toLowerCase();
  const defaultEmail = defaultDatabase.user.email.toLowerCase();
  return (
    authEmail &&
    (
      (authEmail !== defaultEmail && profile?.name === defaultDatabase.user.name) ||
      shouldReplaceGenericDemoAlias(authEmail, profile)
    )
  );
}

function shouldReplaceGenericDemoAlias(authEmail, profile) {
  return (
    isAuthorizedDemoEmail(authEmail) &&
    (
      profile?.name === "Lorena Roa 196" ||
      profile?.faculty === "Facultad por definir" ||
      profile?.career === "Programa acadÃ©mico"
    )
  );
}

async function deleteUserCollections(userId) {
  if (!db || !firebaseModules) return;
  await Promise.all(
    ["cursos", "recomendaciones", "tareasAsistente"].map(async (name) => {
      const snapshot = await firebaseModules.getDocs(firebaseModules.query(firebaseModules.collection(db, name), firebaseModules.where("userId", "==", userId)));
      await Promise.all(snapshot.docs.map((item) => firebaseModules.deleteDoc(item.ref)));
    })
  );
}

function cleanForFirestore(value) {
  return JSON.parse(JSON.stringify(value));
}

function byOrder(a, b) {
  return (Number(a.order) || 0) - (Number(b.order) || 0);
}
