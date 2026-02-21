@echo off
REM Script de instalación para FarmaControl en Windows

echo ======================================
echo    FarmaControl - Setup Installation
echo ======================================
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate

REM Instalar dependencias
echo Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Crear archivo .env
echo Configurando variables de entorno...
if not exist .env (
    copy .env.example .env
    echo Archivo .env creado. Por favor, editalo con tus credenciales de MySQL
) else (
    echo Archivo .env ya existe
)

REM Crear directorios necesarios
echo Creando directorios...
mkdir backend\static\css
mkdir backend\static\js
mkdir backend\templates\admin
mkdir backend\templates\vendedor
mkdir database

echo.
echo ======================================
echo Setup completado!
echo ======================================
echo.
echo Próximos pasos:
echo 1. Editar .env con tus credenciales MySQL
echo 2. Crear la base de datos: mysql -u root -p ^< database\schema.sql
echo 3. Activar entorno: venv\Scripts\activate
echo 4. Iniciar la app: python backend/app.py
echo.
echo La aplicación estará en: http://localhost:5000
echo.
pause
