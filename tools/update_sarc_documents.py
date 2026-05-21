"""Actualiza los documentos SARC para alinearlos con el proyecto real."""

from pathlib import Path
import shutil

from docx import Document


DOCUMENTO_PROYECTO = Path(r"C:\Users\Usuario\OneDrive\Desktop\Documento proyecto SARC - Lorena Roa Rivera.docx")
MINUTA = Path(r"C:\Users\Usuario\OneDrive\Desktop\Minuta Licenciamiento-Lorena Roa.docx")
BACKUP_DIR = Path(r"C:\Users\Usuario\OneDrive\Desktop\Proyecto_SARC\backups_documentos")


def replace_paragraph_text(paragraph, new_text):
    """Reemplaza el texto de un párrafo conservando su estilo base."""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(new_text)


def replace_if_contains(paragraphs, needle, new_text):
    """Reemplaza un párrafo si contiene un texto específico."""
    changed = 0
    for paragraph in paragraphs:
        if needle in paragraph.text:
            replace_paragraph_text(paragraph, new_text)
            changed += 1
    return changed


def set_cell(cell, new_text):
    """Actualiza el texto de una celda conservando el estilo del primer párrafo."""
    paragraph = cell.paragraphs[0]
    replace_paragraph_text(paragraph, new_text)
    for extra in cell.paragraphs[1:]:
        replace_paragraph_text(extra, "")


def backup_file(path):
    """Crea una copia de seguridad dentro del proyecto antes de editar."""
    BACKUP_DIR.mkdir(exist_ok=True)
    target = BACKUP_DIR / path.name
    shutil.copy2(path, target)


