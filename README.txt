SARC - Sistema de Apoyo Academico con Recomendacion de Cursos

Proyecto web local para Visual Studio Code construido con HTML5, CSS3 y JavaScript puro.
La persistencia usa Firebase Authentication y Cloud Firestore.

Como ejecutar:
1. Abrir una terminal en la carpeta del proyecto.
2. Ejecutar: python app.py
3. Entrar a: http://localhost:8000/index.html

Nota:
Se recomienda usar el servidor local porque la aplicacion carga plantillas HTML con fetch,
modulos ES y servicios externos de Firebase.

Configuracion Firebase:
- shared/js/firebase-config.js contiene la configuracion del proyecto Firebase.
- Authentication debe tener activo el proveedor Email/Password.
- Firestore debe publicar las reglas incluidas en firestore.rules.
- FIREBASE_SETUP.md contiene la guia de configuracion y estructura de colecciones.

Estructura principal:
- index.html: shell general de la aplicacion y enlaces CSS/JS.
- app.py: servidor HTTP local para desarrollo.
- firestore.rules: reglas de seguridad por userId.
- FIREBASE_SETUP.md: guia de configuracion Firebase.
- shared/css: estilos base, layout y componentes reutilizables.
- shared/js: arranque, estado, Firebase, navegacion, cursos, PDF, sonido y plantillas.
- shared/components: componentes globales de feedback.
- pages: una carpeta por vista con HTML, CSS y JavaScript independientes.
- tools: scripts para generar documentos tecnicos y reportes.

Caracteristicas:
- Login y recuperacion de contrasena con Firebase Authentication.
- Si el correo no existe en Firebase, el login crea el usuario para facilitar la demo.
- Datos separados por usuario mediante userId en Firestore.
- Colecciones globales: usuarios, cursos, recomendaciones y tareasAsistente.
- Dashboard academico con navegacion por vistas.
- Cursos sugeridos con filtros.
- Inscripcion de cursos.
- Mi progreso con reporte PDF generado desde JavaScript.
- Perfil editable con cambio de foto, modalidad y contrasena.
- La demo reinicia la sesion al cargar para empezar desde login.
