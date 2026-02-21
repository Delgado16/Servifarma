#!/bin/bash

# Script de instalación para FarmaControl

echo "======================================"
echo "   FarmaControl - Setup Installation"
echo "======================================"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env
echo "⚙️  Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Archivo .env creado. Por favor, edítalo con tus credenciales de MySQL"
else
    echo "✅ Archivo .env ya existe"
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/templates/admin
mkdir -p backend/templates/vendedor
mkdir -p database

echo ""
echo "======================================"
echo "✅ Setup completado!"
echo "======================================"
echo ""
echo "Próximos pasos:"
echo "1. Editar .env con tus credenciales MySQL"
echo "2. Crear la base de datos: mysql -u root -p < database/schema.sql"
echo "3. Activar entorno: source venv/bin/activate"
echo "4. Iniciar la app: python backend/app.py"
echo ""
echo "La aplicación estará en: http://localhost:5000"
echo ""
