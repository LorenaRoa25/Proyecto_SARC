# SARC - Sistema de Apoyo Academico con Recomendacion de Cursos

SARC es una aplicacion web academica creada para apoyar a estudiantes en la consulta de cursos complementarios, recomendaciones, inscripcion, seguimiento de progreso y gestion basica de perfil.

El proyecto esta construido con tecnologias web base: HTML, CSS y JavaScript modular. La autenticacion y la persistencia se conectan con Firebase Authentication y Cloud Firestore.

## Que problema resuelve

En un entorno universitario, los estudiantes pueden tener dificultades para encontrar cursos de apoyo o refuerzo segun sus necesidades academicas. SARC centraliza esa informacion en una interfaz sencilla donde el estudiante puede:

- Ver cursos sugeridos.
- Filtrar recomendaciones por area y modalidad.
- Consultar detalle de cada curso.
- Inscribirse si hay cupos disponibles.
- Revisar su progreso academico.
- Descargar un reporte en PDF.
- Editar algunos datos de perfil.

## Como esta pensado el proyecto

La aplicacion funciona como una pagina principal que cambia de vista sin recargar todo el sitio. Para eso usa rutas con hash en la URL, por ejemplo:

```text
#login
#inicio
#recomendaciones
#detalle/matematicas
#progreso
#perfil
```

El archivo `index.html` contiene la estructura general. El archivo `shared/js/app.js` decide que vista mostrar, valida si hay sesion y llama el render correspondiente.

## Tecnologias usadas

| Tecnologia | Uso dentro del proyecto |
| --- | --- |
| HTML5 | Estructura de cada vista y del contenedor principal. |
| CSS3 | Estilos globales, layout, componentes y estilos por pagina. |
| JavaScript ES Modules | Estado, rutas, eventos, renderizado y logica de negocio. |
| Firebase Authentication | Inicio de sesion, creacion demo de usuario y recuperacion de contrasena. |
| Cloud Firestore | Guardado de usuario, cursos, recomendaciones y tareas por `userId`. |
| Python | Servidor local simple para ejecutar el proyecto durante desarrollo. |

## Mapa del proyecto

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
    scripts de apoyo para documentacion
```

## Archivos clave

`shared/js/app.js`  
Inicializa la aplicacion, controla rutas, protege vistas privadas y renderiza la pantalla correspondiente.

`shared/js/data.js`  
Contiene el estado global `state`, los datos base de demostracion y las funciones para cargar o guardar informacion.

`shared/js/firebase-service.js`  
Centraliza la conexion con Firebase Authentication y Cloud Firestore. Aqui se autentica el usuario, se cargan datos y se guardan cambios.

`shared/js/navigation.js`  
Maneja la navegacion interna usando `window.location.hash`.

`shared/js/courses.js`  
Gestiona filtros, busqueda de cursos, inscripciones, control de cupos y refresco de vistas.

`shared/js/template-loader.js`  
Carga los archivos HTML de cada vista y reemplaza variables como `{{courseList}}` o `{{name}}`.

`shared/components/feedback.js`  
Muestra modales, notificaciones y mensajes para enlaces visuales del prototipo.

`pages/`  
Cada carpeta representa una pantalla. Por ejemplo, `pages/login/` tiene su HTML, CSS y JS propios.

## Flujo de datos

1. El estudiante entra a la aplicacion desde el navegador.
2. `app.js` inicializa Firebase y el estado general.
3. El login usa Firebase Authentication.
4. Cuando el usuario entra, `data.js` carga su informacion desde Firestore.
5. Las vistas trabajan con `state.db`, que es la copia en memoria de los datos.
6. Si el usuario se inscribe, edita perfil o marca tareas, se actualiza `state.db`.
7. Luego `saveDatabase()` guarda los cambios en Firestore.
8. Firestore separa los datos por `userId`.

## Base de datos en Firebase

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

Las reglas de `firestore.rules` verifican que el usuario autenticado coincida con el `userId` del documento. Esto evita que un estudiante lea o modifique informacion de otro.

## Ejecucion local

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python app.py
```

Luego abre en el navegador:

```text
http://localhost:8000/index.html
```

No se recomienda abrir `index.html` directamente con doble clic, porque la aplicacion carga plantillas HTML con `fetch` y usa modulos JavaScript.

## Configuracion de Firebase

La configuracion del SDK se encuentra en:

```text
shared/js/firebase-config.js
```

Para preparar Firebase:

1. Crear un proyecto en Firebase Console.
2. Activar Authentication con Email/Password.
3. Crear Cloud Firestore.
4. Publicar las reglas de `firestore.rules`.
5. Revisar la guia `FIREBASE_SETUP.md`.

Nota: para facilitar la demostracion, si el correo ingresado no existe, el sistema puede crear el usuario con Email/Password.

## Documentacion incluida

La carpeta `Documentos/` contiene los documentos principales del proyecto:

- Documentacion del codigo.
- Documento general del proyecto SARC.
- Informe de evaluacion.
- Minuta de licenciamiento.
- Resumen ejecutivo.

Estos documentos complementan el codigo y ayudan a sustentar la arquitectura, alcance, requisitos y funcionamiento del sistema.

## Estado actual

El proyecto ya cuenta con:

- Frontend modular por vistas.
- Autenticacion con Firebase.
- Persistencia en Firestore.
- Separacion de datos por usuario.
- Inscripcion a cursos.
- Vista de progreso.
- Generacion de PDF desde JavaScript.
- Perfil editable.
- Documentacion tecnica y funcional.

## Posibles mejoras futuras

- Separar registro e inicio de sesion en pantallas diferentes.
- Validar estrictamente el dominio institucional del correo.
- Crear un panel administrativo para cursos y usuarios.
- Guardar imagenes de perfil en Firebase Storage.
- Agregar pruebas automatizadas.
- Publicar el proyecto en Firebase Hosting.
- Mejorar el motor de recomendacion con mas criterios academicos.

## Autora

Proyecto desarrollado por Lorena Roa Rivera.
