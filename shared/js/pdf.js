/**
 * Generación simple de reportes PDF sin dependencias externas.
 */

import { state } from "./data.js";

/**
 * Descarga el reporte de progreso de un curso.
 * @param {object} course
 */
export function downloadReport(course) {
  const today = new Date().toLocaleDateString("es-CO", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  });

  const lines = [
    "Reporte de progreso académico",
    "",
    `Estudiante: ${state.db.user.name}`,
    `Fecha: ${today}`,
    `Curso: ${course.name}`,
    `Modalidad: ${course.modality}`,
    `Progreso: ${course.progress}%`,
    `Lecciones completadas: ${course.lessons}`,
    `Tiempo invertido: ${course.timeSpent}`,
    `Promedio de evaluaciones: ${course.average}`,
    `Recomendación del sistema: ${course.recommendation}`,
    `Estado: ${course.status}`
  ];

  const pdfBytes = buildSimplePdf(lines);
  const blob = new Blob([pdfBytes], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = `reporte-${sanitizeFilename(course.name)}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/**
 * Construye bytes mínimos de un PDF con texto.
 * @param {string[]} lines
 * @returns {Uint8Array}
 */
function buildSimplePdf(lines) {
  const streamChunks = [];
  const boxX = 66;
  const boxY = 92;
  const boxWidth = 480;
  const boxHeight = 630;
  let y = 660;

  streamChunks.push(encodeAscii("q 0.95 0.95 0.95 rg 0 0 595 842 re f Q\n"));
  streamChunks.push(encodeAscii(`q 1 1 1 rg ${boxX} ${boxY} ${boxWidth} ${boxHeight} re f Q\n`));
  streamChunks.push(encodeAscii(`q 0 0 0 RG 0.7 w ${boxX} ${boxY} ${boxWidth} ${boxHeight} re S Q\n`));
  streamChunks.push(drawCenteredText("Reporte de progreso academico", 297, 750, 18));

  lines.slice(2).forEach((line, index) => {
    streamChunks.push(drawTextLine(line, 128, y, 16, index < 2));
    y -= 42;
  });

  const contentStream = concatBytes(streamChunks);
  const objects = [
    encodeAscii("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"),
    encodeAscii("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"),
    encodeAscii("3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >> endobj\n"),
    encodeAscii("4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >> endobj\n"),
    encodeAscii("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >> endobj\n"),
    concatBytes([
      encodeAscii(`6 0 obj << /Length ${contentStream.length} >> stream\n`),
      contentStream,
      encodeAscii("\nendstream endobj\n")
    ])
  ];

  const parts = [encodeAscii("%PDF-1.4\n")];
  const offsets = [0];

  objects.forEach((objectBytes) => {
    offsets.push(totalLength(parts));
    parts.push(objectBytes);
  });

  const xrefPos = totalLength(parts);
  parts.push(encodeAscii(`xref\n0 ${objects.length + 1}\n`));
  parts.push(encodeAscii("0000000000 65535 f \n"));
  offsets.slice(1).forEach((offset) => {
    parts.push(encodeAscii(`${String(offset).padStart(10, "0")} 00000 n \n`));
  });
  parts.push(encodeAscii(`trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefPos}\n%%EOF`));

  return concatBytes(parts);
}

/**
 * Dibuja una línea de texto dentro del PDF.
 * @param {string} text
 * @param {number} x
 * @param {number} y
 * @param {number} size
 * @param {boolean} bold
 * @returns {Uint8Array}
 */
function drawTextLine(text, x, y, size, bold = false) {
  return concatBytes([
    encodeAscii("BT "),
    encodeAscii(`/${bold ? "F1" : "F2"} ${size} Tf `),
    encodeAscii(`${x} ${y} Td (`),
    encodePdfString(text),
    encodeAscii(") Tj ET\n")
  ]);
}

/**
 * Dibuja texto centrado aproximando el ancho.
 * @param {string} text
 * @param {number} centerX
 * @param {number} y
 * @param {number} size
 * @returns {Uint8Array}
 */
function drawCenteredText(text, centerX, y, size) {
  const width = text.length * size * 0.5;
  const x = Math.max(110, Math.round(centerX - width / 2));
  return drawTextLine(text, x, y, size, false);
}

/**
 * Codifica texto ASCII para el PDF.
 * @param {string} text
 * @returns {Uint8Array}
 */
function encodeAscii(text) {
  return new TextEncoder().encode(text);
}

/**
 * Escapa texto para objetos de texto PDF.
 * @param {string} text
 * @returns {Uint8Array}
 */
function encodePdfString(text) {
  const bytes = [];
  const source = String(text);

  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    const code = source.charCodeAt(index);

    if (char === "\\" || char === "(" || char === ")") {
      bytes.push(92, code);
      continue;
    }

    bytes.push(mapWinAnsiByte(code));
  }

  return Uint8Array.from(bytes);
}

/**
 * Convierte caracteres latinos comunes a WinAnsi.
 * @param {number} code
 * @returns {number}
 */
function mapWinAnsiByte(code) {
  const map = {
    193: 193,
    201: 201,
    205: 205,
    211: 211,
    218: 218,
    225: 225,
    233: 233,
    237: 237,
    243: 243,
    250: 250,
    209: 209,
    241: 241,
    220: 220,
    252: 252,
    37: 37
  };

  if (map[code]) return map[code];
  if (code >= 32 && code <= 126) return code;
  if (code >= 160 && code <= 255) return code;
  if (code === 8211) return 150;
  return 32;
}

/**
 * Une varios arreglos de bytes.
 * @param {Uint8Array[]} chunks
 * @returns {Uint8Array}
 */
function concatBytes(chunks) {
  const total = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const result = new Uint8Array(total);
  let offset = 0;

  chunks.forEach((chunk) => {
    result.set(chunk, offset);
    offset += chunk.length;
  });

  return result;
}

/**
 * Calcula el largo total de chunks binarios.
 * @param {Uint8Array[]} chunks
 * @returns {number}
 */
function totalLength(chunks) {
  return chunks.reduce((sum, chunk) => sum + chunk.length, 0);
}

/**
 * Normaliza un nombre de curso para usarlo como archivo.
 * @param {string} name
 * @returns {string}
 */
function sanitizeFilename(name) {
  return name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}