def update_project_document():
    """Actualiza documento técnico y funcional del proyecto."""
    backup_file(DOCUMENTO_PROYECTO)
    doc = Document(DOCUMENTO_PROYECTO)

    replace_if_contains(
        doc.paragraphs,
        "Se conecta a la base de datos de estudiantes",
        "El SARC es un sistema web independiente que funciona como complemento al sistema académico oficial, sin reemplazarlo. En la versión actual opera como prototipo funcional frontend con persistencia local para la demo, y la base de datos institucional se encuentra en desarrollo mediante Firebase para soportar autenticación, almacenamiento y consulta de información académica.",
    )

    replace_if_contains(
        doc.paragraphs,
        "El SARC implementa una arquitectura de tres capas",
        "El SARC implementa una arquitectura web modular basada en vistas independientes y módulos compartidos. La versión actual utiliza HTML5, CSS3 y JavaScript puro en el frontend, con persistencia local para demostración y una integración de base de datos en desarrollo con Firebase.",
    )

    replace_if_contains(
        doc.paragraphs,
        "Recommendation Engine: Analiza el perfil",
        "Recommendation Module: Presenta sugerencias académicas a partir de los cursos disponibles, el perfil demo del estudiante y las tareas configuradas. En versiones posteriores podrá conectarse a Firebase para generar recomendaciones con datos persistentes.",
    )

    interaction_replacements = {
        "El cliente (navegador) realiza peticiones HTTP/HTTPS al servidor Nginx.": "El navegador carga el archivo index.html, los estilos globales y el módulo principal shared/js/app.js.",
        "Nginx actúa como proxy inverso y enruta las peticiones al servidor de aplicación (Express.js).": "El módulo app.js controla la navegación por hash, valida la sesión demo y renderiza la vista correspondiente.",
        "El servidor de aplicación valida la sesión del usuario y ejecuta la lógica de negocio.": "Cada vista carga su plantilla HTML, aplica su CSS propio y registra sus eventos en JavaScript puro.",
        "El servidor consulta o actualiza PostgreSQL y/o Redis según la operación.": "La aplicación guarda datos en Cloud Firestore y autentica usuarios con Firebase Authentication.",
        "La respuesta se devuelve en formato JSON al frontend.": "Los módulos compartidos administran cursos, modales, reportes PDF, navegación y estado global.",
        "El frontend actualiza la interfaz de usuario de forma reactiva.": "La interfaz se actualiza dinámicamente al cambiar la ruta o ejecutar acciones como inscripción, edición de perfil o descarga de reportes.",
    }
    for old_text, new_text in interaction_replacements.items():
        replace_if_contains(doc.paragraphs, old_text, new_text)

    # Requisitos no funcionales.
    table = doc.tables[4]
    set_cell(table.rows[1].cells[2], "Las credenciales deben gestionarse de forma segura en la versión con Firebase Authentication. En la demo actual se usan datos simulados y sesión local con expiración.")
    set_cell(table.rows[4].cells[2], "El sistema debe responder adecuadamente en un entorno académico de demostración y quedar preparado para escalar mediante servicios administrados de Firebase.")
    set_cell(table.rows[7].cells[2], "La disponibilidad dependerá del entorno de despliegue seleccionado. Para la versión con Firebase, se proyecta el uso de servicios administrados para mejorar disponibilidad.")
    set_cell(table.rows[8].cells[2], "La arquitectura debe permitir evolucionar desde el prototipo frontend hacia una solución con Firebase para autenticación, base de datos y almacenamiento.")

    # Ficha técnica.
    table = doc.tables[19]
    updates = {
        3: "Aplicación web accesible desde navegador, sin instalación. La versión actual usa HTML5, CSS3 y JavaScript puro con módulos ES; la persistencia real se encuentra en desarrollo con Firebase.",
        4: "Arquitectura frontend modular por vistas y módulos compartidos. La demo usa persistencia local y se proyecta Firebase como capa de autenticación y base de datos.",
        6: "No aplica servidor propio en la versión actual; se proyecta integración con servicios de Firebase.",
        7: "JavaScript puro, sin frameworks frontend.",
        8: "Servicios de Firebase en desarrollo para autenticación y base de datos; no se usa framework de servidor propio en esta versión.",
        9: "Cloud Firestore como base de datos principal, con documentos asociados a userId.",
        10: "Firebase Authentication con correo y contraseña para credenciales y sesiones gestionadas.",
        11: "Generación de reportes PDF implementada en JavaScript puro desde el frontend, sin depender de un servidor propio.",
        13: "Ejecución local mediante app.py para desarrollo y pruebas. Como despliegue futuro se puede usar hosting estático o servicios de Firebase.",
        14: "Servidor local simple con app.py durante desarrollo. Para publicación se proyecta un hosting web compatible con archivos estáticos y Firebase.",
        15: "HTTP local durante desarrollo. En despliegue público se recomienda HTTPS mediante el proveedor de hosting seleccionado.",
    }
    for row_index, value in updates.items():
        set_cell(table.rows[row_index].cells[1], value)
    set_cell(table.rows[6].cells[0], "Servicios de datos")
    set_cell(table.rows[8].cells[0], "Servicios externos")

    # Cronograma.
    table = doc.tables[22]
    set_cell(table.rows[8].cells[2], "Se diseñan las estructuras de datos necesarias para usuarios, cursos, progreso y recomendaciones, considerando Firebase como base de datos del proyecto.")
    set_cell(table.rows[8].cells[6], "En desarrollo")
    set_cell(table.rows[11].cells[2], "Se prepara el entorno de trabajo, la estructura modular del frontend y la integración progresiva con Firebase para persistencia de datos.")
    set_cell(table.rows[11].cells[6], "En desarrollo")

    # Capas del sistema.
    table = doc.tables[24]
    set_cell(table.rows[1].cells[1], "Interfaz de usuario desarrollada con HTML5, CSS3 y JavaScript puro. Cada pantalla se organiza en archivos independientes dentro de pages/, y los módulos compartidos se ubican en shared/.")
    set_cell(table.rows[2].cells[0], "Capa de Lógica de Aplicación")
    set_cell(table.rows[2].cells[1], "Lógica de aplicación implementada en JavaScript puro en el navegador. Incluye navegación, validación de sesión demo, filtros, inscripción, progreso, reportes PDF y edición de perfil.")
    set_cell(table.rows[3].cells[1], "Persistencia con Cloud Firestore para usuarios, cursos, progreso, tareas y recomendaciones, usando userId para separar la información de cada usuario.")

    # Modelo de datos proyectado para Firebase.
    table = doc.tables[25]
    set_cell(table.rows[0].cells[0], "Colección")
    model_updates = {
        1: "Colección de estudiantes. Campos: id, nombre, correo, facultad, carrera, semestre, modalidad_preferida, foto_perfil y fecha_registro. La autenticación se proyecta mediante Firebase Authentication.",
        2: "Colección de cursos. Campos: id, nombre, descripcion, duracion_semanas, nivel, area_interdisciplinaria, modalidad, cupos_disponibles y cupos_totales.",
        3: "Colección de inscripciones. Campos: id, estudiante_id, curso_id, fecha_inscripcion y estado.",
        4: "Colección de progreso. Campos: id, inscripcion_id, porcentaje_progreso, lecciones_completadas, total_lecciones, tiempo_invertido_horas, promedio_evaluaciones, recomendacion_sistema y ultimo_acceso.",
        5: "Colección de recomendaciones. Campos: id, estudiante_id, texto_recomendacion, tipo y fecha_generacion.",
        6: "Colección o subcolección de cursos alternativos. Campos: curso_original_id y curso_alternativo_id para sugerencias cuando no hay cupos.",
    }
    for row_index, value in model_updates.items():
        set_cell(table.rows[row_index].cells[1], value)

    table = doc.tables[26]
    relation_updates = {
        1: "Un estudiante puede tener múltiples documentos de inscripción asociados por estudiante_id.",
        2: "Un curso puede aparecer en múltiples documentos de inscripción asociados por curso_id.",
        3: "Cada inscripción puede tener un documento de progreso asociado.",
        4: "Un estudiante puede recibir múltiples documentos de recomendación.",
        5: "Un curso puede tener múltiples referencias a cursos alternativos definidos.",
    }
    for row_index, value in relation_updates.items():
        set_cell(table.rows[row_index].cells[2], value)

    # Caso de prueba de seguridad.
    table = doc.tables[27]
    set_cell(table.rows[11].cells[3], "Intento de acceso a ruta privada sin sesión activa o sesión local expirada")
    set_cell(table.rows[11].cells[4], "Redirección al login en la demo actual. En la versión Firebase, rechazo de acceso si no existe usuario autenticado.")

    doc.save(DOCUMENTO_PROYECTO)


