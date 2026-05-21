@echo off
REM ============================================================================
REM  Instalador automatico para Proyecto SARC en Windows
REM  Este archivo debe ejecutarse como administrador.
REM  Usa comandos nativos de CMD y PowerShell solo para extraer ZIP y crear .LNK.
REM ============================================================================

REM Activa el modo local para que las variables no contaminen la consola externa.
setlocal EnableExtensions EnableDelayedExpansion

REM Limpia la pantalla para mostrar un inicio ordenado de la instalacion.
cls

REM Muestra el encabezado principal del instalador.
echo ============================================================
echo  INSTALADOR AUTOMATICO - PROYECTO SARC
echo ============================================================
echo.

REM Define la ruta final obligatoria donde se instalara el proyecto.
set "INSTALL_DIR=C:\Program Files\Proyecto_SARC"

REM Define el nombre del acceso directo que se creara en el escritorio.
set "SHORTCUT_NAME=Proyecto SARC"

REM Define una variable para guardar la ubicacion real de este archivo BAT.
set "SCRIPT_DIR=%~dp0"

REM Define una variable con el nombre esperado del ZIP principal.
set "ZIP_NAME=Proyecto_SARC.zip"

REM Define una variable vacia para guardar la ruta detectada del ZIP.
set "RUTA_ORIGEN="

REM Define una variable temporal donde se extraera el ZIP antes de copiarlo.
set "TEMP_EXTRACT=%TEMP%\Proyecto_SARC_extract"

REM Define una variable para la carpeta real desde donde se copiaran los archivos.
set "COPY_SOURCE="

REM Define una variable para el archivo principal que abrira el acceso directo.
set "TARGET_APP="

REM Define una variable para el icono personalizado si existe dentro del proyecto.
set "ICON_FILE="

REM Define una variable vacia para detectar el escritorio real del usuario actual.
set "DESKTOP_DIR="

REM Define una variable vacia para la ruta completa del acceso directo.
set "SHORTCUT_PATH="

REM Define una variable para guardar el PATH del sistema leido desde el registro.
set "CURRENT_SYSTEM_PATH="

REM Verifica si el script se ejecuto con permisos de administrador.
net session >nul 2>&1

