/**
 * Punto de entrada de SARC: inicializa estado, rutas y renderizado de vistas.
 */

import { enableAllCourses, initializeState, resetStartupSession, state } from "./data.js";
import { navigate } from "./navigation.js";
import { bindStaticLinks } from "../components/feedback.js";
import { setDashboardRefresh } from "./courses.js";
import { renderLogin } from "../../pages/login/login.js";
import { renderRecovery } from "../../pages/recuperar/recuperar.js";
import { renderHome } from "../../pages/inicio/inicio.js";
import { renderRecommendations } from "../../pages/recomendaciones/recomendaciones.js";
import { renderDetail } from "../../pages/detalle/detalle.js";
import { renderProgress } from "../../pages/progreso/progreso.js";
import { renderProfile } from "../../pages/perfil/perfil.js";

const authView = document.getElementById("authView");
const dashboardView = document.getElementById("dashboardView");
const viewContainer = document.getElementById("viewContainer");
const loader = document.getElementById("loader");

/**
 * Inicializa la app y registra eventos globales.
 */
async function init() {
  try {
    await initializeState();
    await resetStartupSession();
    await enableAllCourses();
    bindGlobalEvents();
    setDashboardRefresh(renderDashboard);
    await renderApp();
  } catch (error) {
    console.error("Error al inicializar SARC:", error);
    document.getElementById("viewContainer").innerHTML = `
      <div style="padding:40px;text-align:center;color:#cf2a27;font-size:1.3rem;">
        <strong>Error al cargar el sistema</strong><br>
        <span style="font-size:1rem;color:#1f2937;">${error.message || "Revisa la consola del navegador para más detalles."}</span>
      </div>`;
  }
  loader.classList.add("is-hidden");
  window.addEventListener("hashchange", renderApp);
}

/**
 * Registra navegación y enlaces estáticos del shell.
 */
function bindGlobalEvents() {
  document.querySelectorAll(".top-nav-link[data-route]").forEach((button) => {
    button.addEventListener("click", () => navigate(button.dataset.route));
  });

  bindStaticLinks(document);
}

/**
 * Decide qué contenedor mostrar según ruta y autenticación.
 */
async function renderApp() {
  const hash = window.location.hash.replace("#", "");

  if (!hash) {
    window.location.hash = state.session.authenticated ? "inicio" : "login";
    return;
  }

  if (!state.session.authenticated && !["login", "recuperar"].includes(hash)) {
    window.location.hash = "login";
    return;
  }

  if (state.session.authenticated && ["login", "recuperar"].includes(hash)) {
    window.location.hash = "inicio";
    return;
  }

  if (hash.startsWith("detalle/")) {
    state.route = "detalle";
    state.currentDetailId = hash.split("/")[1];
  } else {
    state.route = hash;
  }

  const isAuth = ["login", "recuperar"].includes(state.route);
  authView.classList.toggle("hidden", !isAuth);
  dashboardView.classList.toggle("hidden", isAuth);

  if (isAuth) {
    await renderAuth();
    return;
  }

  await renderDashboard();
}

/**
 * Renderiza vistas públicas de autenticación.
 */
async function renderAuth() {
  if (state.route === "login") {
    await renderLogin(authView);
    return;
  }

  await renderRecovery(authView);
}

/**
 * Renderiza vistas privadas del dashboard y marca navegación activa.
 */
async function renderDashboard() {
  document.querySelectorAll(".top-nav-link[data-route]").forEach((button) => {
    const isActive =
      button.dataset.route === state.route ||
      (state.route === "detalle" && button.dataset.route === "recomendaciones");
    button.classList.toggle("active", isActive);
  });

  const pageRenderers = {
    inicio: renderHome,
    recomendaciones: renderRecommendations,
    detalle: renderDetail,
    progreso: renderProgress,
    perfil: renderProfile
  };

  const renderer = pageRenderers[state.route] || renderHome;
  await renderer(viewContainer);
  bindStaticLinks(dashboardView);
}

init();
