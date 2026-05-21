"""Alinea documentos SARC con el estado actual del proyecto.

El script conserva estilos base de Word: reemplaza texto en parrafos/celdas
sin tocar imagenes, margenes, tablas ni estetica general.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from docx import Document


PROJECT_DIR = Path(__file__).resolve().parents[1]
DESKTOP = PROJECT_DIR.parent
BACKUP_DIR = PROJECT_DIR / "backups_documentos"

DOC_CODE = PROJECT_DIR / "DOCUMENTACION_CODIGO_SARC.docx"
DOC_PROJECT = DESKTOP / "Documento proyecto SARC - Lorena Roa Rivera.docx"
DOC_REPORT = DESKTOP / "Informe_evaluacion_SARC.docx"
DOC_LICENSE = DESKTOP / "Minuta Licenciamiento-Lorena Roa.docx"
DOC_SUMMARY = DESKTOP / "Resumen_Ejecutivo_SARC.docx"


def replace_text_in_paragraph(paragraph, new_text: str) -> None:
    """Reemplaza texto conservando el estilo del primer run."""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(new_text)


def replace_paragraph_contains(doc, needle: str, new_text: str) -> int:
    changed = 0
    for paragraph in doc.paragraphs:
        if needle in paragraph.text:
            replace_text_in_paragraph(paragraph, new_text)
            changed += 1
    return changed


def set_cell_text(cell, new_text: str) -> None:
    if cell.paragraphs:
        replace_text_in_paragraph(cell.paragraphs[0], new_text)
        for paragraph in cell.paragraphs[1:]:
            replace_text_in_paragraph(paragraph, "")
    else:
        cell.text = new_text


def backup(path: Path) -> None:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, BACKUP_DIR / f"{path.stem}_{stamp}{path.suffix}")


def update_project_document() -> None:
    backup(DOC_PROJECT)
    doc = Document(DOC_PROJECT)

    replacements = {
        "Desarrollar un motor de recomendación de cursos basado en el perfil académico del estudiante (carrera, semestre, áreas de interés).":
            "Desarrollar un módulo de recomendación de cursos basado en el perfil académico disponible, los cursos registrados, la modalidad y las tareas sugeridas al estudiante.",
        "Registro e inicio de sesión de estudiantes con correo institucional.":
            "Inicio de sesión de estudiantes mediante Firebase Authentication; para la demo, si el correo no existe se crea el usuario con Email/Password.",
        "La autenticación se realiza exclusivamente con correo del dominio @unisabaneta.edu.co.":
            "La autenticación se realiza con Firebase Authentication usando correo y contraseña; el enfoque institucional se mantiene en la documentación, aunque el código no valida por dominio.",
        "La plataforma depende de un servidor de correo institucional activo para la recuperación de contraseñas.":
            "La recuperación de contraseña depende del servicio de correo de Firebase Authentication y de la configuración del proveedor Email/Password.",
        "Catalog Module: Administra el catálogo de cursos con filtros y paginación.":
            "Catalog Module: Administra el catálogo de cursos con filtros por área y modalidad. La versión actual no implementa paginación.",
        "Progress Module: Registra y calcula el progreso del estudiante por curso.":
            "Progress Module: Muestra el progreso guardado por curso y permite consultar o descargar reportes; no calcula progreso a partir de actividades reales.",
        "El módulo app.js controla la navegación por hash, valida la sesión demo y renderiza la vista correspondiente.":
            "El módulo app.js controla la navegación por hash, valida la sesión en memoria y renderiza la vista correspondiente.",
        "Motor de recomendación de cursos basado en perfil académico.":
            "Módulo de recomendación de cursos basado en el perfil disponible, cursos registrados, filtros y tareas sugeridas.",
        "El sistema guarda la información principal en Firebase, incluyendo datos de usuario, cursos, inscripciones y progreso académico, lo que permite persistencia real entre sesiones.":
            "El sistema guarda la información principal en Firebase, incluyendo datos de usuario, estado de cursos, recomendaciones y tareas del asistente, lo que permite persistencia por userId.",
        "Recibir capacitación básica para administradores del sistema.":
            "Recibir capacitación básica para el uso y configuración del sistema en su alcance actual.",
    }
    for old, new in replacements.items():
        replace_paragraph_contains(doc, old, new)

    # Tabla de usuarios.
    table = doc.tables[1]
    set_cell_text(
        table.rows[2].cells[1],
        "Rol proyectado para versiones futuras. La versión actual no incluye panel administrativo; la gestión se realiza desde la configuración del proyecto y Firebase.",
    )

    # Requerimientos funcionales.
    table = doc.tables[3]
    set_cell_text(
        table.rows[1].cells[2],
        "El sistema permite iniciar sesión con correo y contraseña mediante Firebase. Para facilitar la demo, si el usuario no existe se crea automáticamente con Email/Password.",
    )
    set_cell_text(
        table.rows[2].cells[2],
        "El estudiante ingresa correo y contraseña. Firebase valida las credenciales y, si son correctas, el sistema carga sus datos y redirige al dashboard.",
    )
    set_cell_text(
        table.rows[3].cells[2],
        "El sistema permite solicitar recuperación de contraseña mediante Firebase Authentication. La solicitud envía un correo seguro al usuario configurado.",
    )
    set_cell_text(
        table.rows[12].cells[2],
        "El sistema genera y descarga un archivo PDF simple con el reporte de progreso del curso seleccionado y los datos principales del estudiante.",
    )

    # Requisitos no funcionales.
    table = doc.tables[4]
    set_cell_text(
        table.rows[1].cells[2],
        "Las credenciales se gestionan con Firebase Authentication. La información académica se protege en Firestore mediante reglas por userId.",
    )
    set_cell_text(
        table.rows[5].cells[2],
        "La interfaz debe mantener consistencia visual institucional, claridad de uso y flujos de inscripción de pocos clics.",
    )
    set_cell_text(
        table.rows[8].cells[2],
        "La arquitectura ya integra Firebase Authentication y Cloud Firestore; puede escalar agregando roles, almacenamiento de archivos, panel administrativo y despliegue en hosting estático.",
    )

    # Reglas de negocio.
    table = doc.tables[5]
    set_cell_text(
        table.rows[3].cells[1],
        "Las recomendaciones del asistente virtual se presentan con base en los cursos, el perfil guardado y las tareas configuradas; no hay algoritmo de machine learning en esta versión.",
    )
    set_cell_text(
        table.rows[5].cells[1],
        "El acceso se realiza con correo y contraseña mediante Firebase Authentication. El dominio institucional es una condición esperada del proyecto, pero no se valida explícitamente en el código actual.",
    )

    # Historias de usuario de login/recuperacion.
    table = doc.tables[9]
    set_cell_text(
        table.rows[5].cells[1],
        "1. El sistema recibe correo y contraseña. 2. Con credenciales incorrectas muestra mensaje de error. 3. Con credenciales correctas carga Firestore y redirige al dashboard. 4. El usuario debe existir previamente en Firebase Authentication.",
    )
    table = doc.tables[10]
    set_cell_text(
        table.rows[5].cells[1],
        "1. El botón 'Recuperar contraseña' está visible en login. 2. El formulario solicita correo. 3. Valida los campos ingresados. 4. Firebase envía un enlace seguro de recuperación y el sistema vuelve al login.",
    )

    # Tabla de responsabilidades.
    table = doc.tables[23]
    set_cell_text(
        table.rows[2].cells[1],
        "Proveer la infraestructura de Firebase/hosting requerida, gestionar usuarios autorizados, garantizar el uso ético del sistema y notificar fallas en tiempo razonable.",
    )

    # Ficha tecnica.
    table = doc.tables[19]
    set_cell_text(
        table.rows[4].cells[1],
        "Arquitectura frontend modular por vistas y módulos compartidos, con Firebase Authentication y Cloud Firestore como servicios externos de autenticación y persistencia.",
    )
    set_cell_text(
        table.rows[6].cells[1],
        "No aplica servidor de backend propio. La app usa Firebase como servicio externo de autenticación y datos, y app.py solo sirve archivos estáticos en desarrollo.",
    )
    set_cell_text(
        table.rows[8].cells[1],
        "Firebase Authentication y Cloud Firestore implementados para autenticación, carga, guardado y separación de datos por userId.",
    )
    set_cell_text(
        table.rows[9].cells[1],
        "Cloud Firestore como base de datos principal, con documentos asociados a userId en las colecciones usuarios, cursos, recomendaciones y tareasAsistente.",
    )
    set_cell_text(
        table.rows[10].cells[1],
        "Firebase Authentication con correo y contraseña para credenciales, recuperación y sesión autenticada.",
    )

    # Capas.
    table = doc.tables[24]
    set_cell_text(
        table.rows[2].cells[1],
        "Lógica de aplicación implementada en JavaScript puro en el navegador. Incluye navegación, validación de sesión en memoria, filtros, inscripción, progreso, reportes PDF, edición de perfil y conexión con Firebase.",
    )
    set_cell_text(
        table.rows[3].cells[1],
        "Persistencia en Cloud Firestore mediante las colecciones usuarios, cursos, recomendaciones y tareasAsistente. Cada documento de datos se asocia a userId para separar usuarios.",
    )

    # Modelo de datos real de Firestore.
    table = doc.tables[25]
    set_cell_text(table.rows[1].cells[0], "usuarios")
    set_cell_text(
        table.rows[1].cells[1],
        "Documento por usuario autenticado. El id es el uid de Firebase. Campos principales: userId, email, name, faculty, career, semester, modality y avatar.",
    )
    set_cell_text(table.rows[2].cells[0], "cursos")
    set_cell_text(
        table.rows[2].cells[1],
        "Documentos por usuario y curso con id {uid}_{courseId}. Guardan id, courseId, userId, name, area, modality, seats, enrolled, registered, progress, status, lessons, timeSpent, average, recommendation, alternatives y order.",
    )
    set_cell_text(table.rows[3].cells[0], "recomendaciones")
    set_cell_text(
        table.rows[3].cells[1],
        "Documentos por usuario y curso con id {uid}_{courseId}. Guardan userId, courseId, courseName, recommendation, alternatives y order.",
    )
    set_cell_text(table.rows[4].cells[0], "tareasAsistente")
    set_cell_text(
        table.rows[4].cells[1],
        "Documentos por usuario y tarea con id {uid}_{taskId}. Guardan taskId, userId, label, done y order.",
    )
    set_cell_text(table.rows[5].cells[0], "Nota")
    set_cell_text(
        table.rows[5].cells[1],
        "La versión actual no usa colecciones separadas de Inscripcion ni Progreso; esos datos viven dentro de cada documento de curso del usuario.",
    )
    set_cell_text(table.rows[6].cells[0], "Nota")
    set_cell_text(
        table.rows[6].cells[1],
        "Los cursos alternativos se guardan como arreglo alternatives dentro del curso y en la recomendación, no como colección independiente.",
    )

    # Relaciones.
    table = doc.tables[26]
    set_cell_text(table.rows[1].cells[0], "Usuario - cursos")
    set_cell_text(table.rows[1].cells[1], "1 a N")
    set_cell_text(table.rows[1].cells[2], "Un usuario autenticado puede tener varios documentos de curso, filtrados por userId.")
    set_cell_text(table.rows[2].cells[0], "Usuario - tareasAsistente")
    set_cell_text(table.rows[2].cells[1], "1 a N")
    set_cell_text(table.rows[2].cells[2], "Un usuario puede tener varias tareas del asistente asociadas por userId.")
    set_cell_text(table.rows[3].cells[0], "Curso - recomendación")
    set_cell_text(table.rows[3].cells[1], "1 a 1 por usuario")
    set_cell_text(table.rows[3].cells[2], "Cada curso del usuario tiene un documento de recomendación asociado con el mismo courseId.")
    set_cell_text(table.rows[4].cells[0], "Curso - alternativas")
    set_cell_text(table.rows[4].cells[1], "1 a N embebida")
    set_cell_text(table.rows[4].cells[2], "Las alternativas se guardan como lista dentro del curso y no como documentos separados.")
    set_cell_text(table.rows[5].cells[0], "Auth - usuarios")
    set_cell_text(table.rows[5].cells[1], "1 a 1")
    set_cell_text(table.rows[5].cells[2], "El uid de Firebase Authentication identifica el documento usuarios/{uid}.")

    # Casos de prueba.
    table = doc.tables[27]
    set_cell_text(table.rows[1].cells[3], "Correo y contraseña registrados o creados en Firebase para la demo")
    set_cell_text(table.rows[2].cells[3], "Correo o contraseña inválidos")
    set_cell_text(table.rows[8].cells[4], "Lista de cursos inscritos con barras de progreso y datos correctos del usuario")
    set_cell_text(table.rows[11].cells[3], "Intento de acceso a ruta privada sin sesión autenticada en memoria")
    set_cell_text(table.rows[11].cells[4], "Redirección al login y rechazo de lecturas/escrituras en Firestore si no existe usuario autenticado")

    # Beneficios.
    table = doc.tables[28]
    set_cell_text(
        table.rows[2].cells[1],
        "El módulo de recomendación orienta al estudiante con sugerencias configuradas a partir del perfil, cursos y tareas; puede evolucionar a un motor más avanzado.",
    )

    doc.save(DOC_PROJECT)


def update_evaluation_report() -> None:
    backup(DOC_REPORT)
    doc = Document(DOC_REPORT)
    replace_paragraph_contains(
        doc,
        "Falta anexar instrucciones de despliegue y capturas.",
        "Ya se cuenta con README y guía de configuración Firebase; como mejora documental, conviene anexar capturas del despliegue o de la ejecución local.",
    )
    replace_paragraph_contains(
        doc,
        "Falta preparar un guion de presentación y una ruta de demostración del sistema.",
        "La guía de sustentación del código complementa este punto; como mejora final, conviene ensayar una ruta de demostración con login, inscripción, progreso, perfil y Firestore.",
    )
    doc.save(DOC_REPORT)


def update_license_document() -> None:
    backup(DOC_LICENSE)
    doc = Document(DOC_LICENSE)
    replacements = {
        "Usuario Autorizado: Toda persona natural (estudiante, administrativo o docente) habilitada por LA INSTITUCIÓN para acceder al SARC con credenciales institucionales.":
            "Usuario Autorizado: Toda persona natural habilitada por LA INSTITUCIÓN para acceder al SARC. En la versión 1.0.0 implementada, el uso funcional corresponde al perfil estudiante; roles administrativos o docentes quedan sujetos a desarrollo futuro.",
        "Autenticación: gestionada mediante Firebase Authentication, con credenciales institucionales (@unisabaneta.edu.co), control de sesiones y protección de rutas privadas.":
            "Autenticación: gestionada mediante Firebase Authentication con correo y contraseña, control de sesión en memoria y protección de rutas privadas desde el frontend. El uso institucional de correos autorizados es una condición operativa, no una validación estricta del código actual.",
        "Base de datos: Firebase Firestore como plataforma de almacenamiento en la nube, con sincronización en tiempo real, sin requerir infraestructura de servidor propia.":
            "Base de datos: Cloud Firestore como plataforma de almacenamiento en la nube, consultada y actualizada desde JavaScript mediante operaciones de lectura y escritura por usuario.",
        "Autenticación segura mediante correo institucional (@unisabaneta.edu.co), con gestión de sesiones, recuperación de contraseña y protección de rutas privadas.":
            "Autenticación mediante Firebase Email/Password, recuperación de contraseña por Firebase y protección de rutas privadas en el frontend. El correo institucional se mantiene como criterio operativo del proyecto.",
        "Motor de recomendación de cursos basado en perfil académico del estudiante: carrera, semestre, áreas de interés y progreso registrado.":
            "Módulo de recomendación de cursos basado en datos del perfil, cursos disponibles, modalidad, progreso guardado y tareas sugeridas; no incluye machine learning en la versión 1.0.0.",
        "Personal administrativo designado con rol de Administrador para la gestión del catálogo de cursos, cupos y usuarios.":
            "Personal administrativo solo en versiones futuras o mediante gestión externa de Firebase; la versión 1.0.0 no incluye panel administrativo.",
        "Docentes o coordinadores académicos habilitados por decisión institucional para el acceso a reportes de seguimiento.":
            "Docentes o coordinadores académicos como usuarios futuros, sujetos a una ampliación funcional del sistema.",
        "La licencia autoriza el uso del SARC exclusivamente dentro del dominio institucional de UNISABANETA, con sede principal en Sabaneta, Antioquia, Colombia. El acceso remoto está permitido únicamente para Usuarios Autorizados que utilicen credenciales institucionales válidas.":
            "La licencia autoriza el uso del SARC para fines institucionales de UNISABANETA, con sede principal en Sabaneta, Antioquia, Colombia. El acceso remoto está permitido únicamente para usuarios autorizados por LA INSTITUCIÓN.",
        "Entregar el sistema con mecanismos de autenticación robusta: credenciales institucionales, gestión de sesiones con expiración automática y protección de rutas privadas.":
            "Entregar el sistema con mecanismos de autenticación acordes a la versión 1.0.0: Firebase Email/Password, protección de rutas privadas desde el frontend y reglas de Firestore por usuario.",
        "Gestionar las credenciales de administración con estricta confidencialidad, cambiándolas periódicamente y revocando accesos de usuarios que cesen su vinculación con la institución.":
            "Gestionar las cuentas autorizadas de Firebase con estricta confidencialidad y revocar accesos de usuarios que cesen su vinculación con la institución.",
        "Todos los accesos de Usuarios Autorizados deberán ser deshabilitados y las credenciales de administración invalidadas en un plazo no mayor a cinco (5) días hábiles.":
            "Todos los accesos de Usuarios Autorizados deberán ser deshabilitados en Firebase o en el mecanismo de autenticación vigente en un plazo no mayor a cinco (5) días hábiles.",
    }
    for old, new in replacements.items():
        replace_paragraph_contains(doc, old, new)
    doc.save(DOC_LICENSE)


def update_summary() -> None:
    backup(DOC_SUMMARY)
    doc = Document(DOC_SUMMARY)
    replacements = {
        "Territorio: Dominio institucional de UNISABANETA. El acceso remoto está permitido únicamente con credenciales institucionales válidas.":
            "Territorio: Uso institucional de UNISABANETA. El acceso remoto está permitido únicamente para usuarios autorizados por la institución.",
        "Usuarios autorizados: Estudiantes activos, personal administrativo con rol de Administrador y docentes habilitados institucionalmente.":
            "Usuarios autorizados: Estudiantes activos en la versión implementada. Roles administrativos o docentes quedan sujetos a ampliaciones futuras del sistema.",
    }
    for old, new in replacements.items():
        replace_paragraph_contains(doc, old, new)
    doc.save(DOC_SUMMARY)


def main() -> None:
    update_project_document()
    update_evaluation_report()
    update_license_document()
    update_summary()
    print("Documentos alineados con el proyecto actual.")


if __name__ == "__main__":
    main()