REM Si la verificacion anterior falla, se detiene la instalacion por permisos.
if not "%ERRORLEVEL%"=="0" (
    echo ERROR: Este instalador debe ejecutarse como administrador.
    echo.
    echo Haga clic derecho sobre este archivo y seleccione "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

REM Informa que los permisos de administrador fueron confirmados.
echo [OK] Permisos de administrador confirmados.
echo.

REM Sale de la ruta actual y se ubica en la raiz de la unidad activa.
cd \

REM Entra a C:\Windows como paso solicitado de preparacion.
cd /d C:\Windows

REM Verifica si se logro acceder correctamente a C:\Windows.
if not "%ERRORLEVEL%"=="0" (
    echo ERROR: No fue posible acceder a C:\Windows.
    echo.
    pause
    exit /b 1
)

REM Informa que se accedio correctamente a C:\Windows.
echo [OK] Acceso a C:\Windows completado.

REM Entra a C:\Program Files como paso solicitado antes de crear la carpeta.
cd /d "C:\Program Files"

REM Verifica si se logro acceder correctamente a C:\Program Files.
if not "%ERRORLEVEL%"=="0" (
    echo ERROR: No fue posible acceder a C:\Program Files.
    echo Verifique los permisos del sistema.
    echo.
    pause
    exit /b 1
)

REM Informa que se accedio correctamente a C:\Program Files.
echo [OK] Acceso a C:\Program Files completado.
echo.

REM Crea la carpeta final del proyecto si todavia no existe.
if not exist "%INSTALL_DIR%" md "%INSTALL_DIR%"

REM Verifica si la carpeta final del proyecto existe despues de intentar crearla.
if not exist "%INSTALL_DIR%" (
    echo ERROR: No se pudo crear la carpeta:
    echo %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

REM Informa que la carpeta de instalacion esta lista.
echo [OK] Carpeta de instalacion lista:
echo      %INSTALL_DIR%
echo.

REM Busca primero el ZIP con nombre exacto junto a este archivo BAT.
if exist "%SCRIPT_DIR%%ZIP_NAME%" set "RUTA_ORIGEN=%SCRIPT_DIR%%ZIP_NAME%"

REM Si no se encontro el ZIP exacto, busca automaticamente el primer ZIP disponible.
if "%RUTA_ORIGEN%"=="" (
    for %%Z in ("%SCRIPT_DIR%*.zip") do (
        if "!RUTA_ORIGEN!"=="" if exist "%%~fZ" set "RUTA_ORIGEN=%%~fZ"
    )
)

REM Verifica si finalmente se encontro algun archivo ZIP para instalar.
if "%RUTA_ORIGEN%"=="" (
    echo ERROR: No se encontro ningun archivo ZIP junto a este instalador.
    echo.
    echo Coloque Proyecto_SARC.zip en la misma carpeta que este archivo BAT.
    echo Ruta revisada:
    echo %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

REM Informa cual ZIP sera usado como origen de instalacion.
echo [OK] ZIP detectado:
echo      %RUTA_ORIGEN%
echo.

REM Elimina una carpeta temporal anterior para evitar mezclar archivos viejos.
if exist "%TEMP_EXTRACT%" rd /s /q "%TEMP_EXTRACT%"

REM Crea una carpeta temporal limpia para la extraccion del ZIP.
md "%TEMP_EXTRACT%"

REM Verifica si la carpeta temporal fue creada correctamente.
if not exist "%TEMP_EXTRACT%" (
    echo ERROR: No se pudo crear la carpeta temporal de extraccion.
    echo %TEMP_EXTRACT%
    echo.
    pause
    exit /b 1
)

REM Informa que comenzara la extraccion del archivo ZIP.
echo Extrayendo archivos del proyecto...

REM Usa PowerShell unicamente para extraer el ZIP, como fue solicitado.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Expand-Archive -LiteralPath $env:RUTA_ORIGEN -DestinationPath $env:TEMP_EXTRACT -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"

REM Verifica si PowerShell reporto error durante la extraccion.
if not "%ERRORLEVEL%"=="0" (
    echo.
    echo ERROR: Fallo la extraccion del archivo ZIP.
    echo Verifique que el ZIP no este corrupto o bloqueado por Windows.
    echo.
    pause
    exit /b 1
)

REM Informa que la extraccion temporal fue exitosa.
echo [OK] Extraccion del ZIP completada.
echo.

REM Usa la carpeta temporal como origen inicial de copia.
set "COPY_SOURCE=%TEMP_EXTRACT%"

REM Si el ZIP contiene una carpeta raiz Proyecto_SARC, usa esa carpeta como origen real.
if exist "%TEMP_EXTRACT%\Proyecto_SARC\" set "COPY_SOURCE=%TEMP_EXTRACT%\Proyecto_SARC"

REM Si el ZIP contiene una carpeta raiz con el mismo nombre base del ZIP, usa esa carpeta.
for %%N in ("%RUTA_ORIGEN%") do if exist "%TEMP_EXTRACT%\%%~nN\" set "COPY_SOURCE=%TEMP_EXTRACT%\%%~nN"

REM Informa la carpeta exacta desde donde se copiaran los archivos extraidos.
echo [OK] Origen real de copia:
echo      %COPY_SOURCE%
echo.

REM Copia todos los archivos extraidos hacia C:\Program Files\Proyecto_SARC.
echo Copiando archivos hacia la carpeta final...

REM Usa robocopy, comando nativo de Windows, para copiar todo el contenido.
robocopy "%COPY_SOURCE%" "%INSTALL_DIR%" /E /COPY:DAT /R:2 /W:2 >nul

REM Robocopy considera exitosos los codigos de salida menores que 8.
if %ERRORLEVEL% GEQ 8 (
    echo ERROR: Fallo la copia de archivos hacia:
    echo %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

REM Verifica que exista contenido dentro de la carpeta instalada.
dir /b "%INSTALL_DIR%" >nul 2>&1

REM Si no se puede listar contenido, la copia no fue valida.
if not "%ERRORLEVEL%"=="0" (
    echo ERROR: No se pudo verificar el contenido instalado.
    echo.
    pause
    exit /b 1
)

REM Informa que la copia fue validada correctamente.
echo [OK] Archivos copiados y verificados correctamente.
echo.

REM Crea o actualiza la variable de entorno del sistema SARC_HOME.
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v SARC_HOME /t REG_EXPAND_SZ /d "%INSTALL_DIR%" /f >nul

REM Verifica si se pudo crear la variable SARC_HOME.
if not "%ERRORLEVEL%"=="0" (
    echo ADVERTENCIA: No se pudo crear la variable de entorno SARC_HOME.
) else (
    echo [OK] Variable de entorno SARC_HOME configurada.
)

REM Lee el PATH del sistema desde el registro de Windows.
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| find /I "Path"') do set "CURRENT_SYSTEM_PATH=%%B"

REM Si no se pudo leer el PATH del sistema, usa el PATH disponible en la sesion actual.
if "%CURRENT_SYSTEM_PATH%"=="" set "CURRENT_SYSTEM_PATH=%PATH%"

REM Revisa si la ruta del proyecto ya existe dentro del PATH.
echo ;!CURRENT_SYSTEM_PATH!; | find /I ";%INSTALL_DIR%;" >nul 2>&1

REM Si la ruta aun no existe en PATH, se agrega al PATH del sistema.
if not "%ERRORLEVEL%"=="0" (
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "!CURRENT_SYSTEM_PATH!;%INSTALL_DIR%" /f >nul
    if "!ERRORLEVEL!"=="0" (
        echo [OK] Ruta del proyecto agregada al PATH del sistema.
    ) else (
        echo ADVERTENCIA: No se pudo agregar la ruta del proyecto al PATH.
    )
) else (
    echo [OK] La ruta del proyecto ya existe en el PATH.
)

REM Separa visualmente la configuracion de entorno del siguiente bloque.
echo.

REM Busca primero el lanzador silencioso de SARC. La aplicacion no debe abrirse
REM como archivo HTML directo porque usa ES Modules y fetch.
if "%TARGET_APP%"=="" (
    for /f "delims=" %%B in ('dir /b /s "%INSTALL_DIR%\iniciar_sarc.vbs" 2^>nul') do (
        if "!TARGET_APP!"=="" set "TARGET_APP=%%~fB"
    )
)

REM Si no se encontro VBS, busca un ejecutable principal dentro del proyecto instalado.
if "%TARGET_APP%"=="" (
    for /f "delims=" %%E in ('dir /b /s "%INSTALL_DIR%\*.exe" 2^>nul') do (
        if "!TARGET_APP!"=="" set "TARGET_APP=%%~fE"
    )
)

REM Verifica si se encontro algun archivo valido para abrir desde el acceso directo.
if "%TARGET_APP%"=="" (
    echo ERROR: No se encontro iniciar_sarc.vbs ni ningun archivo .exe para el acceso directo.
    echo.
    pause
    exit /b 1
)

REM Informa el archivo principal detectado para el acceso directo.
echo [OK] Archivo principal detectado:
echo      %TARGET_APP%

REM Busca un icono personalizado ICO dentro del proyecto instalado.
for /f "delims=" %%I in ('dir /b /s "%INSTALL_DIR%\*.ico" 2^>nul') do (
    if "!ICON_FILE!"=="" set "ICON_FILE=%%~fI"
)

REM Si no se encontro icono, se informa como advertencia sin detener la instalacion.
if "%ICON_FILE%"=="" (
    echo ADVERTENCIA: No se encontro archivo .ico; se usara el icono predeterminado.
) else (
    echo [OK] Icono personalizado detectado:
    echo      %ICON_FILE%
)

REM Detecta el escritorio real desde el registro del usuario actual.
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| find /I "Desktop"') do set "DESKTOP_DIR=%%B"

REM Expande variables como %%USERPROFILE%% si el registro las devuelve sin resolver.
call set "DESKTOP_DIR=%DESKTOP_DIR%"

REM Si la ruta del registro no existe fisicamente, la descarta para probar respaldos.
if not "%DESKTOP_DIR%"=="" if not exist "%DESKTOP_DIR%" set "DESKTOP_DIR="

REM Si el registro no entrega una ruta valida, intenta con el escritorio de OneDrive.
if "%DESKTOP_DIR%"=="" if exist "%USERPROFILE%\OneDrive\Desktop" set "DESKTOP_DIR=%USERPROFILE%\OneDrive\Desktop"

REM Si el equipo usa nombre localizado, intenta con OneDrive\Escritorio.
if "%DESKTOP_DIR%"=="" if exist "%USERPROFILE%\OneDrive\Escritorio" set "DESKTOP_DIR=%USERPROFILE%\OneDrive\Escritorio"

REM Si OneDrive no aplica, intenta con el escritorio local tradicional.
if "%DESKTOP_DIR%"=="" if exist "%USERPROFILE%\Desktop" set "DESKTOP_DIR=%USERPROFILE%\Desktop"

REM Como ultimo respaldo localizado, intenta con la carpeta Escritorio local.
if "%DESKTOP_DIR%"=="" if exist "%USERPROFILE%\Escritorio" set "DESKTOP_DIR=%USERPROFILE%\Escritorio"

REM Verifica si existe la carpeta Escritorio detectada.
if "%DESKTOP_DIR%"=="" (
    echo ERROR: No se pudo detectar la ruta del escritorio del usuario actual.
    echo.
    pause
    exit /b 1
)

REM Verifica si la carpeta Escritorio detectada existe fisicamente.
if not exist "%DESKTOP_DIR%" (
    echo ERROR: La ruta de escritorio detectada no existe:
    echo %DESKTOP_DIR%
    echo.
    pause
    exit /b 1
)

REM Define la ruta completa del acceso directo despues de detectar el escritorio.
set "SHORTCUT_PATH=%DESKTOP_DIR%\%SHORTCUT_NAME%.lnk"

REM Informa la ruta de escritorio que se usara para crear el acceso directo.
echo [OK] Escritorio detectado:
echo      %DESKTOP_DIR%

REM Informa que se creara el acceso directo en el escritorio actual.
echo.
echo Creando acceso directo en el escritorio...

REM Usa PowerShell unicamente para crear el acceso directo .lnk.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; try { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut($env:SHORTCUT_PATH); $Shortcut.TargetPath = $env:TARGET_APP; $Shortcut.Arguments = ''; $Shortcut.WorkingDirectory = $env:INSTALL_DIR; if (($env:ICON_FILE -ne '') -and (Test-Path -LiteralPath $env:ICON_FILE)) { $Shortcut.IconLocation = $env:ICON_FILE + ',0' }; $Shortcut.Save(); exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"

REM Verifica si PowerShell reporto error al crear el acceso directo.
if not "%ERRORLEVEL%"=="0" (
    echo ERROR: Fallo la creacion del acceso directo.
    echo.
    pause
    exit /b 1
)

REM Verifica si el archivo .lnk existe fisicamente en el escritorio.
if not exist "%SHORTCUT_PATH%" (
    echo ERROR: No se encontro el acceso directo despues de crearlo.
    echo %SHORTCUT_PATH%
    echo.
    pause
    exit /b 1
)

REM Informa que el acceso directo fue creado correctamente.
echo [OK] Acceso directo creado:
echo      %SHORTCUT_PATH%
echo.

REM Limpia la carpeta temporal usada para extraer el ZIP.
if exist "%TEMP_EXTRACT%" rd /s /q "%TEMP_EXTRACT%"

REM Muestra el resumen final de la instalacion.
echo ============================================================
echo  INSTALACION COMPLETADA CORRECTAMENTE
echo ============================================================
echo Proyecto instalado en:
echo %INSTALL_DIR%
echo.
echo Acceso directo creado como:
echo %SHORTCUT_NAME%
echo.
echo Nota: si se modifico el PATH, abra una nueva consola para usarlo.
echo.

REM Pausa final para que el usuario pueda leer el resultado.
pause

REM Cierra el entorno local de variables del instalador.
endlocal

REM Devuelve codigo de salida exitoso al sistema.
exit /b 0
