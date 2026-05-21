@echo off
REM ================================================================
REM  SARC - Despliegue local portable en Windows
REM  Sistema de Apoyo Academico con Recomendacion de Cursos
REM ================================================================

setlocal
cd /d "%~dp0"

echo.
echo ================================================================
echo  SARC - Sistema de Apoyo Academico con Recomendacion de Cursos
echo ================================================================
echo Ruta del proyecto: %CD%
echo.

IF NOT EXIST "index.html" (
  echo ERROR: No se encontro index.html en la carpeta del proyecto.
  echo Verifique que este archivo .bat este ubicado en la raiz del proyecto SARC.
  pause
  exit /b 1
)

IF NOT EXIST "app.py" (
  echo ERROR: No se encontro app.py. No es posible iniciar el servidor local.
  pause
  exit /b 1
)

IF NOT EXIST "shared\js\app.js" (
  echo ERROR: No se encontro shared\js\app.js.
  echo La estructura del proyecto esta incompleta.
  pause
  exit /b 1
)

IF NOT EXIST "shared\js\firebase-config.js" (
  echo ERROR: No se encontro shared\js\firebase-config.js.
  echo Sin este archivo no se puede conectar con Firebase.
  pause
  exit /b 1
)

set "PYTHON_CMD="

python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
  set "PYTHON_CMD=python"
)

IF "%PYTHON_CMD%"=="" (
  py -3 --version >nul 2>&1
  IF %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
  )
)

IF "%PYTHON_CMD%"=="" (
  echo ERROR: No se encontro Python instalado en este computador.
  echo.
  echo Para ejecutar SARC localmente instale Python 3 desde:
  echo https://www.python.org/downloads/
  echo.
  echo Durante la instalacion marque la opcion "Add python.exe to PATH".
  echo Luego cierre esta ventana y vuelva a ejecutar iniciar_sarc.bat.
  pause
  exit /b 1
)

echo Verificacion del entorno completada.
echo Python detectado mediante: %PYTHON_CMD%
echo.
echo Iniciando servidor local...
echo URL del sistema: http://localhost:8000/
echo.
echo El navegador se abrira automaticamente.
echo Para detener el sistema, presione Ctrl+C o cierre esta ventana.
echo.

%PYTHON_CMD% app.py

echo.
echo El servidor local de SARC se ha detenido.
pause
endlocal
