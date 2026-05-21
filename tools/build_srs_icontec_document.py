"""Genera documentacion academica SRS IEEE 830 / ICONTEC para SARC."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT = PROJECT_DIR / "Documentos" / "SARC_SRS_IEEE830_ICONTEC.docx"

BLUE = "0B4F8A"
GREEN = "6AA84F"
LIGHT_BLUE = "EAF3FA"
LIGHT_GREEN = "EAF5E6"
LIGHT_GRAY = "F2F4F7"
TEXT = RGBColor(31, 41, 55)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text: str, bold: bool = False, size: int = 9) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(str(text))
    run.bold = bold
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = TEXT
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        set_cell_text(hdr.cells[i], header, bold=True, size=8)
        set_cell_shading(hdr.cells[i], BLUE)
        hdr.cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        if widths:
            hdr.cells[i].width = Inches(widths[i])
    for row_values in rows:
        row = table.add_row()
        for i, value in enumerate(row_values):
            set_cell_text(row.cells[i], value, size=8)
            if widths:
                row.cells[i].width = Inches(widths[i])
    doc.add_paragraph()


def add_gantt_matrix(doc: Document) -> None:
    """Agrega un cronograma visual por semanas con colores institucionales."""
    headers = ["Fase", "Actividad", "Febrero", "Marzo", "Abril", "Mayo", "Estado"]
    rows = [
        ["F1", "Requisitos y alcance", 1, 0, 0, 0, "Terminado"],
        ["F2", "Arquitectura, datos y mockups", 0, 1, 0, 0, "Terminado"],
        ["F3", "Login, Firebase y rutas", 0, 1, 1, 0, "Terminado"],
        ["F3", "Cursos, filtros e inscripcion", 0, 0, 1, 0, "Terminado"],
        ["F3", "Progreso, perfil y reportes", 0, 0, 1, 0, "Terminado"],
        ["F4", "Pruebas y ajustes visuales", 0, 0, 0, 1, "En cierre"],
        ["F5", "Documentacion y sustentacion", 0, 0, 0, 1, "En cierre"],
    ]

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        set_cell_text(hdr.cells[i], header, bold=True, size=6)
        set_cell_shading(hdr.cells[i], BLUE)
        hdr.cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for row_values in rows:
        row = table.add_row()
        for i, value in enumerate(row_values):
            cell = row.cells[i]
            if i in (0, 1, len(headers) - 1):
                set_cell_text(cell, value, bold=(i == 0), size=6)
                if i == 0:
                    set_cell_shading(cell, LIGHT_BLUE)
                elif i == len(headers) - 1:
                    set_cell_shading(cell, LIGHT_GREEN if value == "Terminado" else LIGHT_GRAY)
            else:
                set_cell_text(cell, "Activo" if value else " ", size=6)
                set_cell_shading(cell, GREEN if value else "FFFFFF")
    doc.add_paragraph()


def add_toc(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("TABLA DE CONTENIDO")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor.from_string(BLUE)
    p = doc.add_paragraph()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), r'TOC \o "1-3" \h \z \u')
    p._p.append(fld)
    note = doc.add_paragraph("Nota: en Microsoft Word, haga clic derecho sobre la tabla y seleccione 'Actualizar campo' para refrescar la numeración de páginas.")
    note.style = "Caption"
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_page_number(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Página ")
    run.font.name = "Arial"
    run.font.size = Pt(9)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    p._p.append(fld)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor.from_string(BLUE if level == 1 else "1F2937")


def add_para(doc: Document, text: str, style: str | None = None, align: int | None = None) -> None:
    p = doc.add_paragraph(style=style)
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11)
    run.font.color.rgb = TEXT


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(item)
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.color.rgb = TEXT


def add_numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(item)
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.color.rgb = TEXT


def add_placeholder(doc: Document, title: str, instruction: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, LIGHT_GREEN)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p = cell.add_paragraph(instruction)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.name = "Arial"
        run.font.size = Pt(9)
    doc.add_paragraph()


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_after = Pt(6)
    for name in ["Heading 1", "Heading 2", "Heading 3"]:
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.bold = True
        style.paragraph_format.space_before = Pt(10)
        style.paragraph_format.space_after = Pt(6)
    doc.styles["Heading 1"].font.size = Pt(14)
    doc.styles["Heading 2"].font.size = Pt(12)
    doc.styles["Heading 3"].font.size = Pt(11)
    doc.styles["Caption"].font.name = "Arial"
    doc.styles["Caption"].font.size = Pt(9)


def apply_icontec_section(section) -> None:
    section.top_margin = Cm(3)
    section.bottom_margin = Cm(3)
    section.left_margin = Cm(4)
    section.right_margin = Cm(2)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)


def build_doc() -> Document:
    doc = Document()
    configure_styles(doc)
    for section in doc.sections:
        apply_icontec_section(section)
        add_page_number(section)

    # Portada ICONTEC
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SISTEMA DE APOYO ACADÉMICO CON RECOMENDACIÓN DE CURSOS (SARC)")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Especificación de Requerimientos de Software (SRS) basada en IEEE 830\nDocumentación académica y técnica bajo Norma ICONTEC")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    doc.add_paragraph()
    doc.add_paragraph()
    for line in [
        "Lorena Roa Rivera",
        "Proyecto universitario de Ingeniería Informática",
        "Docente evaluador: ______________________________",
        "Corporación Universitaria de Sabaneta - Unisabaneta",
        "Facultad de Ingeniería",
        "Sabaneta, Antioquia",
        "2026",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.name = "Arial"
        r.font.size = Pt(12)
    doc.add_page_break()

    add_toc(doc)
    doc.add_page_break()

    add_heading(doc, "1. Introducción", 1)
    add_para(doc, "El Sistema de Apoyo Académico con Recomendación de Cursos (SARC) es una plataforma web académica desarrollada para la Universidad de Sabaneta (Unisabaneta), orientada a estudiantes universitarios que requieren identificar, consultar e inscribirse en cursos complementarios de apoyo a su formación profesional. El proyecto se fundamenta en la necesidad de fortalecer competencias transversales como matemáticas, programación, idiomas y habilidades interdisciplinarias mediante una solución web centralizada.")
    add_para(doc, "Desde el punto de vista tecnológico, SARC corresponde a una aplicación web modular construida con HTML5, CSS3 y JavaScript ES Modules. La versión analizada integra Firebase Authentication para autenticación por correo y contraseña, Cloud Firestore para persistencia de datos académicos por usuario, y un servidor local en Python para la ejecución de la aplicación durante desarrollo. El proyecto no utiliza frameworks frontend ni backend tradicionales; su diseño se basa en módulos JavaScript compartidos, plantillas HTML por vista y estado global administrado en memoria.")
    add_para(doc, "Los sistemas de recomendación educativa son relevantes porque permiten orientar al estudiante hacia recursos formativos pertinentes, reduciendo la dispersión de información y facilitando decisiones académicas más informadas. En SARC, la recomendación implementada es de tipo funcional y basada en reglas: cursos disponibles, área, modalidad, progreso, calificaciones y tareas sugeridas. No se implementa machine learning ni analítica predictiva avanzada en la versión actual.")
    add_para(doc, "El presente documento consolida la documentación técnica y académica del proyecto bajo una estructura inspirada en la norma IEEE 830 para especificación de requerimientos de software, complementada con criterios de presentación académica ICONTEC. La información se construye a partir del código fuente, README, guía de Firebase, reglas de Firestore y documentos existentes en la carpeta Documentos.")

    add_heading(doc, "2. Planteamiento del problema", 1)
    add_para(doc, "En el contexto universitario, los estudiantes suelen encontrar dificultades para identificar cursos complementarios que respondan a sus necesidades académicas reales. La información sobre cursos de apoyo, refuerzo o formación interdisciplinaria puede estar distribuida en diferentes canales institucionales, lo que dificulta el acceso oportuno a oportunidades de aprendizaje.")
    add_para(doc, "Esta dispersión afecta especialmente áreas transversales como matemáticas, programación e inglés, donde el fortalecimiento temprano de competencias puede incidir en el desempeño académico, la permanencia estudiantil y la preparación profesional. Cuando el estudiante no cuenta con una orientación personalizada, puede desaprovechar recursos formativos disponibles o tomar decisiones poco alineadas con su perfil.")
    add_para(doc, "La problemática se manifiesta en bajo aprovechamiento de cursos complementarios, falta de seguimiento individualizado, dificultad para visualizar el progreso y ausencia de una herramienta que centralice recomendaciones, inscripción y reportes. El SARC surge como respuesta tecnológica a esta necesidad mediante una plataforma web que organiza la oferta complementaria y la presenta de forma navegable, filtrable y asociada al perfil del estudiante.")

    add_heading(doc, "3. Justificación", 1)
    add_para(doc, "La implementación de SARC se justifica por su aporte institucional, académico y tecnológico. Institucionalmente, proporciona a Unisabaneta un prototipo funcional que centraliza cursos complementarios y puede servir como base para procesos futuros de acompañamiento estudiantil. Para los estudiantes, reduce la fricción de búsqueda, permite consultar cursos sugeridos, inscribirse, revisar progreso y descargar reportes de avance.")
    add_para(doc, "Académicamente, el sistema contribuye al fortalecimiento de competencias interdisciplinarias al visibilizar cursos de matemáticas, programación, idiomas, derecho, comunicación y formulación de proyectos. La lógica de recomendación, aunque no predictiva, permite orientar acciones concretas con base en cursos inscritos, rendimiento y modalidad preferida.")
    add_para(doc, "Desde la ingeniería de software, el proyecto evidencia una arquitectura modular comprensible y mantenible: vistas separadas por carpeta, módulos compartidos para datos, navegación, Firebase, cursos, reportes y feedback visual. Además, integra buenas prácticas iniciales de seguridad al delegar credenciales a Firebase Authentication y aislar información en Firestore mediante reglas por userId.")

    add_heading(doc, "4. Objetivos", 1)
    add_heading(doc, "4.1 Objetivo general", 2)
    add_para(doc, "Desarrollar una plataforma web académica que facilite el acceso de estudiantes universitarios a cursos complementarios mediante un sistema de recomendación personalizada y seguimiento del progreso académico, fortaleciendo sus competencias interdisciplinarias y profesionales.")
    add_heading(doc, "4.2 Objetivos específicos", 2)
    objectives = [
        ["OE-01", "Implementar autenticación segura", "Permitir que los estudiantes accedan mediante correo y contraseña gestionados por Firebase Authentication, evitando almacenar contraseñas en Firestore."],
        ["OE-02", "Desarrollar recomendación de cursos", "Presentar cursos sugeridos y recomendaciones académicas a partir del perfil disponible, cursos inscritos, actividades evaluativas y rendimiento."],
        ["OE-03", "Crear catálogo filtrable", "Ofrecer filtros por área interdisciplinaria y modalidad para facilitar la exploración de cursos complementarios."],
        ["OE-04", "Diseñar seguimiento académico", "Mostrar progreso, estado, último acceso, actividades evaluativas y cálculo de nota final por curso inscrito."],
        ["OE-05", "Generar reportes", "Permitir la descarga de reportes PDF simples con información académica del estudiante y del curso."],
        ["OE-06", "Implementar asistente virtual", "Mostrar recomendaciones académicas de apoyo en el dashboard. En la versión actual opera como asistente basado en reglas, no como chatbot conversacional."],
        ["OE-07", "Gestionar perfil", "Permitir visualizar datos del estudiante, modificar modalidad preferida, actualizar contraseña y cambiar avatar local en base64."],
        ["OE-08", "Mejorar experiencia de aprendizaje", "Integrar navegación simple, modales, toasts, filtros y rutas protegidas para una experiencia clara en el prototipo web."],
    ]
    add_table(doc, ["ID", "Objetivo", "Explicación técnica y académica"], objectives, [0.8, 1.8, 4.3])

    add_heading(doc, "5. Alcance del sistema", 1)
    add_heading(doc, "5.1 Funcionalidades incluidas y estado real", 2)
    scope_rows = [
        ["Inicio de sesión", "Implementada", "Login con correo, contraseña, validación de dominio institucional en interfaz y autenticación Firebase."],
        ["Registro de usuario", "Funcionalidad futura o pendiente", "No existe pantalla ni flujo de registro en el código actual; los usuarios deben existir en Firebase Authentication o ser gestionados externamente."],
        ["Dashboard académico", "Implementada", "Vista de bienvenida, cursos sugeridos y asistente virtual con recomendaciones generadas desde datos académicos."],
        ["Sistema de recomendación", "Prototipada", "Recomendación por reglas y datos locales/Firestore; no usa inteligencia artificial predictiva ni machine learning."],
        ["Catálogo de cursos", "Implementada", "Vista Recomendaciones con listado de cursos sugeridos y acciones de detalle e inscripción."],
        ["Filtros por categoría y modalidad", "Implementada", "Selectores por área y modalidad en pages/recomendaciones."],
        ["Inscripción a cursos", "Implementada", "Controla cupos, evita duplicados por marca registered y actualiza estado del curso."],
        ["Seguimiento de progreso", "Implementada", "Muestra cursos inscritos, barras de progreso, actividades, cálculo ponderado y estado académico."],
        ["Perfil de usuario", "Implementada", "Muestra datos, avatar, modalidad, edición de contraseña y cierre de sesión."],
        ["Reportes descargables", "Implementada", "Generación de PDF simple desde JavaScript sin dependencia externa."],
        ["Asistente virtual", "Prototipada", "Panel de recomendaciones académicas; no hay conversación, NLP ni conexión con modelo externo."],
        ["Panel administrativo", "Funcionalidad futura o pendiente", "Mencionado como posible evolución; no existe carpeta, ruta ni interfaz administrativa."],
        ["Configuración", "Funcionalidad futura o pendiente", "No existe vista de configuración independiente; algunos ajustes están en Perfil."],
    ]
    add_table(doc, ["Funcionalidad", "Clasificación", "Soporte en el proyecto"], scope_rows, [1.8, 1.5, 3.6])
    add_heading(doc, "5.2 Exclusiones del sistema", 2)
    add_bullets(doc, [
        "No incluye módulo de pagos, facturación ni transacciones monetarias.",
        "No incluye gestión docente avanzada ni carga de contenidos académicos por profesores.",
        "No incluye videoconferencias, foros académicos ni mensajería interna.",
        "No implementa IA predictiva avanzada, modelos de machine learning ni detección automática de riesgo de deserción.",
        "No incluye integraciones externas institucionales distintas a Firebase.",
        "No incluye panel administrativo visual para gestión de usuarios, cursos o cupos.",
    ])

    add_heading(doc, "6. Descripción general del sistema", 1)
    add_heading(doc, "6.1 Arquitectura general", 2)
    add_para(doc, "SARC funciona como una aplicación web de una sola página con navegación por hash. El archivo index.html define el shell principal, carga estilos globales y registra shared/js/app.js como punto de entrada. El módulo app.js inicializa el estado, protege rutas privadas y renderiza la vista correspondiente según rutas como #login, #inicio, #recomendaciones, #detalle/{curso}, #progreso y #perfil.")
    add_para(doc, "Aunque no se utiliza un framework MVC formal, el proyecto puede documentarse como una arquitectura modular inspirada en MVC: el modelo se representa por state.db, defaultDatabase y Firebase; la vista se compone de plantillas HTML y CSS por pantalla; y los controladores son los módulos JavaScript que cargan plantillas, enlazan eventos, validan entradas y coordinan persistencia.")
    add_heading(doc, "6.2 Tecnologías utilizadas", 2)
    tech_rows = [
        ["HTML5", "Estructura de index.html y plantillas por vista."],
        ["CSS3", "Estilos globales, layout, componentes y hojas por pantalla."],
        ["JavaScript ES Modules", "Rutas, estado, renderizado, eventos, reglas de negocio, reportes PDF y Firebase."],
        ["Firebase Authentication", "Autenticación por correo/contraseña, recuperación y cambio de contraseña."],
        ["Cloud Firestore", "Persistencia de usuarios, cursos, recomendaciones, tareas y aceptación de Habeas Data."],
        ["Python http.server", "Servidor local app.py con MIME types, CORS y headers anti-cache para desarrollo."],
        ["No usado: frameworks frontend", "No se evidencia React, Angular, Vue, Bootstrap ni backend Express/Django/Flask."],
        ["No usado: localStorage", "La versión actual usa estado en memoria y Firestore; localStorage no aparece como persistencia activa."],
    ]
    add_table(doc, ["Tecnología", "Uso real en SARC"], tech_rows, [2.0, 4.8])
    add_heading(doc, "6.3 Usuarios del sistema", 2)
    add_table(doc, ["Actor", "Estado", "Descripción"], [
        ["Estudiante", "Implementado", "Usuario principal. Accede al sistema, consulta cursos, se inscribe, revisa progreso, descarga reportes y edita perfil."],
        ["Sistema", "Implementado", "Ejecuta validaciones, renderiza recomendaciones, controla cupos, guarda datos y genera reportes."],
        ["Administrador", "Futuro o pendiente", "Rol proyectado para gestión de cursos y usuarios. No existe interfaz administrativa en la versión actual."],
        ["Docente/coordinador", "Futuro o pendiente", "Rol potencial para seguimiento institucional o gestión de contenidos; no implementado."],
    ], [1.4, 1.4, 4.0])

    add_heading(doc, "7. Documento SRS basado en IEEE 830", 1)
    add_heading(doc, "7.1 Propósito", 2)
    add_para(doc, "Este SRS especifica las funciones, restricciones, dependencias, actores, reglas de negocio y requisitos de calidad del SARC. Está dirigido al equipo académico evaluador, a la desarrolladora, a posibles responsables técnicos institucionales y a futuros mantenedores del sistema.")
    add_heading(doc, "7.2 Requerimientos funcionales", 2)
    rf_rows = [
        ["RF-01", "Autenticación", "El sistema debe permitir iniciar sesión con correo institucional y contraseña mediante Firebase Authentication.", "Alta", "Implementado"],
        ["RF-02", "Validación de formulario", "El botón de ingreso debe activarse solo cuando el correo tenga formato válido, dominio @unisabaneta.edu.co, contraseña fuerte y aceptación de Habeas Data.", "Alta", "Implementado"],
        ["RF-03", "Habeas Data", "El sistema debe registrar la aceptación de tratamiento de datos personales en la colección habeasData.", "Alta", "Implementado"],
        ["RF-04", "Recuperación de contraseña", "El sistema debe solicitar recuperación mediante Firebase Authentication y redirigir al login.", "Alta", "Implementado"],
        ["RF-05", "Dashboard", "El sistema debe mostrar bienvenida, cursos sugeridos y recomendaciones del asistente virtual.", "Alta", "Implementado"],
        ["RF-06", "Filtrado de cursos", "El sistema debe filtrar cursos por área y modalidad desde la vista Recomendaciones.", "Media", "Implementado"],
        ["RF-07", "Detalle de curso", "El sistema debe mostrar descripción, duración, nivel y acción de inscripción.", "Media", "Implementado"],
        ["RF-08", "Inscripción", "El sistema debe permitir inscripción si hay cupos, marcar el curso como inscrito y disminuir cupo.", "Alta", "Implementado"],
        ["RF-09", "Sin cupos", "El sistema debe mostrar modal con alternativas cuando un curso no tenga cupos disponibles.", "Media", "Implementado"],
        ["RF-10", "Progreso académico", "El sistema debe mostrar cursos inscritos, avance, estado, último acceso y actividades evaluativas.", "Alta", "Implementado"],
        ["RF-11", "Cálculo de nota", "El sistema debe calcular nota final ponderada con base en actividades y porcentajes.", "Alta", "Implementado"],
        ["RF-12", "Reporte detallado", "El sistema debe abrir un modal con resumen de curso, lecciones, tiempo, actividades y nota final.", "Alta", "Implementado"],
        ["RF-13", "Descarga PDF", "El sistema debe generar un archivo PDF simple de progreso del curso.", "Alta", "Implementado"],
        ["RF-14", "Perfil", "El sistema debe visualizar datos del estudiante y avatar.", "Alta", "Implementado"],
        ["RF-15", "Edición de perfil", "El sistema debe permitir cambiar modalidad, avatar y contraseña.", "Media", "Implementado"],
        ["RF-16", "Cierre de sesión", "El sistema debe cerrar sesión en Firebase y volver al login.", "Alta", "Implementado"],
        ["RF-17", "Registro independiente", "El sistema debe permitir registrar estudiantes desde una vista formal.", "Media", "Pendiente"],
        ["RF-18", "Panel administrativo", "El sistema debe permitir administrar catálogo, cupos y usuarios.", "Media", "Futuro"],
    ]
    add_table(doc, ["ID", "Módulo", "Descripción", "Prioridad", "Estado"], rf_rows, [0.7, 1.2, 3.4, 0.8, 0.9])
    add_heading(doc, "7.3 Requerimientos no funcionales", 2)
    rnf_rows = [
        ["RNF-01", "Seguridad", "Las credenciales deben gestionarse exclusivamente con Firebase Authentication; no deben almacenarse contraseñas en Firestore.", "Alta"],
        ["RNF-02", "Privacidad", "La información académica debe separarse por userId y protegerse con reglas de Firestore.", "Alta"],
        ["RNF-03", "Usabilidad", "La interfaz debe mantener navegación clara por pantallas y mensajes de feedback mediante modales y toasts.", "Alta"],
        ["RNF-04", "Compatibilidad", "Debe ejecutarse en navegadores modernos compatibles con ES Modules, fetch y APIs de Blob/FileReader.", "Media"],
        ["RNF-05", "Rendimiento", "Las vistas deben renderizarse sin recarga completa de página y con plantillas cacheadas en memoria.", "Media"],
        ["RNF-06", "Disponibilidad", "La disponibilidad productiva depende de Firebase y del hosting elegido; en desarrollo depende del servidor local.", "Media"],
        ["RNF-07", "Escalabilidad", "La estructura por módulos permite agregar vistas y colecciones futuras sin reescribir todo el sistema.", "Media"],
        ["RNF-08", "Accesibilidad", "Los formularios incluyen aria-label en campos principales, pero se recomienda auditoría WCAG para una versión institucional.", "Media"],
        ["RNF-09", "Mantenibilidad", "El código debe conservar separación por vistas y módulos compartidos.", "Alta"],
    ]
    add_table(doc, ["ID", "Categoría", "Descripción", "Prioridad"], rnf_rows, [0.8, 1.2, 4.3, 0.8])
    add_heading(doc, "7.4 Reglas de negocio", 2)
    add_table(doc, ["ID", "Regla"], [
        ["RN-01", "Un estudiante no debe inscribirse dos veces en el mismo curso; el estado registered bloquea una inscripción duplicada."],
        ["RN-02", "Si no hay cupos disponibles, se informa al estudiante y se muestran alternativas configuradas en el curso."],
        ["RN-03", "Los cursos sugeridos principales corresponden a CORE_COURSE_IDS: matematicas, programacion e ingles."],
        ["RN-04", "La nota final se calcula como la suma ponderada de nota por porcentaje de cada actividad."],
        ["RN-05", "El reporte PDF incluye datos del estudiante, fecha, curso, modalidad, progreso, lecciones, tiempo, promedio, recomendación y estado."],
        ["RN-06", "El tratamiento de datos personales exige aceptación de Habeas Data antes de ingresar."],
    ], [0.8, 5.9])
    add_heading(doc, "7.5 Restricciones, suposiciones y dependencias", 2)
    add_table(doc, ["Tipo", "Descripción"], [
        ["Restricción", "La aplicación requiere servidor HTTP local o hosting web; no debe abrirse solo con doble clic porque usa fetch y módulos ES."],
        ["Restricción", "La versión actual no incluye backend propio; las operaciones de autenticación y base de datos dependen de Firebase."],
        ["Restricción", "La recuperación de contraseña depende del correo configurado en Firebase Authentication."],
        ["Suposición", "Los estudiantes cuentan con acceso a internet y navegador moderno."],
        ["Suposición", "La institución provee o valida datos académicos básicos como facultad, carrera y semestre."],
        ["Dependencia", "Firebase Authentication, Cloud Firestore, reglas firestore.rules y configuración compartida en firebase-config.js."],
        ["Dependencia", "Plantillas HTML cargadas desde pages/* mediante template-loader.js."],
    ], [1.2, 5.5])
    add_heading(doc, "7.6 Casos de uso y actores", 2)
    cu_rows = [
        ["CU-01", "Iniciar sesión", "Estudiante", "RF-01, RF-02"],
        ["CU-02", "Aceptar Habeas Data", "Estudiante", "RF-03"],
        ["CU-03", "Recuperar contraseña", "Estudiante", "RF-04"],
        ["CU-04", "Ver dashboard", "Estudiante", "RF-05"],
        ["CU-05", "Explorar catálogo", "Estudiante", "RF-06"],
        ["CU-06", "Consultar detalle", "Estudiante", "RF-07"],
        ["CU-07", "Inscribirse en curso", "Estudiante/Sistema", "RF-08, RF-09"],
        ["CU-08", "Ver progreso", "Estudiante", "RF-10, RF-11"],
        ["CU-09", "Descargar reporte", "Estudiante/Sistema", "RF-12, RF-13"],
        ["CU-10", "Editar perfil", "Estudiante", "RF-14, RF-15"],
        ["CU-11", "Cerrar sesión", "Estudiante", "RF-16"],
    ]
    add_table(doc, ["ID", "Caso de uso", "Actor", "Requisitos asociados"], cu_rows, [0.8, 2.1, 1.5, 2.2])
    add_heading(doc, "7.7 Priorización de requerimientos", 2)
    add_para(doc, "La priorización se define con base en el valor funcional para la demostración académica y el riesgo técnico. Autenticación, dashboard, catálogo, inscripción, progreso, reportes y seguridad se consideran de prioridad alta. Registro independiente, panel administrativo e integraciones avanzadas se clasifican como evolución futura.")

    add_heading(doc, "8. Análisis de mockups y prototipos", 1)
    mockups = [
        ["Login", "Autenticar al estudiante y validar aceptación de Habeas Data.", "Logo S, campos de correo y contraseña, checkbox de privacidad, botón INGRESAR y enlace recuperar.", "Ingreso -> dashboard; recuperar -> #recuperar.", "Correo institucional, contraseña fuerte y aceptación de datos."],
        ["Registro", "Crear estudiantes nuevos.", "No existe pantalla real en la versión actual.", "Pendiente.", "Pendiente. Funcionalidad futura."],
        ["Recuperación de contraseña", "Solicitar correo de recuperación mediante Firebase.", "Correo, nueva contraseña, confirmación, botones Volver y Enviar.", "Login -> Recuperar -> Login.", "Correo no vacío, longitud mínima y coincidencia de contraseñas."],
        ["Dashboard principal", "Mostrar bienvenida, cursos sugeridos y asistente.", "Banner verde, lista de cursos y panel de asistente virtual.", "Menú superior hacia recomendaciones, progreso y perfil.", "Solo accesible si hay sesión autenticada."],
        ["Panel de cursos recomendados", "Presentar cursos base recomendados.", "Botones de cursos Matemáticas, Programación e Inglés.", "Click abre detalle del curso.", "Curso debe existir en state.db.courses."],
        ["Catálogo de cursos", "Explorar y filtrar cursos sugeridos.", "Selectores de área y modalidad, listado con Ver detalles e Inscribirse.", "Filtros actualizan la lista; detalle/inscripción ejecutan eventos.", "No duplicar inscripción y validar cupos."],
        ["Perfil de usuario", "Visualizar y editar datos básicos.", "Datos personales, avatar, botones Editar Perfil, Reiniciar demo y Cerrar sesión.", "Modal de edición y cierre a login.", "Contraseña nueva fuerte y confirmada; contraseña actual requerida."],
        ["Seguimiento de progreso", "Visualizar avances y actividades.", "Barras, tarjetas de actividades, fórmula de nota, estado y botón reporte.", "Editar nota recalcula; reporte abre modal.", "Notas entre 0 y máximo; porcentajes idealmente suman 100%."],
        ["Reportes", "Consultar y descargar informe de progreso.", "Modal con datos del curso y botón Descargar PDF.", "Desde Progreso hacia modal y descarga local.", "Curso debe existir y tener datos suficientes."],
        ["Configuración", "Configurar preferencias generales.", "No existe pantalla independiente; modalidad se gestiona en Perfil.", "Pendiente.", "Funcionalidad futura."],
        ["Asistente virtual", "Orientar al estudiante con recomendaciones.", "Panel con recomendaciones por rendimiento académico.", "Se visualiza en Inicio.", "Basado en cursos inscritos y cálculo de rendimiento, no en chatbot."],
    ]
    add_table(doc, ["Pantalla", "Objetivo funcional", "Elementos visuales", "Flujo", "Validaciones"], mockups, [1.0, 1.6, 1.7, 1.2, 1.4])
    add_heading(doc, "8.1 Espacios para capturas de mockups", 2)
    for title, instruction in [
        ("Figura 1. Mockup de Login", "Insertar captura de la pantalla #login mostrando correo, contraseña, Habeas Data y botón INGRESAR."),
        ("Figura 2. Mockup de Recuperación", "Insertar captura de #recuperar con campos de correo, nueva contraseña y confirmación."),
        ("Figura 3. Mockup de Dashboard", "Insertar captura de #inicio con bienvenida, cursos sugeridos y asistente virtual."),
        ("Figura 4. Mockup de Catálogo", "Insertar captura de #recomendaciones con filtros por área/modalidad y listado de cursos."),
        ("Figura 5. Mockup de Detalle", "Insertar captura de #detalle/matematicas o un curso seleccionado con descripción, duración, nivel e inscripción."),
        ("Figura 6. Mockup de Progreso", "Insertar captura de #progreso mostrando barras, actividades evaluativas y cálculo de nota."),
        ("Figura 7. Mockup de Reporte", "Insertar captura del modal 'Reporte detallado de progreso' y, si se desea, del PDF descargado."),
        ("Figura 8. Mockup de Perfil", "Insertar captura de #perfil con datos del estudiante, avatar y acciones de cuenta."),
        ("Figura 9. Mockup de Modal Editar Perfil", "Insertar captura del modal de edición con modalidad, contraseña y selector de imagen."),
        ("Figura 10. Mockup móvil", "Insertar captura en vista móvil para evidenciar comportamiento responsivo del prototipo."),
    ]:
        add_placeholder(doc, title, instruction)

    add_heading(doc, "9. Arquitectura del sistema", 1)
    add_heading(doc, "9.1 Arquitectura modular inspirada en MVC", 2)
    add_table(doc, ["Capa conceptual", "Implementación real", "Responsabilidad"], [
        ["Modelo", "shared/js/data.js, state.db, defaultDatabase, Firebase Firestore", "Representa datos de usuario, cursos, actividades, recomendaciones y sesión."],
        ["Vista", "index.html, pages/*/*.html, shared/css/*.css, pages/*/*.css", "Define estructura visual, componentes y estilos de cada pantalla."],
        ["Controlador", "app.js, courses.js, módulos JS por vista", "Inicializa, enruta, enlaza eventos, valida, actualiza estado y persiste cambios."],
        ["Servicio", "firebase-service.js, pdf.js, template-loader.js", "Abstrae autenticación, persistencia, reportes PDF y carga de plantillas."],
    ], [1.4, 2.3, 3.0])
    add_heading(doc, "9.2 Frontend", 2)
    add_para(doc, "El frontend está compuesto por plantillas HTML independientes por vista, hojas CSS globales y específicas, y módulos JavaScript encargados de renderizar dinámicamente la interfaz dentro de viewContainer o authView. La navegación se realiza mediante window.location.hash.")
    add_heading(doc, "9.3 Backend y servicios", 2)
    add_para(doc, "No existe backend de aplicación propio. Firebase actúa como backend administrado para autenticación y base de datos. app.py no procesa lógica de negocio; únicamente sirve archivos estáticos durante desarrollo y agrega cabeceras CORS, MIME y anti-cache.")
    add_heading(doc, "9.4 Base de datos", 2)
    add_para(doc, "Cloud Firestore almacena colecciones globales con documentos asociados a userId. Las colecciones identificadas son usuarios, cursos, recomendaciones, tareasAsistente y habeasData. Las reglas de seguridad validan que request.auth.uid coincida con el usuario del documento.")
    add_heading(doc, "9.5 APIs, localStorage y seguridad", 2)
    add_para(doc, "Las APIs externas usadas corresponden al SDK modular de Firebase importado dinámicamente desde gstatic. No se evidencia uso activo de localStorage para persistencia en la versión actual. La seguridad se apoya en Firebase Authentication, reglas de Firestore, validaciones de formularios, aceptación de Habeas Data y separación de datos por userId.")
    add_heading(doc, "9.6 Flujo de datos", 2)
    add_numbered(doc, [
        "El navegador solicita index.html desde el servidor local o hosting web.",
        "index.html carga estilos y shared/js/app.js como módulo principal.",
        "app.js inicializa Firebase, espera el estado de autenticación y carga state.db.",
        "La ruta hash determina si se renderiza login/recuperación o dashboard.",
        "Las vistas cargan plantillas con template-loader.js e interpolan datos.",
        "Las acciones del usuario modifican state.db.",
        "saveDatabase() persiste cambios en Firestore mediante firebase-service.js.",
        "Los reportes PDF se generan en el navegador desde shared/js/pdf.js.",
    ])

    add_heading(doc, "10. Modelo de datos", 1)
    model_rows = [
        ["Usuario", "email, name, faculty, career, semester, modality, avatar, habeasDataAccepted", "Un usuario posee varios cursos, tareas y recomendaciones por userId."],
        ["Curso", "id, name, area, modality, seats, description, duration, level, enrolled, progress, status, activities", "Pertenece al conjunto académico del usuario; contiene actividades evaluativas."],
        ["Categoría", "area dentro de Curso", "No existe entidad independiente; se deriva del campo area."],
        ["Recomendación", "courseId, courseName, recommendation, alternatives", "Persistida por usuario/curso en Firestore y usada para orientación académica."],
        ["Inscripción", "enrolled, registered, seats dentro de Curso", "No existe colección separada; se representa como estado del curso por usuario."],
        ["Progreso", "progress, lessons, timeSpent, average, activities", "Asociado al curso inscrito y recalculado visualmente."],
        ["Reporte", "Generado bajo demanda", "No se persiste; pdf.js construye un PDF simple en el cliente."],
        ["Preferencias", "modality", "Integrada al perfil del usuario."],
        ["Asistente virtual", "assistantTasks y recomendaciones calculadas", "Prototipo basado en reglas y rendimiento, no chatbot."],
    ]
    add_table(doc, ["Entidad", "Atributos / representación", "Relaciones y observaciones"], model_rows, [1.3, 2.5, 3.0])
    add_heading(doc, "10.1 Cardinalidades", 2)
    add_bullets(doc, [
        "Un Usuario puede tener muchos Cursos asociados por userId.",
        "Un Curso puede tener muchas Actividades evaluativas.",
        "Un Usuario puede tener muchas Recomendaciones, una por curso recomendado o persistido.",
        "Un Usuario puede tener muchas Tareas del asistente.",
        "Un Reporte pertenece conceptualmente a un Curso y a un Usuario, pero se genera temporalmente y no se almacena.",
    ])

    add_heading(doc, "11. Plan de pruebas", 1)
    add_heading(doc, "11.1 Estrategia", 2)
    add_para(doc, "El plan de pruebas se orienta a validar el flujo funcional del estudiante, la persistencia con Firebase, la seguridad de acceso por usuario, la coherencia de cálculos académicos y la usabilidad de las pantallas principales. El proyecto no evidencia un framework de pruebas automatizadas, por lo cual se proponen pruebas manuales y futuras pruebas unitarias sobre funciones puras.")
    test_rows = [
        ["CP-01", "Login válido", "Correo institucional, contraseña válida, Habeas aceptado", "Ingresar datos y enviar formulario", "Dashboard #inicio", "Pendiente de evidenciar con captura", "Pendiente"],
        ["CP-02", "Login inválido", "Contraseña incorrecta", "Enviar formulario", "Toast de credenciales incorrectas", "Pendiente", "Pendiente"],
        ["CP-03", "Recuperar contraseña", "Correo registrado", "Enviar solicitud", "Correo Firebase enviado y retorno a login", "Pendiente", "Pendiente"],
        ["CP-04", "Filtrar cursos", "Área Matemáticas, modalidad Virtual", "Cambiar selects", "Lista actualizada", "Pendiente", "Pendiente"],
        ["CP-05", "Ver detalle", "Curso matematicas", "Clic Ver detalles", "Pantalla detalle con descripción", "Pendiente", "Pendiente"],
        ["CP-06", "Inscripción con cupos", "Curso disponible", "Clic INSCRIBIRSE", "Modal éxito, progress=5, cupos disminuyen", "Pendiente", "Pendiente"],
        ["CP-07", "Inscripción duplicada", "Curso registered=true", "Intentar inscribirse", "Botón deshabilitado o toast informativo", "Pendiente", "Pendiente"],
        ["CP-08", "Cálculo de nota", "Actividades con porcentajes y notas", "Cambiar nota", "Nota final y estado recalculados", "Pendiente", "Pendiente"],
        ["CP-09", "Descargar PDF", "Curso inscrito", "Abrir reporte y descargar", "Archivo reporte-{curso}.pdf", "Pendiente", "Pendiente"],
        ["CP-10", "Editar perfil", "Modalidad y avatar", "Actualizar perfil", "Perfil refrescado y guardado", "Pendiente", "Pendiente"],
        ["CP-11", "Seguridad Firestore", "Usuario A intenta documento de B", "Evaluar reglas", "Acceso denegado", "Pendiente", "Pendiente"],
        ["CP-12", "Responsive", "Viewport móvil", "Abrir pantallas principales", "Contenido visible sin solapamientos", "Pendiente", "Pendiente"],
    ]
    add_table(doc, ["ID", "Objetivo", "Datos de entrada", "Procedimiento", "Resultado esperado", "Resultado obtenido", "Estado"], test_rows, [0.55, 1.0, 1.2, 1.3, 1.5, 1.0, 0.7])
    add_heading(doc, "11.2 Pruebas unitarias, integración y seguridad", 2)
    add_bullets(doc, [
        "Pruebas unitarias futuras: calculateFinalGrade(), getAcademicStatus(), sanitizeFilename(), selected() y normalizeDatabase().",
        "Pruebas de integración: login -> carga Firestore -> dashboard; inscripción -> saveDatabase() -> Firestore; progreso -> reporte PDF.",
        "Pruebas de seguridad: reglas firestore.rules, aislamiento por userId, no almacenamiento de contraseñas y recuperación mediante Firebase.",
        "Pruebas de compatibilidad: Chrome, Edge, Firefox y vista móvil usando DevTools.",
    ])

    add_heading(doc, "12. Conclusiones", 1)
    add_para(doc, "El SARC constituye una solución web académica coherente con la problemática de centralización de cursos complementarios y orientación personalizada para estudiantes universitarios. La versión actual permite demostrar un flujo funcional completo: autenticación, dashboard, recomendaciones, catálogo, detalle, inscripción, progreso, reportes y perfil.")
    add_para(doc, "Desde el punto de vista institucional, el sistema puede contribuir a mejorar el acceso a oportunidades formativas y a fortalecer competencias interdisciplinarias. Desde la ingeniería de software, el proyecto evidencia separación modular, integración con Firebase, documentación técnica y una base mantenible para futuras ampliaciones.")
    add_para(doc, "El alcance actual debe diferenciar claramente lo implementado de lo prototipado y lo pendiente. La recomendación no corresponde a IA avanzada, el asistente virtual no es conversacional, el registro independiente no está implementado y el panel administrativo es una mejora futura. Esta claridad fortalece la validez académica del documento y evita inconsistencias técnicas.")

    add_heading(doc, "13. Bibliografía", 1)
    bibliography = [
        "IEEE. IEEE Recommended Practice for Software Requirements Specifications. IEEE Std 830-1998. New York: Institute of Electrical and Electronics Engineers, 1998.",
        "PRESSMAN, Roger S. Ingeniería del software: un enfoque práctico. 7. ed. México: McGraw-Hill, 2010.",
        "SOMMERVILLE, Ian. Ingeniería de software. 10. ed. Madrid: Pearson, 2016.",
        "FIREBASE. Firebase Documentation: Authentication and Cloud Firestore. Google, 2026. Disponible en: https://firebase.google.com/docs.",
        "W3C. Web Content Accessibility Guidelines (WCAG) 2.2. World Wide Web Consortium, 2023.",
        "COLOMBIA. Congreso de la República. Ley 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales.",
        "ISO/IEC/IEEE. Systems and software engineering - Life cycle processes - Requirements engineering. ISO/IEC/IEEE 29148, 2018.",
        "RICCI, Francesco; ROKACH, Lior; SHAPIRA, Bracha. Recommender Systems Handbook. 3. ed. New York: Springer, 2022.",
    ]
    for item in bibliography:
        add_para(doc, item)

    add_heading(doc, "14. Anexos", 1)
    add_heading(doc, "Anexo A. Diagrama UML de casos de uso", 2)
    add_para(doc, "El diagrama UML del sistema se representa textualmente porque el entregable documental reserva espacio para insertar la figura exportada desde una herramienta UML. El actor principal es Estudiante. Los casos de uso principales son iniciar sesión, recuperar contraseña, ver dashboard, explorar catálogo, ver detalle, inscribirse, ver progreso, consultar reporte, descargar PDF, editar perfil y cerrar sesión. El actor Sistema participa en validación de cupos, generación de recomendaciones y reportes. El actor Administrador se clasifica como futuro.")
    add_placeholder(doc, "Figura A1. Diagrama UML de casos de uso", "Insertar aquí el diagrama UML exportado. Debe mostrar al actor Estudiante conectado con CU-01 a CU-11, al Sistema como actor secundario y al Administrador como actor futuro fuera del alcance actual.")

    add_heading(doc, "Anexo B. Historias de usuario SCRUM", 2)
    hu_rows = [
        ["HU-01", "Como estudiante quiero iniciar sesión con correo institucional para acceder a mis cursos.", "Credenciales válidas redirigen a #inicio; inválidas muestran error; Habeas aceptado es obligatorio.", "Alta", "5 pts", "Sprint 1"],
        ["HU-02", "Como estudiante quiero recuperar mi contraseña para restablecer el acceso.", "Formulario valida correo y confirmación; Firebase envía enlace; retorna al login.", "Alta", "3 pts", "Sprint 1"],
        ["HU-03", "Como estudiante quiero ver cursos sugeridos para identificar opciones de refuerzo.", "Dashboard muestra nombre, cursos base y recomendaciones.", "Alta", "5 pts", "Sprint 2"],
        ["HU-04", "Como estudiante quiero filtrar cursos por área y modalidad para encontrar opciones relevantes.", "Los filtros actualizan el listado sin recargar la página.", "Media", "5 pts", "Sprint 2"],
        ["HU-05", "Como estudiante quiero consultar detalles de un curso antes de inscribirme.", "Detalle muestra descripción, duración, nivel y botón de inscripción.", "Media", "3 pts", "Sprint 2"],
        ["HU-06", "Como estudiante quiero inscribirme en cursos con cupos disponibles.", "Si hay cupos confirma; si no hay cupos muestra alternativas; evita duplicados.", "Alta", "8 pts", "Sprint 3"],
        ["HU-07", "Como estudiante quiero visualizar mi progreso y calificaciones para conocer mi estado académico.", "Muestra progreso, actividades, fórmula, nota final y estado.", "Alta", "8 pts", "Sprint 3"],
        ["HU-08", "Como estudiante quiero descargar un reporte PDF para conservar evidencia de mi avance.", "El PDF se genera con datos del estudiante y curso.", "Alta", "5 pts", "Sprint 4"],
        ["HU-09", "Como estudiante quiero editar mi perfil y modalidad preferida.", "Permite avatar, modalidad y contraseña con validaciones.", "Media", "5 pts", "Sprint 4"],
        ["HU-10", "Como administrador quiero gestionar cursos y cupos.", "Criterio futuro: CRUD de cursos, usuarios y cupos.", "Media", "13 pts", "Sprint futuro"],
    ]
    add_table(doc, ["ID", "Historia", "Criterios de aceptación", "Prioridad", "Estimación", "Sprint"], hu_rows, [0.6, 2.1, 2.3, 0.8, 0.7, 0.8])

    add_heading(doc, "Anexo C. Ficha técnica del software", 2)
    add_table(doc, ["Campo", "Detalle"], [
        ["Nombre", "Sistema de Apoyo Académico con Recomendación de Cursos (SARC)"],
        ["Versión documental", "1.0.0 académica"],
        ["Arquitectura", "Aplicación web modular inspirada en MVC, con vistas HTML, módulos JS y Firebase como servicio."],
        ["Frontend", "HTML5, CSS3, JavaScript ES Modules."],
        ["Backend", "No hay backend propio; Firebase Authentication y Cloud Firestore actúan como servicios administrados."],
        ["Servidor desarrollo", "Python ThreadingHTTPServer en app.py, puerto 8000."],
        ["Seguridad", "Firebase Auth, reglas Firestore por userId, Habeas Data y protección de rutas frontend."],
        ["Compatibilidad", "Navegadores modernos con soporte ES Modules."],
        ["Despliegue", "Local con iniciar_sarc.vbs y app.py en segundo plano; futuro posible en Firebase Hosting u hosting estático."],
        ["Dependencias", "SDK Firebase desde gstatic; no usa npm ni framework frontend."],
        ["Integraciones", "Firebase Authentication, Cloud Firestore; Firebase Storage futuro para avatares."],
    ], [2.0, 4.8])

    add_heading(doc, "Anexo D. Ficha técnica del hardware", 2)
    add_table(doc, ["Componente", "Requerimiento mínimo", "Requerimiento recomendado"], [
        ["Cliente", "Equipo con navegador moderno y conexión a internet.", "Equipo portátil o escritorio con Chrome/Edge actualizado."],
        ["Procesador", "Dual Core 1.8 GHz.", "Intel i3/Ryzen 3 o superior."],
        ["RAM", "4 GB.", "8 GB o superior."],
        ["Almacenamiento", "200 MB para proyecto local.", "1 GB para documentación, evidencias y respaldos."],
        ["Red", "Conexión estable a internet para Firebase.", "Banda ancha institucional estable."],
        ["Navegador", "Chrome 100+, Edge 100+, Firefox 95+.", "Chrome o Edge actualizado."],
        ["Servidor desarrollo", "Equipo local con Python 3.", "Equipo institucional o hosting estático con HTTPS."],
        ["Servidor productivo", "Hosting web estático y Firebase.", "Firebase Hosting más políticas de respaldo y monitoreo."],
    ], [1.5, 2.6, 2.6])

    add_heading(doc, "Anexo E. Cronograma de Gantt", 2)
    gantt_rows = [
        ["1", "Análisis del problema", "2026-01-15", "2026-01-31", "12 días hábiles", "Ninguna", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["2", "Levantamiento de requisitos", "2026-02-01", "2026-02-14", "10 días hábiles", "Fase 1", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["3", "Diseño de mockups", "2026-02-15", "2026-02-28", "10 días hábiles", "Fase 2", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["4", "Arquitectura y estructura del proyecto", "2026-03-01", "2026-03-08", "6 días hábiles", "Fase 3", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["5", "Desarrollo de autenticación y rutas", "2026-03-09", "2026-03-18", "8 días hábiles", "Fase 4", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["6", "Catálogo, detalle e inscripción", "2026-03-19", "2026-03-31", "9 días hábiles", "Fase 5", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["7", "Progreso, calificaciones y reportes", "2026-04-01", "2026-04-12", "8 días hábiles", "Fase 6", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["8", "Perfil, Firebase y seguridad", "2026-04-13", "2026-04-22", "8 días hábiles", "Fase 7", "Finalizado", "Alta", "Lorena Roa Rivera"],
        ["9", "Pruebas, ajustes y documentación", "2026-04-23", "2026-05-10", "12 días hábiles", "Fase 8", "En cierre", "Alta", "Lorena Roa Rivera"],
        ["10", "Sustentación y entrega final", "2026-05-11", "2026-05-20", "8 días hábiles", "Fase 9", "Pendiente", "Alta", "Lorena Roa Rivera"],
    ]
    add_table(doc, ["No.", "Fase", "Inicio", "Fin", "Duración", "Dependencia", "Estado", "Prioridad", "Responsable"], gantt_rows, [0.4, 1.4, 0.75, 0.75, 0.9, 0.9, 0.75, 0.7, 1.0])
    add_para(doc, "El cronograma organiza el proyecto en fases secuenciales, iniciando con análisis y requisitos, continuando con diseño, desarrollo modular, integración Firebase, pruebas y documentación. Las fases futuras de panel administrativo, IA avanzada e integraciones institucionales no se incluyen dentro del cronograma de entrega de la versión 1.0.0, porque exceden el alcance implementado.")

    # Metadata note
    core = doc.core_properties
    core.title = "SARC - SRS IEEE 830 ICONTEC"
    core.subject = "Documentación académica y técnica del Sistema de Apoyo Académico con Recomendación de Cursos"
    core.author = "Lorena Roa Rivera"
    core.keywords = "SARC, IEEE 830, ICONTEC, Firebase, ingeniería de software"
    return doc


def add_compact_srs(doc: Document) -> None:
    """Crea una version reducida del documento, cercana a 15 paginas."""
    add_heading(doc, "1. Introducción", 1)
    add_para(doc, "El Sistema de Apoyo Académico con Recomendación de Cursos (SARC) es una plataforma web académica orientada a estudiantes de la Universidad de Sabaneta (Unisabaneta). Su finalidad es centralizar cursos complementarios y ofrecer recomendaciones de formación según la información académica disponible del estudiante, facilitando procesos de inscripción, seguimiento de progreso y consulta de reportes.")
    add_para(doc, "El proyecto fue desarrollado como una aplicación web modular con HTML5, CSS3 y JavaScript ES Modules. Integra Firebase Authentication para autenticación por correo y contraseña, Cloud Firestore para persistencia de información académica por usuario y un servidor local Python para ejecución en desarrollo. No utiliza frameworks frontend ni backend tradicionales; su estructura se basa en plantillas HTML por vista, módulos JavaScript compartidos y estado global administrado en memoria.")
    add_para(doc, "En el contexto de transformación digital educativa, SARC representa un prototipo funcional que permite organizar la oferta de apoyo académico, orientar al estudiante mediante recomendaciones basadas en reglas y fortalecer competencias transversales como matemáticas, programación, comunicación e idiomas. La versión actual no implementa inteligencia artificial predictiva ni machine learning; el sistema de recomendación opera con datos del perfil, cursos, progreso y actividades evaluativas.")

    add_heading(doc, "2. Planteamiento del problema y justificación", 1)
    add_para(doc, "Actualmente, muchos estudiantes universitarios presentan dificultades para encontrar cursos complementarios que fortalezcan competencias clave. La oferta académica de apoyo puede estar dispersa en diferentes canales, lo que reduce su visibilidad y dificulta que el estudiante tome decisiones oportunas sobre su formación.")
    add_para(doc, "Esta situación impacta el rendimiento académico, la permanencia estudiantil y el desarrollo de competencias interdisciplinarias. En áreas como matemáticas, programación e inglés, la falta de orientación temprana puede generar bajo aprovechamiento de recursos institucionales y mayor riesgo académico.")
    add_para(doc, "SARC se justifica como una herramienta de apoyo académico porque centraliza cursos complementarios, permite consultar recomendaciones, facilita la inscripción, muestra progreso por curso y genera reportes de avance. Para Unisabaneta, el sistema aporta una base tecnológica organizada y escalable; para el estudiante, reduce la dispersión de información y mejora la experiencia de acompañamiento académico.")

    add_heading(doc, "3. Objetivos", 1)
    add_heading(doc, "3.1 Objetivo general", 2)
    add_para(doc, "Desarrollar una plataforma web académica que facilite el acceso de estudiantes universitarios a cursos complementarios mediante un sistema de recomendación personalizada y seguimiento del progreso académico, fortaleciendo sus competencias interdisciplinarias y profesionales.")
    add_heading(doc, "3.2 Objetivos específicos", 2)
    add_bullets(doc, [
        "Implementar un módulo de autenticación seguro para estudiantes mediante Firebase Authentication.",
        "Desarrollar recomendaciones académicas basadas en perfil, cursos inscritos, modalidad y progreso.",
        "Crear un catálogo de cursos filtrable por área interdisciplinaria y modalidad.",
        "Permitir inscripción a cursos con control básico de cupos y validación de duplicados.",
        "Diseñar una vista de seguimiento del progreso académico con actividades evaluativas y cálculo de nota final.",
        "Generar reportes académicos descargables en formato PDF.",
        "Gestionar perfil de usuario, modalidad preferida, avatar y cambio de contraseña.",
    ])

    add_heading(doc, "4. Alcance del sistema", 1)
    add_para(doc, "La versión actual de SARC incluye autenticación, recuperación de contraseña, dashboard académico, recomendaciones basadas en reglas, catálogo filtrable, detalle de curso, inscripción, progreso académico, reportes PDF y perfil de usuario. También contempla aceptación de Habeas Data y persistencia en Firestore por userId.")
    add_heading(doc, "4.1 Clasificación de funcionalidades", 2)
    add_table(doc, ["Funcionalidad", "Estado real", "Observación"], [
        ["Inicio de sesión y recuperación", "Implementada", "Firebase Authentication con correo y contraseña."],
        ["Dashboard y recomendaciones", "Implementada / prototipada", "Recomendaciones por reglas; no hay IA avanzada."],
        ["Catálogo, filtros, detalle e inscripción", "Implementada", "Filtros por área/modalidad y control de cupos."],
        ["Progreso y reportes PDF", "Implementada", "Cálculo ponderado de notas y PDF simple desde JavaScript."],
        ["Perfil de usuario", "Implementada", "Modalidad, avatar, contraseña, cierre de sesión y reinicio demo."],
        ["Registro separado, panel administrativo, foros, pagos, videollamadas", "Futura o pendiente", "No existe vista ni módulo implementado."],
    ], [1.8, 1.6, 3.4])
    add_heading(doc, "4.2 Exclusiones", 2)
    add_bullets(doc, [
        "No incluye módulo de pagos, facturación ni comercio electrónico.",
        "No incluye gestión docente avanzada ni carga de materiales académicos.",
        "No incluye videoconferencias, foros ni mensajería interna.",
        "No incluye panel administrativo visual ni roles docentes implementados.",
        "No implementa machine learning, chatbot conversacional ni analítica predictiva de deserción.",
    ])

    add_heading(doc, "5. Descripción general y arquitectura", 1)
    add_para(doc, "SARC funciona como una aplicación web de una sola página con navegación por hash. El archivo index.html contiene el contenedor principal, carga hojas de estilo globales y declara shared/js/app.js como punto de entrada. El módulo app.js inicializa Firebase, carga el estado, valida sesión y renderiza la vista correspondiente según rutas como #login, #inicio, #recomendaciones, #detalle/{curso}, #progreso y #perfil.")
    add_para(doc, "Aunque el proyecto no usa un framework MVC formal, puede documentarse como una arquitectura modular inspirada en MVC: el modelo corresponde al estado global state.db, defaultDatabase y Firestore; la vista corresponde a plantillas HTML y CSS; y los controladores corresponden a los módulos JavaScript que enlazan eventos, validan datos, ejecutan acciones y guardan cambios.")
    add_table(doc, ["Componente", "Responsabilidad real"], [
        ["index.html", "Shell principal, carga de CSS y módulo de entrada."],
        ["shared/js/app.js", "Inicialización, rutas hash, protección de vistas y renderizado."],
        ["shared/js/data.js", "Estado global, datos base, cálculo académico y persistencia."],
        ["shared/js/firebase-service.js", "Autenticación, lectura/escritura Firestore, recuperación y contraseña."],
        ["shared/js/courses.js", "Filtros, detalle, inscripción, cupos y refresco de dashboard."],
        ["pages/*", "Pantallas independientes: login, recuperar, inicio, recomendaciones, detalle, progreso y perfil."],
    ], [2.1, 4.7])
    add_heading(doc, "5.1 Tecnologías utilizadas", 2)
    add_para(doc, "Las tecnologías reales utilizadas son HTML5, CSS3, JavaScript ES Modules, Firebase Authentication, Cloud Firestore y Python http.server para desarrollo local. No se evidencian React, Angular, Vue, Express, Django, Flask, Bootstrap, npm ni servidor backend propio. La persistencia activa se maneja con Firestore; localStorage no aparece como mecanismo de persistencia activo en la versión revisada.")
    add_heading(doc, "5.2 Seguridad y flujo de datos", 2)
    add_para(doc, "La seguridad se apoya en Firebase Authentication, reglas de Firestore por userId, validaciones de formularios, control de rutas privadas en frontend y aceptación de tratamiento de datos personales. Las reglas firestore.rules impiden que un usuario autenticado acceda a documentos cuyo userId no coincida con request.auth.uid.")
    add_numbered(doc, [
        "El navegador carga index.html desde el servidor local o hosting web.",
        "app.js inicializa Firebase y determina la ruta actual.",
        "Las vistas cargan plantillas HTML mediante template-loader.js.",
        "El usuario interactúa con formularios, filtros, botones de inscripción o edición.",
        "El estado se modifica en state.db y luego se persiste en Firestore mediante saveDatabase().",
        "Los reportes PDF se generan en el navegador con shared/js/pdf.js.",
    ])

    add_heading(doc, "6. Documento SRS basado en IEEE 830", 1)
    add_heading(doc, "6.1 Propósito y alcance del SRS", 2)
    add_para(doc, "Este SRS define de forma resumida los requerimientos funcionales y no funcionales del SARC, sus restricciones, reglas de negocio y dependencias. Está dirigido a evaluadores académicos, desarrolladores y posibles responsables técnicos institucionales.")
    add_heading(doc, "6.2 Requerimientos funcionales principales", 2)
    add_bullets(doc, [
        "RF-01. El sistema debe autenticar estudiantes mediante correo y contraseña usando Firebase Authentication.",
        "RF-02. El sistema debe permitir recuperación de contraseña mediante el servicio de Firebase.",
        "RF-03. El sistema debe mostrar un dashboard con saludo, cursos sugeridos y recomendaciones académicas.",
        "RF-04. El sistema debe permitir explorar cursos filtrando por área interdisciplinaria y modalidad.",
        "RF-05. El sistema debe mostrar detalle del curso e inscripción con control de cupos.",
        "RF-06. El sistema debe mostrar progreso por curso inscrito, actividades evaluativas, nota final y estado académico.",
        "RF-07. El sistema debe generar reportes PDF descargables con datos de avance.",
        "RF-08. El sistema debe permitir ver y editar perfil, modalidad, avatar y contraseña.",
        "RF-09. El sistema debe cerrar sesión y redirigir al login.",
    ])
    add_heading(doc, "6.3 Requerimientos no funcionales principales", 2)
    add_bullets(doc, [
        "Seguridad: las credenciales no deben almacenarse en Firestore y los datos deben aislarse por userId.",
        "Usabilidad: la navegación debe ser clara y apoyarse en modales, toasts y botones visibles.",
        "Compatibilidad: debe ejecutarse en navegadores modernos compatibles con ES Modules y fetch.",
        "Mantenibilidad: la estructura por vistas y módulos compartidos debe conservarse para facilitar evolución.",
        "Disponibilidad: en producción dependerá de Firebase y del hosting seleccionado; en desarrollo depende de app.py.",
    ])
    add_heading(doc, "6.4 Reglas de negocio, restricciones y dependencias", 2)
    add_bullets(doc, [
        "Un estudiante no debe inscribirse dos veces en el mismo curso.",
        "Si no hay cupos, el sistema muestra alternativas configuradas en el curso.",
        "Las recomendaciones de la versión actual son basadas en reglas y rendimiento, no en machine learning.",
        "El sistema requiere servidor HTTP o hosting web; no se recomienda abrir index.html con doble clic.",
        "La autenticación, recuperación y persistencia dependen de Firebase Authentication y Cloud Firestore.",
    ])

    add_heading(doc, "7. Análisis de mockups y prototipos", 1)
    add_para(doc, "Las pantallas del sistema corresponden a vistas reales ubicadas en la carpeta pages. Login valida correo, contraseña y aceptación de Habeas Data; Recuperar permite solicitar restablecimiento; Inicio presenta bienvenida, cursos sugeridos y asistente; Recomendaciones permite filtrar e inscribirse; Detalle amplía información del curso; Progreso muestra avance y notas; Perfil administra datos básicos del estudiante.")
    add_para(doc, "El prototipo mantiene una estructura visual académica con barra superior, enlaces institucionales, tarjetas, banners verdes, botones de acción y modales de feedback. Algunas pantallas solicitadas en la documentación original, como Registro y Configuración independiente, no existen en el código actual y se clasifican como funcionalidades futuras o pendientes.")
    add_heading(doc, "7.1 Capturas requeridas para mockups", 2)
    for title, instruction in [
        ("Figura 1. Login", "Insertar captura de #login con correo, contraseña, Habeas Data y botón INGRESAR."),
        ("Figura 2. Dashboard", "Insertar captura de #inicio con bienvenida, cursos sugeridos y asistente virtual."),
        ("Figura 3. Catálogo", "Insertar captura de #recomendaciones con filtros y botones Ver detalles / Inscribirse."),
        ("Figura 4. Detalle de curso", "Insertar captura de #detalle/matematicas o de otro curso seleccionado."),
        ("Figura 5. Progreso", "Insertar captura de #progreso con barras, actividades y cálculo de nota."),
        ("Figura 6. Reporte", "Insertar captura del modal de reporte detallado o del PDF generado."),
        ("Figura 7. Perfil", "Insertar captura de #perfil con datos, avatar y acciones de cuenta."),
    ]:
        add_placeholder(doc, title, instruction)

    add_heading(doc, "8. Conclusiones", 1)
    add_para(doc, "SARC constituye una solución web académica coherente con la necesidad de centralizar cursos complementarios y orientar al estudiante en su proceso formativo. La versión actual permite demostrar un flujo completo: autenticación, dashboard, recomendaciones, catálogo, detalle, inscripción, progreso, reportes y perfil.")
    add_para(doc, "El proyecto evidencia una arquitectura modular mantenible y una integración funcional con Firebase para autenticación y datos. Su principal fortaleza académica está en diferenciar con claridad lo implementado, lo prototipado y lo pendiente, evitando presentar como inteligencia artificial avanzada lo que actualmente es una recomendación basada en reglas.")
    add_para(doc, "Como trabajo universitario de ingeniería de software, SARC ofrece una base sólida para futuras ampliaciones: panel administrativo, registro formal, integración institucional, analítica avanzada, almacenamiento de avatares en Firebase Storage y pruebas automatizadas.")

    add_heading(doc, "9. Bibliografía", 1)
    for item in [
        "IEEE. IEEE Recommended Practice for Software Requirements Specifications. IEEE Std 830-1998. New York: Institute of Electrical and Electronics Engineers, 1998.",
        "PRESSMAN, Roger S. Ingeniería del software: un enfoque práctico. 7. ed. México: McGraw-Hill, 2010.",
        "SOMMERVILLE, Ian. Ingeniería de software. 10. ed. Madrid: Pearson, 2016.",
        "FIREBASE. Firebase Documentation: Authentication and Cloud Firestore. Google, 2026. Disponible en: https://firebase.google.com/docs.",
        "COLOMBIA. Congreso de la República. Ley 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales.",
        "RICCI, Francesco; ROKACH, Lior; SHAPIRA, Bracha. Recommender Systems Handbook. 3. ed. New York: Springer, 2022.",
    ]:
        add_para(doc, item)

    add_heading(doc, "10. Anexos", 1)
    add_heading(doc, "Anexo A. Diagrama UML y casos de uso", 2)
    add_para(doc, "El actor principal del sistema es el Estudiante. El actor Sistema participa en validacion de cupos, generacion de recomendaciones y reportes. El actor Administrador se mantiene como rol futuro, debido a que no existe panel administrativo implementado en la version actual.")
    add_bullets(doc, [
        "CU-01. Iniciar sesion.",
        "CU-02. Recuperar contrasena.",
        "CU-03. Ver dashboard academico.",
        "CU-04. Explorar catalogo y filtrar cursos.",
        "CU-05. Ver detalle de curso.",
        "CU-06. Inscribirse en curso.",
        "CU-07. Ver progreso academico.",
        "CU-08. Consultar y descargar reporte.",
        "CU-09. Editar perfil.",
        "CU-10. Cerrar sesion.",
    ])
    add_placeholder(doc, "Figura A1. Diagrama UML de casos de uso", "Insertar aqui el diagrama UML exportado. Debe mostrar Estudiante como actor principal, Sistema como actor secundario y Administrador como actor futuro.")

    add_heading(doc, "Anexo B. Historias de usuario SCRUM", 2)
    add_para(doc, "Las historias se presentan en formato SCRUM academico, con criterios verificables y estimacion por puntos para sustentar la priorizacion funcional.")
    add_table(doc, ["ID", "Historia", "Criterios de aceptacion", "Prioridad", "Estimacion"], [
        ["HU-01", "Como estudiante quiero iniciar sesion para acceder a mis cursos.", "Credenciales validas redirigen a Inicio sin notificacion automatica de exito; errores muestran feedback controlado; Habeas Data es obligatorio.", "Alta", "5 pts"],
        ["HU-02", "Como estudiante quiero recuperar mi contrasena para restablecer el acceso.", "El sistema valida correo institucional y solicita recuperacion mediante Firebase Authentication.", "Alta", "3 pts"],
        ["HU-03", "Como estudiante quiero ver cursos sugeridos y recomendaciones.", "El dashboard muestra cursos base, tareas y recomendaciones generadas desde datos academicos disponibles.", "Alta", "5 pts"],
        ["HU-04", "Como estudiante quiero filtrar cursos por area y modalidad.", "Los filtros actualizan el listado sin recargar la pagina y conservan la coherencia visual del catalogo.", "Media", "3 pts"],
        ["HU-05", "Como estudiante quiero inscribirme a cursos disponibles.", "Si hay cupos, confirma inscripcion; si no hay cupos, informa alternativas; evita duplicados.", "Alta", "5 pts"],
        ["HU-06", "Como estudiante quiero ver mi progreso y descargar reportes.", "La vista muestra avance, actividades, nota final, estado academico y PDF descargable.", "Alta", "8 pts"],
        ["HU-07", "Como estudiante quiero editar mi perfil.", "Permite modalidad, avatar y cambio de contrasena con validaciones de seguridad.", "Media", "5 pts"],
        ["HU-08", "Como responsable de demostracion quiero reiniciar datos solo en el usuario demo autorizado.", "El boton Reiniciar demo solo se muestra y ejecuta para lorena.roa@unisabaneta.edu.co; otros usuarios no lo ven.", "Alta", "3 pts"],
    ], [0.55, 2.0, 2.8, 0.75, 0.85])

    add_heading(doc, "Anexo C. Ficha tecnica de hardware", 2)
    add_table(doc, ["Elemento", "Cliente minimo", "Cliente recomendado", "Servidor / hosting"], [
        ["Procesador", "Dual Core 1.8 GHz.", "Core i3/Ryzen 3 o superior.", "No requiere servidor propio; hosting estatico o Firebase Hosting."],
        ["Memoria RAM", "4 GB para navegador moderno.", "8 GB o superior para pruebas y navegacion fluida.", "Servicio administrado; recursos dependen del proveedor cloud."],
        ["Almacenamiento", "100 MB libres para cache y descargas PDF.", "500 MB libres para capturas, documentos y reportes.", "Repositorio y archivos estaticos; Firestore almacena datos en la nube."],
        ["Requisitos minimos", "Navegador compatible con ES Modules, fetch, Blob y FileReader.", "Chrome o Edge actualizado con conexion estable.", "HTTPS recomendado para despliegue y uso de Firebase."],
        ["Requisitos recomendados", "Conexion a internet activa.", "Conexion institucional estable y pantalla 1366x768 o superior.", "Firebase Authentication y Cloud Firestore configurados."],
    ], [1.1, 1.7, 1.8, 2.1])

    add_heading(doc, "Anexo D. Ficha tecnica de software", 2)
    add_table(doc, ["Categoria", "Detalle tecnico actualizado"], [
        ["Tecnologias utilizadas", "HTML5, CSS3, JavaScript ES Modules, Firebase Authentication, Cloud Firestore y Python http.server para desarrollo local."],
        ["Versiones", "Firebase SDK 10.12.5 importado dinamicamente desde gstatic; Python 3 para app.py; navegadores modernos con soporte ES Modules."],
        ["Firebase", "Autenticacion por correo/contrasena, recuperacion de contrasena, cambio de contrasena y persistencia en Firestore por userId."],
        ["HTML5 / CSS3", "Plantillas por vista en pages/ y estilos globales en shared/css, manteniendo colores institucionales azul y verde."],
        ["JavaScript", "Modulos para rutas, estado, datos, cursos, progreso, PDF, Firebase, plantillas y feedback visual."],
        ["Librerias utilizadas", "No usa frameworks frontend ni dependencias npm obligatorias; la app consume Firebase SDK desde CDN."],
        ["Compatibilidad", "Chrome, Edge, Firefox o Safari moderno con JavaScript habilitado y acceso a internet."],
        ["Navegadores", "Probado para entorno academico en navegadores Chromium; se recomienda Chrome o Edge actualizado."],
        ["Hosting", "Ejecucion local con app.py; despliegue recomendado en hosting estatico HTTPS o Firebase Hosting."],
        ["Dependencias", "Firebase configurado en shared/js/firebase-config.js; reglas en firestore.rules; no requiere backend propio."],
    ], [1.45, 5.35])

    add_heading(doc, "Anexo E. Repositorio GitHub", 2)
    add_table(doc, ["Campo", "Descripcion academica"], [
        ["Nombre del repositorio", "Proyecto_SARC"],
        ["Descripcion breve", "Repositorio del Sistema de Apoyo Academico con Recomendacion de Cursos, desarrollado como aplicacion web modular para entorno universitario."],
        ["Objetivo", "Centralizar el codigo fuente, documentos de apoyo y configuracion necesaria para ejecutar, revisar y evolucionar SARC."],
        ["Enlace oficial", "https://github.com/LorenaRoa25/Proyecto_SARC"],
        ["Contenido", "index.html, pages/, shared/, app.py, firestore.rules, README.md, FIREBASE_SETUP.md, Documentos/ y herramientas de generacion documental."],
        ["Importancia del control de versiones", "Permite trazabilidad de cambios, respaldo del codigo, colaboracion tecnica, revision academica y recuperacion ante errores."],
    ], [1.7, 5.1])

    add_heading(doc, "Anexo F. Cronograma de Gantt", 2)
    add_para(doc, "El cronograma se organiza como matriz visual por semanas. Los bloques verdes representan periodos activos de trabajo y las columnas conservan una lectura limpia para sustentacion academica.")
    add_gantt_matrix(doc)
    add_table(doc, ["Fase", "Actividad", "Inicio", "Fin", "Prioridad", "Estado"], [
        ["F1", "Recoleccion y analisis de requisitos", "02/02/2026", "27/02/2026", "Alta", "Terminado"],
        ["F2", "Diseno de arquitectura, datos y mockups", "02/03/2026", "20/03/2026", "Alta", "Terminado"],
        ["F3", "Implementacion de autenticacion, cursos, progreso, perfil y Firebase", "23/03/2026", "30/04/2026", "Alta", "Terminado"],
        ["F4", "Pruebas funcionales, ajustes visuales y correcciones", "01/05/2026", "07/05/2026", "Alta", "En cierre"],
        ["F5", "Documentacion academica, anexos y preparacion de sustentacion", "08/05/2026", "15/05/2026", "Alta", "En cierre"],
    ], [0.65, 3.0, 0.9, 0.9, 0.7, 0.8])


def build_compact_doc() -> Document:
    doc = Document()
    configure_styles(doc)
    for section in doc.sections:
        apply_icontec_section(section)
        add_page_number(section)

    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SISTEMA DE APOYO ACADÉMICO CON RECOMENDACIÓN DE CURSOS (SARC)")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Especificación de Requerimientos de Software (SRS) basada en IEEE 830\nDocumentación académica bajo Norma ICONTEC")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    doc.add_paragraph()
    doc.add_paragraph()
    for line in [
        "Lorena Roa Rivera",
        "Proyecto universitario de Ingeniería Informática",
        "Docente evaluador: ______________________________",
        "Corporación Universitaria de Sabaneta - Unisabaneta",
        "Facultad de Ingeniería",
        "Sabaneta, Antioquia",
        "2026",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.name = "Arial"
        r.font.size = Pt(12)
    doc.add_page_break()

    add_toc(doc)
    doc.add_page_break()
    add_compact_srs(doc)

    core = doc.core_properties
    core.title = "SARC - SRS IEEE 830 ICONTEC"
    core.subject = "Documento compacto de requerimientos y documentación técnica del SARC"
    core.author = "Lorena Roa Rivera"
    core.keywords = "SARC, IEEE 830, ICONTEC, Firebase, ingeniería de software"
    return doc


def main() -> None:
    doc = build_compact_doc()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
