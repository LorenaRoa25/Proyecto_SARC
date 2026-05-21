"""Servidor local portable para ejecutar SARC en Windows.

SARC no tiene backend de negocio. Este archivo solo sirve los archivos
estaticos del frontend para que ES Modules, fetch y Firebase funcionen
correctamente desde localhost.
"""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import mimetypes
import os
import sys
import threading
import webbrowser


HOST = "localhost"
PORT = 8000
PROJECT_DIR = Path(__file__).resolve().parent
BASE_URL = f"http://{HOST}:{PORT}/"

# MIME types necesarios para ES Modules y recursos estaticos.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/html", ".html")


class SarcHandler(SimpleHTTPRequestHandler):
    """Sirve archivos estaticos del proyecto SARC con MIME types correctos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def end_headers(self):
        """Agrega headers CORS y evita cache de modulos durante desarrollo."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        """Evita fallos al ejecutarse con pythonw.exe sin consola visible."""
        return


def open_browser():
    """Abre el navegador en la pagina principal del sistema."""
    webbrowser.open(BASE_URL)


def validate_project_files():
    """Verifica que el servidor se ejecute desde la raiz portable de SARC."""
    required_files = [
        "index.html",
        "shared/js/app.js",
        "shared/js/firebase-config.js",
        "pages/login/login.html",
    ]
    missing = [item for item in required_files if not (PROJECT_DIR / item).exists()]
    if missing:
        print("ERROR: La carpeta del proyecto SARC esta incompleta.")
        print("Archivos faltantes:")
        for item in missing:
            print(f" - {item}")
        return False
    return True


def main():
    """Inicia el servidor HTTP local."""
    if not validate_project_files():
        sys.exit(1)

    os.chdir(PROJECT_DIR)

    try:
        server = ThreadingHTTPServer((HOST, PORT), SarcHandler)
    except OSError as error:
        print("ERROR: No fue posible iniciar SARC en el puerto 8000.")
        print("Causa probable: ya existe otro servidor usando http://localhost:8000/")
        print("Solucion: cierre la otra ventana de SARC o detenga el proceso anterior.")
        print(f"Detalle tecnico: {error}")
        open_browser()
        sys.exit(1)

    server.timeout = 0.5
    print(f"SARC ejecutandose en {BASE_URL}")
    print("Firebase se conecta desde el navegador mediante shared/js/firebase-config.js")
    print("Presiona Ctrl+C para detener el servidor.")

    timer = threading.Timer(0.8, open_browser)
    timer.daemon = True
    timer.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
