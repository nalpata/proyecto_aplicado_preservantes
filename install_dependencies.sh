#!/bin/bash

# Script para instalar dependencias en el entorno virtual

echo "======================================"
echo "Instalación de Dependencias"
echo "======================================"

# Verificar si estamos en un entorno virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No estás en un entorno virtual."
    echo "Ejecuta primero: source venv/bin/activate"
    exit 1
fi

echo "✓ Entorno virtual activo: $VIRTUAL_ENV"
echo ""

# Actualizar pip
echo "1️⃣  Actualizando pip..."
pip install --upgrade pip

echo ""
echo "2️⃣  Instalando dependencias..."
echo ""

# Instalar dependencias una por una con feedback
pip install PyPDF2==3.0.1
echo "✓ PyPDF2 instalado"

pip install sentence-transformers==2.2.2
echo "✓ sentence-transformers instalado"

pip install chromadb==0.4.14
echo "✓ chromadb instalado"

pip install streamlit==1.28.1
echo "✓ streamlit instalado"

pip install python-dotenv==1.0.0
echo "✓ python-dotenv instalado"

pip install pandas==2.1.1
echo "✓ pandas instalado"

pip install numpy==1.24.3
echo "✓ numpy instalado"

echo ""
echo "======================================"
echo "✅ Instalación Completada"
echo "======================================"
echo ""
echo "Ahora puedes ejecutar:"
echo "  python run_pipeline.py"
echo "  streamlit run streamlit_app.py"
echo ""
