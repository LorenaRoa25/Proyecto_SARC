# SARC - Sistema de Apoyo Academico con Recomendacion de Cursos

SARC es una aplicacion web academica desarrollada para apoyar a estudiantes universitarios en la consulta de cursos complementarios, recomendaciones academicas, inscripcion a cursos, seguimiento de progreso, gestion basica de perfil y generacion de reportes PDF.

El sistema funciona como un frontend web conectado directamente con Firebase Authentication y Firebase Firestore. No utiliza Node.js obligatorio, Express, base de datos local ni backend de negocio. El archivo `app.py` se usa solo para servir archivos estaticos en `localhost` durante la ejecucion local.

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

## Instalacion En Windows

La instalacion se realiza con el archivo `instalar_proyecto_sarc.bat`. Este archivo debe ejecutarse como administrador porque copia el proyecto en `C:\Program Files\Proyecto_SARC`, configura variables de entorno y crea el acceso directo del escritorio.

Pasos:

1. Colocar `instalar_proyecto_sarc.bat` y `Proyecto_SARC.zip` en la misma carpeta.
2. Hacer clic derecho sobre `instalar_proyecto_sarc.bat`.
3. Seleccionar `Ejecutar como administrador`.
4. Esperar a que el instalador copie los archivos y cree el acceso directo `Proyecto SARC`.
5. Abrir la aplicacion desde el acceso directo del escritorio.

El acceso directo no abre `index.html` directamente. Apunta a `iniciar_sarc.vbs`, que inicia `app.py` en segundo plano y abre el navegador en `http://localhost:8000/` sin mostrar una terminal.

## Ejecucion Local En Windows

1. Abrir la carpeta principal del proyecto `Proyecto_SARC`.
2. Hacer doble clic en el archivo `iniciar_sarc.vbs`.
3. Esperar a que el navegador abra automaticamente el sistema.
4. El navegador se abrira automaticamente en:

```text
http://localhost:8000/
```

5. Para cerrar el sistema, cerrar el navegador y detener el proceso `pythonw.exe` desde el Administrador de tareas si necesita apagar el servidor local oculto.

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
  iniciar_sarc.vbs
  instalar_proyecto_sarc.bat
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
    Guia_Rapida_Uso_SARC.docx

  tools/
    scripts de apoyo documental y capturas
```

## Carpetas Principales

`pages/` contiene las vistas funcionales del sistema, separadas por modulo: login, recuperacion, inicio, recomendaciones, detalle, progreso y perfil.

`shared/` agrupa codigo reutilizable: estilos globales, componentes, navegacion, estado, conexion Firebase, cursos, reportes PDF y perfiles especiales.

`Documentos/` contiene los entregables academicos vigentes del proyecto: Manual Tecnico, Manual de Usuario, Guia Rapida de Uso y documento SRS IEEE830 ICONTEC.

`tools/` contiene scripts auxiliares para documentacion, capturas y generacion de archivos academicos. No es necesario ejecutar esta carpeta para usar el sistema.

## Archivos Clave

`index.html` define la estructura principal de la aplicacion.

`app.py` sirve los archivos estaticos en `localhost` para que el navegador cargue correctamente modulos JavaScript, plantillas y Firebase.

`iniciar_sarc.vbs` automatiza el despliegue local en Windows sin mostrar una terminal: valida archivos esenciales, detecta Python, ejecuta `app.py` en segundo plano y abre el navegador.

`instalar_proyecto_sarc.bat` instala SARC en `C:\Program Files\Proyecto_SARC`, extrae `Proyecto_SARC.zip`, configura `SARC_HOME`, agrega la ruta al PATH y crea el acceso directo `Proyecto SARC` en el escritorio.

`shared/js/app.js` inicializa el sistema, controla rutas y protege vistas privadas.

`shared/js/data.js` centraliza el estado global, datos base, recomendaciones y persistencia.

`shared/js/firebase-service.js` concentra la conexion con Firebase Authentication y Cloud Firestore.

`shared/js/user-profiles.js` centraliza reglas de perfiles especiales, incluyendo la validacion del usuario demo autorizado.

## Funcionamiento General

1. El usuario abre SARC desde el acceso directo `Proyecto SARC` o desde `iniciar_sarc.vbs`.
2. `iniciar_sarc.vbs` detecta Python y ejecuta `app.py` en segundo plano.
3. `app.py` inicia el servidor local en `http://localhost:8000/`.
4. El navegador carga `index.html` y los modulos JavaScript.
5. El estudiante inicia sesion con Firebase Authentication.
6. Los datos academicos se cargan desde Cloud Firestore.
7. Las vistas trabajan con el estado en memoria del frontend.
8. Los cambios de perfil, cursos, progreso y tareas se guardan en Firestore.
9. Los reportes PDF se generan desde JavaScript en el navegador.

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
- Instalador Windows mediante `instalar_proyecto_sarc.bat`.
- Despliegue local portable mediante lanzador silencioso `.vbs`.

No implementa panel administrativo funcional, backend propio, Express, base de datos local, chatbot conversacional ni inteligencia artificial predictiva.

## Posibles Errores Comunes

| Situacion | Causa probable | Solucion |
| --- | --- | --- |
| El instalador no avanza | No se ejecuto como administrador o falta `Proyecto_SARC.zip`. | Ejecutar `instalar_proyecto_sarc.bat` como administrador y verificar que el ZIP este junto al BAT. |
| No se encontro Python | Python no esta instalado o no esta agregado al PATH. | Instalar Python 3 desde python.org y marcar "Add python.exe to PATH". |
| No se encontro `index.html` | El lanzador no esta en la raiz del proyecto. | Ejecutar `iniciar_sarc.vbs` desde la carpeta principal de SARC. |
| No se encontro `firebase-config.js` | Falta la configuracion Firebase. | Verificar que exista `shared/js/firebase-config.js`. |
| Puerto 8000 ocupado | Ya existe otra instancia local ejecutandose. | Cerrar la instancia anterior o detener `pythonw.exe` desde el Administrador de tareas. |
| La app queda en pantalla de carga | Se abrio `index.html` directamente como archivo. | Abrir SARC desde `Proyecto SARC` o desde `iniciar_sarc.vbs`. |
| Login o Firestore no responden | No hay internet o Firebase no esta disponible. | Revisar conexion, credenciales Firebase y reglas de Firestore. |

## Autora

Proyecto desarrollado por Lorena Roa Rivera.
