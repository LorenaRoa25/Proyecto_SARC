# SARC - Sistema de Apoyo Académico con Recomendación de Cursos

SARC es una aplicación web académica creada para apoyar a estudiantes en la consulta de cursos complementarios, recomendaciones, inscripción, seguimiento de progreso y gestión básica de perfil.

El proyecto está construido con tecnologías web base: HTML, CSS y JavaScript modular. La autenticación y la persistencia se conectan con Firebase Authentication y Cloud Firestore.

## Qué Problema Resuelve

En un entorno universitario, los estudiantes pueden tener dificultades para encontrar cursos de apoyo o refuerzo según sus necesidades académicas. SARC centraliza esa información en una interfaz sencilla donde el estudiante puede:

- Ver cursos sugeridos.
- Filtrar recomendaciones por área y modalidad.
- Consultar el detalle de cada curso.
- Inscribirse si hay cupos disponibles.
- Revisar su progreso académico.
- Descargar un reporte en PDF.
- Editar algunos datos de perfil.

## Cómo Está Pensado El Proyecto

La aplicación funciona como una página principal que cambia de vista sin recargar todo el sitio. Para eso usa rutas con hash en la URL, por ejemplo:

```text
#login
#inicio
#recomendaciones
#detalle/matematicas
#progreso
#perfil
```

El archivo `index.html` contiene la estructura general. El archivo `shared/js/app.js` decide qué vista mostrar, valida si hay sesión y llama el render correspondiente.

## Tecnologías Usadas

| Tecnología | Uso dentro del proyecto |
| --- | --- |
| HTML5 | Estructura de cada vista y del contenedor principal. |
| CSS3 | Estilos globales, layout, componentes y estilos por página. |
| JavaScript ES Modules | Estado, rutas, eventos, renderizado y lógica de negocio. |
| Firebase Authentication | Inicio de sesión, creación demo de usuario y recuperación de contraseña. |
| Cloud Firestore | Guardado de usuario, cursos, recomendaciones y tareas por `userId`. |
| Python | Servidor local simple para ejecutar el proyecto durante desarrollo. |

## Mapa Del Proyecto

```text
Proyecto_SARC_1/
  index.html
  app.py
  README.md
  FIREBASE_SETUP.md
  firestore.rules

  shared/
    css/
      base.css
      layout.css
      components.css
    js/
      app.js
      data.js
      firebase-config.js
      firebase-service.js
      navigation.js
      courses.js
      template-loader.js
      pdf.js
      sound.js
    components/
      feedback.js

  pages/
    login/
    recuperar/
    inicio/
    recomendaciones/
    detalle/
    progreso/
    perfil/

  Documentos/
    DOCUMENTACION_CODIGO_SARC.docx
    Documento proyecto SARC - Lorena Roa Rivera.docx
    Informe_evaluacion_SARC.docx
    Minuta Licenciamiento-Lorena Roa.docx
    Resumen_Ejecutivo_SARC.docx

  tools/
    scripts de apoyo para documentación
```

## Archivos Clave

`shared/js/app.js`  
Inicializa la aplicación, controla rutas, protege vistas privadas y renderiza la pantalla correspondiente.

`shared/js/data.js`  
Contiene el estado global `state`, los datos base de demostración y las funciones para cargar o guardar información.

`shared/js/firebase-service.js`  
Centraliza la conexión con Firebase Authentication y Cloud Firestore. Aquí se autentica el usuario, se cargan datos y se guardan cambios.

`shared/js/navigation.js`  
Maneja la navegación interna usando `window.location.hash`.

`shared/js/courses.js`  
Gestiona filtros, búsqueda de cursos, inscripciones, control de cupos y refresco de vistas.

`shared/js/template-loader.js`  
Carga los archivos HTML de cada vista y reemplaza variables como `{{courseList}}` o `{{name}}`.

`shared/components/feedback.js`  
Muestra modales, notificaciones y mensajes para enlaces visuales del prototipo.

`pages/`  
Cada carpeta representa una pantalla. Por ejemplo, `pages/login/` tiene su HTML, CSS y JS propios.

## Flujo De Datos

1. El estudiante entra a la aplicación desde el navegador.
2. `app.js` inicializa Firebase y el estado general.
3. El login usa Firebase Authentication.
4. Cuando el usuario entra, `data.js` carga su información desde Firestore.
5. Las vistas trabajan con `state.db`, que es la copia en memoria de los datos.
6. Si el usuario se inscribe, edita perfil o marca tareas, se actualiza `state.db`.
7. Luego `saveDatabase()` guarda los cambios en Firestore.
8. Firestore separa los datos por `userId`.

## Base De Datos En Firebase

El proyecto usa estas colecciones principales:

- `usuarios`
- `cursos`
- `recomendaciones`
- `tareasAsistente`

Ejemplos de documentos:

```text
usuarios/{uid}
cursos/{uid}_{courseId}
recomendaciones/{uid}_{courseId}
tareasAsistente/{uid}_{taskId}
```

Las reglas de `firestore.rules` verifican que el usuario autenticado coincida con el `userId` del documento. Esto evita que un estudiante lea o modifique información de otro.

## Ejecución Local

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python app.py
```

Luego abre en el navegador:

```text
http://localhost:8000/index.html
```

No se recomienda abrir `index.html` directamente con doble clic, porque la aplicación carga plantillas HTML con `fetch` y usa módulos JavaScript.

## Configuración De Firebase

La configuración del SDK se encuentra en:

```text
shared/js/firebase-config.js
```

Para preparar Firebase:

1. Crear un proyecto en Firebase Console.
2. Activar Authentication con Email/Password.
3. Crear Cloud Firestore.
4. Publicar las reglas de `firestore.rules`.
5. Revisar la guía `FIREBASE_SETUP.md`.

Nota: para facilitar la demostración, si el correo ingresado no existe, el sistema puede crear el usuario con Email/Password.

## Documentación Incluida

La carpeta `Documentos/` contiene los documentos principales del proyecto:

- Documentación del código.
- Documento general del proyecto SARC.
- Informe de evaluación.
- Minuta de licenciamiento.
- Resumen ejecutivo.

Estos documentos complementan el código y ayudan a sustentar la arquitectura, alcance, requisitos y funcionamiento del sistema.

## Estado Actual

El proyecto ya cuenta con:

- Frontend modular por vistas.
- Autenticación con Firebase.
- Persistencia en Firestore.
- Separación de datos por usuario.
- Inscripción a cursos.
- Vista de progreso.
- Generación de PDF desde JavaScript.
- Perfil editable.
- Documentación técnica y funcional.

## Posibles Mejoras Futuras

- Separar registro e inicio de sesión en pantallas diferentes.
- Validar estrictamente el dominio institucional del correo.
- Crear un panel administrativo para cursos y usuarios.
- Guardar imágenes de perfil en Firebase Storage.
- Agregar pruebas automatizadas.
- Publicar el proyecto en Firebase Hosting.
- Mejorar el motor de recomendación con más criterios académicos.

## Actualizar GitHub Después De Hacer Cambios

Los cambios que haces en tu computador no se suben automáticamente a GitHub. Cada vez que quieras actualizar el repositorio, usa:

```bash
git status
git add .
git commit -m "Describe el cambio realizado"
git push
```

Ejemplo:

```bash
git add .
git commit -m "Actualiza documentación y corrige tildes"
git push
```

Después de `git push`, entra al repositorio en GitHub y recarga la página.

## Autora

Proyecto desarrollado por Lorena Roa Rivera.
