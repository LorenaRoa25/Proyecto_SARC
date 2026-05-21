# SARC - Sistema de Apoyo Academico con Recomendacion de Cursos

SARC es una aplicacion web academica desarrollada para apoyar a estudiantes universitarios en la consulta de cursos complementarios, recomendaciones academicas, inscripcion a cursos, seguimiento de progreso, gestion basica de perfil y generacion de reportes PDF.

El sistema funciona como un frontend web conectado directamente con Firebase Authentication y Cloud Firestore. No utiliza Node.js obligatorio, Express, base de datos local ni backend de negocio. El archivo `app.py` se usa solo para servir archivos estaticos en `localhost` durante la ejecucion local.

## Objetivo Academico

Centralizar en una interfaz sencilla la informacion de cursos de apoyo academico, permitiendo que el estudiante consulte recomendaciones basadas en reglas, revise su avance, gestione su perfil y descargue reportes de progreso para apoyar su proceso de aprendizaje.

## Tecnologias Utilizadas

| Tecnologia | Uso dentro del proyecto |
| --- | --- |
| HTML5 | Estructura principal del sistema y plantillas de cada vista. |
| CSS3 | Estilos globales, layout, componentes visuales y adaptacion por pantalla. |
| JavaScript ES Modules | Navegacion, estado global, validaciones, recomendaciones, progreso, perfil y reportes. |
| Firebase Authentication | Inicio de sesion, recuperacion de contrasena y gestion de credenciales. |
| Cloud Firestore | Persistencia de usuarios, cursos, recomendaciones, tareas y aceptacion de Habeas Data. |
| Python local server (`app.py`) | Servidor local de archivos estaticos para ejecutar SARC en Windows. |

## Requisitos Minimos

- Windows 10 o superior.
- Python 3 instalado y agregado al PATH.
- Navegador moderno: Chrome, Edge, Firefox o Safari.
- Conexion a internet para Firebase Authentication y Cloud Firestore.
- Carpeta completa del proyecto SARC.

## Ejecucion Local En Windows

1. Abrir la carpeta principal del proyecto `Proyecto_SARC`.
2. Hacer doble clic en el archivo `iniciar_sarc.bat`.
3. Esperar a que la consola valide el entorno e inicie el servidor local.
4. El navegador se abrira automaticamente en:

```text
http://localhost:8000/
```

5. Para cerrar el sistema, presionar `Ctrl+C` en la consola o cerrar la ventana del servidor.

No se recomienda abrir `index.html` directamente con doble clic, porque la aplicacion usa JavaScript ES Modules y carga plantillas HTML mediante `fetch`.

## Credenciales Demo

Usuario demo:

```text
lorena.roa.196@unisabaneta.edu.co
```

Contrasena demo:

```text
Lorena25!
```

El usuario demo se utiliza para pruebas y sustentacion academica. Esta cuenta tiene funciones especiales de demostracion, como el boton `Reiniciar demo`, que solo aparece para la cuenta demo autorizada. Los demas usuarios registrados no deben visualizar ni ejecutar esa funcionalidad.

## Estructura Del Proyecto

```text
Proyecto_SARC/
  index.html
  app.py
  iniciar_sarc.bat
  README.md
  FIREBASE_SETUP.md
  firestore.rules

  pages/
    login/
    recuperar/
    inicio/
    recomendaciones/
    detalle/
    progreso/
    perfil/

  shared/
    css/
    js/
    components/

  Documentos/
    Manual_Tecnico_SARC.docx
    Manual_Usuario_SARC.docx
    SARC_SRS_IEEE830_ICONTEC.docx
    Informe_evaluacion_SARC.docx
    Minuta Licenciamiento-Lorena Roa.docx
    Resumen_Ejecutivo_Minuta_SARC.docx
    Guia_Rapida_Uso_SARC.docx

  tools/
    scripts de apoyo documental y capturas
```

## Carpetas Principales

