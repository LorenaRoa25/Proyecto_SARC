const fs = require("fs/promises");
const http = require("http");
const { spawn } = require("child_process");
const path = require("path");

const chromePath = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const projectDir = path.resolve(__dirname, "..");
const outDir = path.join(projectDir, "Documentos", "manual_usuario_sarc_capturas");
const userDataDir = path.join(projectDir, "tools", ".chrome-sarc-profile");
const email = "lorena.roa.196@unisabaneta.edu.co";
const password = process.env.SARC_DEMO_PASSWORD || process.argv[2] || "";
const port = 9224;

if (!password) {
  console.error("Falta SARC_DEMO_PASSWORD o argumento de contrasena.");
  process.exit(1);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch (error) {
          reject(error);
        }
      });
    }).on("error", reject);
  });
}

async function waitForEndpoint(url, retries = 40) {
  for (let i = 0; i < retries; i += 1) {
    try {
      return await getJson(url);
    } catch {
      await sleep(250);
    }
  }
  throw new Error(`No fue posible conectar con Chrome: ${url}`);
}

async function cdpClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });

  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    if (data.id && pending.has(data.id)) {
      const { resolve, reject } = pending.get(data.id);
      pending.delete(data.id);
      if (data.error) reject(new Error(data.error.message));
      else resolve(data.result || {});
    }
  });

  return {
    send(method, params = {}) {
      id += 1;
      ws.send(JSON.stringify({ id, method, params }));
      return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
    },
    close() {
      ws.close();
    },
  };
}

async function waitForExpression(client, expression, timeout = 20000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const result = await client.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.result?.value) return true;
    await sleep(300);
  }
  throw new Error(`Timeout esperando: ${expression}`);
}

async function evaluate(client, expression) {
  return client.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
}

async function screenshot(client, fileName) {
  const shot = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  await fs.writeFile(path.join(outDir, fileName), Buffer.from(shot.data, "base64"));
}

async function main() {
  await fs.mkdir(outDir, { recursive: true });
  await fs.rm(userDataDir, { recursive: true, force: true });
  await fs.mkdir(userDataDir, { recursive: true });

  const chrome = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${port}`,
    "--window-size=1280,720",
    `--user-data-dir=${userDataDir}`,
    "http://127.0.0.1:8000/index.html#login",
  ], { stdio: "ignore" });

  try {
    const version = await waitForEndpoint(`http://127.0.0.1:${port}/json/version`);
    const pages = await waitForEndpoint(`http://127.0.0.1:${port}/json`);
    const page = pages.find((item) => item.type === "page") || pages[0];
    const client = await cdpClient(page.webSocketDebuggerUrl || version.webSocketDebuggerUrl);

    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await waitForExpression(client, "location.hash === '#login' && document.querySelector('#loginForm') && document.querySelector('#loader')?.classList.contains('is-hidden') === true");
    await sleep(1000);
    await evaluate(client, "document.querySelector('#loader') && (document.querySelector('#loader').style.display = 'none'); window.scrollTo(0, 0)");
    await screenshot(client, "01_login_raw.png");

    await evaluate(client, `
      (async () => {
        const email = document.querySelector('#loginEmail');
        const password = document.querySelector('#loginPassword');
        const habeas = document.querySelector('#habeasDataCheck');
        email.value = ${JSON.stringify(email)};
        password.value = ${JSON.stringify(password)};
        habeas.checked = true;
        for (const el of [email, password, habeas]) {
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        document.querySelector('form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        document.querySelector('form button[type="submit"]').click();
      })();
    `);
    await waitForExpression(client, "location.hash === '#inicio'", 30000);
    await sleep(1200);
    await evaluate(client, "document.querySelector('#toastContainer') && (document.querySelector('#toastContainer').innerHTML = '')");
    await screenshot(client, "02_inicio_raw.png");

    await evaluate(client, "location.hash = '#recomendaciones'");
    await waitForExpression(client, "document.querySelector('.catalog-layout') && location.hash === '#recomendaciones'");
    await sleep(1200);
    await evaluate(client, "window.scrollTo(0, 0); document.querySelector('#toastContainer') && (document.querySelector('#toastContainer').innerHTML = '')");
    await screenshot(client, "03_recomendaciones_raw.png");

    await evaluate(client, "location.hash = '#progreso'");
    await waitForExpression(client, "document.querySelector('.progress-layout') && location.hash === '#progreso'");
    await sleep(1200);
    await evaluate(client, "window.scrollTo(0, 0); document.querySelector('#toastContainer') && (document.querySelector('#toastContainer').innerHTML = '')");
    await screenshot(client, "04_progreso_raw.png");

    await evaluate(client, "location.hash = '#perfil'");
    await waitForExpression(client, "document.querySelector('.profile-layout') && location.hash === '#perfil'");
    await sleep(1200);
    await evaluate(client, "window.scrollTo(0, 0); document.querySelector('#toastContainer') && (document.querySelector('#toastContainer').innerHTML = '')");
    await screenshot(client, "05_perfil_raw.png");

    client.close();
  } finally {
    chrome.kill();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
