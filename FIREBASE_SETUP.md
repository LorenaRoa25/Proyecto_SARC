# Configuracion Firebase para SARC

## 1. Crear el proyecto

1. Entra a Firebase Console.
2. Crea un proyecto nuevo o usa uno existente.
3. Agrega una app Web.
4. Copia la configuracion del SDK en `shared/js/firebase-config.js`.

## 2. Activar Authentication

1. Ve a Authentication.
2. En Sign-in method activa Email/Password.
3. No crees campos de contrasena en Firestore. Firebase Authentication administra las credenciales.

## 3. Crear Firestore

1. Ve a Firestore Database.
2. Crea la base de datos.
3. Publica las reglas de `firestore.rules`.

## 4. Colecciones usadas

- `usuarios`: documento por usuario autenticado. El id del documento es el `uid`.
- `cursos`: documentos globales filtrados por `userId`. El id queda como `{uid}_{courseId}`, por ejemplo `abc123_algebra-lineal`.
- `recomendaciones`: documentos globales filtrados por `userId`. El id queda como `{uid}_{courseId}`.
- `tareasAsistente`: documentos globales filtrados por `userId`. El id queda como `{uid}_{taskId}`.

No se crea una coleccion por usuario. Cada documento guarda `userId`, lo que permite multiples usuarios con datos distintos y consultas filtradas.

Si ya existian documentos como `cursos/algebra-lineal`, esos documentos son datos antiguos globales. La app multiusuario no los actualiza para evitar que un usuario sobrescriba la informacion de otro. Despues de iniciar sesion, revisa en Firestore documentos con id compuesto, por ejemplo `UID_algebra-lineal`, y confirma que tengan el campo `userId`.

## 5. Primer ingreso

Al ingresar con correo y contrasena, Firebase autentica al usuario. Si el usuario no existe, se crea con Email/Password y se siembran datos iniciales en Firestore para ese `uid`.