`pages/` contiene las vistas funcionales del sistema, separadas por modulo: login, recuperacion, inicio, recomendaciones, detalle, progreso y perfil.

`shared/` agrupa codigo reutilizable: estilos globales, componentes, navegacion, estado, conexion Firebase, cursos, reportes PDF y perfiles especiales.

`Documentos/` contiene los entregables academicos del proyecto, incluyendo el Manual Tecnico, Manual de Usuario y documento SRS IEEE830 ICONTEC.

`tools/` contiene scripts auxiliares para documentacion, capturas y generacion de archivos academicos. No es necesario ejecutar esta carpeta para usar el sistema.

## Archivos Clave

`index.html` define la estructura principal de la aplicacion.

`app.py` sirve los archivos estaticos en `localhost` para que el navegador cargue correctamente modulos JavaScript, plantillas y Firebase.

`iniciar_sarc.bat` automatiza el despliegue local en Windows: valida archivos esenciales, detecta Python, ejecuta `app.py` y abre el navegador.

`shared/js/app.js` inicializa el sistema, controla rutas y protege vistas privadas.

`shared/js/data.js` centraliza el estado global, datos base, recomendaciones y persistencia.

`shared/js/firebase-service.js` concentra la conexion con Firebase Authentication y Cloud Firestore.

`shared/js/user-profiles.js` centraliza reglas de perfiles especiales, incluyendo la validacion del usuario demo autorizado.

## Funcionamiento General

1. El usuario abre SARC desde `iniciar_sarc.bat`.
2. `app.py` inicia el servidor local en `http://localhost:8000/`.
3. El navegador carga `index.html` y los modulos JavaScript.
4. El estudiante inicia sesion con Firebase Authentication.
5. Los datos academicos se cargan desde Cloud Firestore.
6. Las vistas trabajan con el estado en memoria del frontend.
7. Los cambios de perfil, cursos, progreso y tareas se guardan en Firestore.
8. Los reportes PDF se generan desde JavaScript en el navegador.

## Firebase

La configuracion del SDK se encuentra en:

```text
shared/js/firebase-config.js
```

El proyecto usa estas colecciones principales:

- `usuarios`
- `cursos`
- `recomendaciones`
- `tareasAsistente`
- `habeasData`

Las reglas de `firestore.rules` separan la informacion por `userId`, evitando que un usuario lea o modifique datos de otro.

## Alcance Actual

El sistema implementa:

- Inicio de sesion institucional.
- Recuperacion y cambio de contrasena mediante Firebase.
- Aceptacion de Habeas Data.
- Recomendaciones academicas basadas en reglas.
- Catalogo de cursos con filtros.
- Inscripcion a cursos.
- Seguimiento de progreso academico.
- Reportes PDF.
- Perfil de estudiante editable.
- Perfil demo con reinicio controlado.
- Despliegue local portable mediante `.bat`.

No implementa panel administrativo funcional, backend propio, Express, base de datos local, chatbot conversacional ni inteligencia artificial predictiva.

## Posibles Errores Comunes

| Situacion | Causa probable | Solucion |
| --- | --- | --- |
| No se encontro Python | Python no esta instalado o no esta agregado al PATH. | Instalar Python 3 desde python.org y marcar "Add python.exe to PATH". |
| No se encontro `index.html` | El `.bat` no esta en la raiz del proyecto. | Ejecutar `iniciar_sarc.bat` desde la carpeta principal de SARC. |
| No se encontro `firebase-config.js` | Falta la configuracion Firebase. | Verificar que exista `shared/js/firebase-config.js`. |
| Puerto 8000 ocupado | Ya existe otra instancia local ejecutandose. | Cerrar la consola anterior o detener el proceso que usa el puerto 8000. |
| Login o Firestore no responden | No hay internet o Firebase no esta disponible. | Revisar conexion, credenciales Firebase y reglas de Firestore. |

## Autora

Proyecto desarrollado por Lorena Roa Rivera.
