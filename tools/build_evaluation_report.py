"""Genera un informe narrativo de cumplimiento del proyecto SARC."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_DIR / "Informe_evaluacion_SARC_vs_escala_Unisabaneta.docx"


def add_heading(document, text, level=1):
    """Agrega un encabezado institucional."""
    heading = document.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(8, 83, 148)
    return heading


def add_bullet(document, text):
    """Agrega un punto de lista compacto."""
    paragraph = document.add_paragraph(text, style="List Bullet")
    paragraph.paragraph_format.space_after = Pt(2)


def add_note_box(document, title, body):
    """Agrega un recuadro informativo sencillo."""
    table = document.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), "EAF2F8")
    tc_pr.append(shading)

    paragraph = cell.paragraphs[0]
    title_run = paragraph.add_run(title)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(8, 83, 148)
    paragraph.add_run("\n" + body)
    document.add_paragraph()


def configure_document(document):
    """Configura márgenes y tipografía general."""
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    styles = document.styles
    styles["Normal"].font.name = "Segoe UI"
    styles["Normal"].font.size = Pt(10)


def add_cover(document):
    """Crea la portada del informe."""
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Informe de Revisión del Proyecto SARC\nsegún la Escala de Evaluación Unisabaneta")
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(8, 83, 148)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.add_run("Sistema de Apoyo Académico con Recomendación de Cursos")
    subtitle_run.font.size = Pt(12)
    subtitle_run.font.color.rgb = RGBColor(80, 80, 80)

    author = document.add_paragraph()
    author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_run = author.add_run("Lorena Roa Rivera")
    author_run.font.size = Pt(11)


def build_document():
    """Construye el informe final en formato DOCX."""
    document = Document()
    configure_document(document)
    add_cover(document)

    add_heading(document, "1. Propósito del informe", 1)
    document.add_paragraph(
        "Este documento presenta una revisión organizada del proyecto SARC frente a los aspectos solicitados "
        "en la escala de evaluación de proyectos de Unisabaneta. El objetivo es identificar qué elementos ya "
        "están presentes en el proyecto, cuáles se encuentran en desarrollo y qué aspectos pueden fortalecerse "
        "antes de la entrega o sustentación."
    )

    add_heading(document, "2. Evidencias revisadas", 1)
    for item in [
        "Escala de Evaluación Proyectos Unisabaneta.",
        "Documento proyecto SARC - Lorena Roa Rivera.",
        "Minuta Licenciamiento - Lorena Roa.",
        "Código actual del proyecto SARC desarrollado con HTML5, CSS3 y JavaScript puro.",
        "Estructura modular del proyecto en carpetas pages, shared, assets y herramientas de documentación.",
    ]:
        add_bullet(document, item)

    add_heading(document, "3. Estado general del proyecto", 1)
    document.add_paragraph(
        "El proyecto SARC cuenta con una base funcional y documental sólida para una entrega académica. "
        "La aplicación implementa una experiencia web navegable que permite al estudiante iniciar sesión, "
        "recuperar contraseña, ver cursos sugeridos, filtrar recomendaciones, consultar detalles de cursos, "
        "inscribirse, visualizar progreso, descargar reportes en PDF y editar su perfil."
    )
    document.add_paragraph(
        "El código fue reorganizado en una estructura profesional por vistas, con archivos HTML, CSS y "
        "JavaScript independientes para cada pantalla. Además, se separaron módulos compartidos para estado, "
        "navegación, cursos, reportes, sonido, componentes de feedback y estilos globales."
    )
    add_note_box(
        document,
        "Nota sobre arquitectura y base de datos",
        "La documentación técnica puede ajustarse para reflejar la evolución real del proyecto. Actualmente, "
        "la demo funciona como frontend modular con persistencia local, y la base de datos se encuentra en "
        "desarrollo con Firebase. Por tanto, se recomienda actualizar los documentos para describir Firebase "
        "como tecnología de datos en proceso de implementación, evitando presentar como final una arquitectura "
        "que todavía está en construcción."
    )

    add_heading(document, "4. Aspectos que el proyecto ya tiene", 1)

    add_heading(document, "4.1 Problema, contexto y justificación", 2)
    document.add_paragraph(
        "El proyecto define un problema claro relacionado con la necesidad de apoyar a estudiantes en áreas "
        "académicas transversales como matemáticas, inglés y programación. También explica la importancia de "
        "centralizar cursos complementarios y orientar al estudiante según sus necesidades."
    )
    add_bullet(document, "Tiene planteamiento del problema.")
    add_bullet(document, "Tiene objetivo general y objetivos específicos.")
    add_bullet(document, "Tiene alcance del sistema y público objetivo.")
    add_bullet(document, "Tiene justificación académica e institucional.")

    add_heading(document, "4.2 Requisitos y funcionalidades", 2)
    document.add_paragraph(
        "El documento del proyecto incluye requisitos funcionales, requisitos no funcionales, reglas de negocio, "
        "casos de uso e historias de usuario. En el código actual se evidencia la implementación de los flujos "
        "principales del estudiante."
    )
    for item in [
        "Inicio de sesión con credenciales demo.",
        "Recuperación y actualización de contraseña.",
        "Dashboard con cursos sugeridos y asistente virtual.",
        "Catálogo de recomendaciones con filtros por área y modalidad.",
        "Detalle de curso con descripción, duración y nivel.",
        "Inscripción a cursos con mensajes de confirmación.",
        "Pantalla de progreso con barras e información del curso.",
        "Generación de reporte PDF simulado.",
        "Perfil editable con foto, modalidad y contraseña.",
    ]:
        add_bullet(document, item)

    add_heading(document, "4.3 Diseño y organización del código", 2)
    document.add_paragraph(
        "La estructura actual del proyecto facilita el mantenimiento porque separa cada vista en sus propios "
        "archivos y ubica las funciones reutilizables en módulos compartidos."
    )
    for item in [
        "Cada vista tiene HTML, CSS y JavaScript independiente.",
        "Los estilos globales están en shared/css.",
        "La lógica reutilizable está en shared/js.",
        "Los componentes de mensajes y modales están en shared/components.",
        "El archivo index.html funciona como contenedor principal de la aplicación.",
    ]:
        add_bullet(document, item)

    add_heading(document, "4.4 Documentación legal y técnica", 2)
    document.add_paragraph(
        "El proyecto cuenta con documentación técnica y minuta de licenciamiento. Esto fortalece los criterios "
        "de documentación, ética, legalidad y propiedad intelectual."
    )
    add_bullet(document, "Existe documento técnico del proyecto.")
    add_bullet(document, "Existe minuta de licenciamiento de software.")
    add_bullet(document, "Existe README con instrucciones de ejecución.")
    add_bullet(document, "Existe documentación del código reorganizado.")

    add_heading(document, "5. Aspectos que están en desarrollo o requieren ajuste", 1)

    add_heading(document, "5.1 Base de datos y persistencia", 2)
    document.add_paragraph(
        "La versión actual utiliza Firebase Authentication y Cloud Firestore para la persistencia de datos. "
        "Los documentos se organizan en colecciones globales filtradas por userId para separar la información "
        "de múltiples usuarios."
    )
    add_bullet(document, "Authentication gestiona usuarios con correo y contraseña.")
    add_bullet(document, "Firestore guarda perfil, cursos, recomendaciones y tareas por userId.")
    add_bullet(document, "Las reglas de Firestore protegen el acceso a documentos de otros usuarios.")

    add_heading(document, "5.2 Seguridad", 2)
    document.add_paragraph(
        "El sistema tiene validaciones de formularios, navegación protegida y autenticación con Firebase. "
        "Para una versión productiva conviene complementar estas medidas con pruebas de reglas, monitoreo "
        "y políticas de protección de datos personales."
    )
    for item in [
        "Verificar reglas de seguridad con usuarios reales y casos negativos.",
        "Documentar el flujo de recuperación de contraseña administrado por Firebase.",
        "Validar dominios autorizados y configuración del proyecto Firebase.",
        "Falta documentar medidas básicas de protección de datos personales.",
    ]:
        add_bullet(document, item)

    add_heading(document, "5.3 Pruebas", 2)
    document.add_paragraph(
        "El documento del proyecto contiene plan y casos de prueba, pero aún falta evidencia de ejecución. "
        "Para fortalecer la entrega, conviene agregar un reporte de pruebas manual o automatizado."
    )
    add_bullet(document, "Faltan capturas de pruebas realizadas.")
    add_bullet(document, "Falta tabla de resultado esperado frente a resultado obtenido.")
    add_bullet(document, "Faltan pruebas automatizadas unitarias o de navegación.")

    add_heading(document, "5.4 Despliegue y DevOps", 2)
    document.add_paragraph(
        "El proyecto puede ejecutarse localmente mediante app.py, pero todavía no cuenta con despliegue público, "
        "pipeline de integración continua ni entornos separados. Para una entrega académica puede ser suficiente "
        "si se entrega como demo local; para nivel profesional, debe fortalecerse."
    )
    add_bullet(document, "Tiene ejecución local documentada.")
    add_bullet(document, "Falta demo publicada o evidencia de despliegue.")
    add_bullet(document, "Falta configuración de CI/CD o pipeline.")

    add_heading(document, "5.5 Manual de usuario", 2)
    document.add_paragraph(
        "Aunque el sistema tiene documentación técnica, sería recomendable agregar un manual de usuario con "
        "capturas de pantalla y pasos de uso. Esto ayudaría a evidenciar usabilidad y producto final."
    )
    add_bullet(document, "Agregar pasos para iniciar sesión.")
    add_bullet(document, "Agregar pasos para inscribirse a un curso.")
    add_bullet(document, "Agregar pasos para consultar progreso y descargar reporte.")
    add_bullet(document, "Agregar pasos para editar perfil.")

    add_heading(document, "6. Ajustes recomendados en los documentos", 1)
    document.add_paragraph(
        "Como los documentos pueden modificarse, se recomienda alinearlos con el estado real del proyecto y "
        "con las decisiones tecnológicas actuales. Esto evita inconsistencias durante la evaluación."
    )
    for item in [
        "Actualizar la arquitectura para indicar que la base de datos se está desarrollando con Firebase.",
        "Eliminar o dejar como alternativa futura referencias a tecnologías que no correspondan con la entrega actual.",
        "Aclarar que la versión actual es un prototipo funcional frontend con evolución hacia persistencia en Firebase.",
        "Actualizar los requisitos no funcionales de seguridad para indicar qué está implementado y qué queda pendiente.",
        "Agregar una sección de limitaciones actuales y mejoras futuras.",
    ]:
        add_bullet(document, item)

    add_heading(document, "7. Recomendaciones antes de enviar", 1)
    for item in [
        "Incluir este informe como anexo de revisión del estado actual.",
        "Actualizar el documento técnico para reflejar Firebase como base de datos en desarrollo.",
        "Agregar un pequeño reporte de pruebas manuales con capturas.",
        "Preparar una sustentación honesta: prototipo funcional actual y evolución hacia Firebase.",
        "No presentar como final elementos que todavía están en construcción.",
        "Mantener la estructura modular actual porque facilita mejorar el proyecto sin rehacerlo.",
    ]:
        add_bullet(document, item)

    add_heading(document, "8. Conclusión", 1)
    document.add_paragraph(
        "El proyecto SARC cumple con una parte importante de los criterios funcionales, documentales y de "
        "organización del código. La aplicación ya demuestra el flujo principal del estudiante y está preparada "
        "para seguir evolucionando. Los principales ajustes pendientes son alinear la documentación con la "
        "implementación real, completar la integración de Firebase, fortalecer seguridad, agregar evidencias de "
        "pruebas y preparar un manual de usuario."
    )
    document.add_paragraph(
        "Con estos ajustes, el proyecto puede presentarse de forma más coherente y sólida ante la escala de "
        "evaluación, mostrando claramente lo que ya está implementado y lo que se encuentra en desarrollo."
    )

    document.save(OUTPUT_PATH)


if __name__ == "__main__":
    build_document()