def update_license_document():
    """Actualiza minuta de licenciamiento."""
    backup_file(MINUTA)
    doc = Document(MINUTA)

    replacements = {
        "Software / SARC: La aplicación web denominada «Sistema de Apoyo Académico con Recomendación de Cursos», versión 1.0.0, desarrollada con arquitectura de tres capas (Frontend HTML5/CSS3/JS, Backend Node.js/Express.js vía API REST, y base de datos PostgreSQL con Redis).":
        "Software / SARC: La aplicación web denominada «Sistema de Apoyo Académico con Recomendación de Cursos», versión 1.0.0, desarrollada con HTML5, CSS3 y JavaScript puro bajo una arquitectura frontend modular por vistas y módulos compartidos. La versión actual utiliza Firebase Authentication y Cloud Firestore para autenticación y persistencia.",
        "Backend: lógica de negocio implementada mediante API REST con Node.js y Express.js.":
            "Lógica de aplicación: implementada en JavaScript puro en el navegador, con módulos para autenticación demo, navegación, cursos, progreso, reportes y perfil. La integración con servicios de Firebase se encuentra en desarrollo.",
        "Base de datos: motor relacional PostgreSQL para almacenamiento persistente, complementado con Redis para gestión de sesiones y caché.":
            "Base de datos: Cloud Firestore con colecciones globales protegidas por userId. La autenticación se gestiona mediante Firebase Authentication.",
    }

    for old_text, new_text in replacements.items():
        replace_if_contains(doc.paragraphs, old_text, new_text)

    replace_if_contains(
        doc.paragraphs,
        "Autenticación segura mediante correo institucional",
        "Autenticación demo mediante correo institucional, gestión de sesión local, recuperación de contraseña y protección básica de rutas privadas. En la versión con Firebase se proyecta autenticación real mediante servicios administrados.",
    )

    replace_if_contains(
        doc.paragraphs,
        "Motor de recomendación de cursos basado en perfil académico",
        "Módulo de recomendación de cursos basado en datos académicos demo, cursos disponibles y tareas sugeridas. En versiones posteriores podrá apoyarse en Firebase para usar información persistente del estudiante.",
    )

    replace_if_contains(
        doc.paragraphs,
        "Entregar el sistema con mecanismos de autenticación robusta",
        "Entregar el sistema con mecanismos de autenticación acordes al alcance de la versión entregada: autenticación demo en la versión local y proyección de Firebase Authentication para una versión con usuarios persistentes.",
    )

    replace_if_contains(
        doc.paragraphs,
        "Realizar copias de seguridad periódicas de la base de datos del SARC",
        "Realizar copias de seguridad periódicas o exportaciones de la información almacenada en Firebase cuando la base de datos se encuentre implementada, garantizando su recuperación y protección.",
    )

    doc.save(MINUTA)


if __name__ == "__main__":
    update_project_document()
    update_license_document()
    print("Documentos actualizados correctamente.")
