"""Servidor local para ejecutar SARC desde Visual Studio Code."""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import threading
import webbrowser


HOST = "localhost"
PORT = 8000
PROJECT_DIR = Path(__file__).resolve().parent


class SarcHandler(SimpleHTTPRequestHandler):
    """Sirve archivos estáticos del proyecto SARC."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)


def open_browser():
    """Abre el navegador en la página principal del sistema."""
    webbrowser.open(f"http://{HOST}:{PORT}/index.html")


def main():
    """Inicia el servidor HTTP local."""
    os.chdir(PROJECT_DIR)
    server = ThreadingHTTPServer((HOST, PORT), SarcHandler)
    print(f"SARC ejecutándose en http://{HOST}:{PORT}/index.html")
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
