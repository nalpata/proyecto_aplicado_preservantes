#!/bin/bash

# Script para instalar dependencias correctamente (evitando el bug de pip)

set -e  # Salir si hay error

echo "=================================================="
echo "🔧 Instalación Correcta de Dependencias"
echo "=================================================="
echo ""

# Verificar que estamos en venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No estás en el entorno virtual"
    echo "Ejecuta primero: source venv/bin/activate"
    exit 1
fi

echo "✓ Entorno virtual activo: $VIRTUAL_ENV"
echo ""

# Paso 1: Actualizar pip
echo "1️⃣  Actualizando pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✓ pip actualizado"
echo ""

# Paso 2: Instalar dependencias base
echo "2️⃣  Instalando numpy y pandas..."
pip install numpy pandas > /dev/null 2>&1
echo "✓ numpy y pandas instalados"
echo ""

# Paso 3: Instalar PyTorch (CPU version)
echo "3️⃣  Instalando PyTorch (puede tardar 2-3 minutos)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch instalado"
echo ""

# Paso 4: Instalar sentence-transformers
echo "4️⃣  Instalando sentence-transformers..."
pip install sentence-transformers
echo "✓ sentence-transformers instalado"
echo ""

# Paso 5: Instalar ChromaDB
echo "5️⃣  Instalando ChromaDB..."
pip install chromadb
echo "✓ ChromaDB instalado"
echo ""

# Paso 6: Instalar Streamlit
echo "6️⃣  Instalando Streamlit..."
pip install streamlit
echo "✓ Streamlit instalado"
echo ""

# Paso 7: Instalar resto
echo "7️⃣  Instalando PyPDF2 y python-dotenv..."
pip install PyPDF2 python-dotenv
echo "✓ PyPDF2 y python-dotenv instalados"
echo ""

# Verificación final
echo "=================================================="
echo "🧪 Verificando instalación..."
echo "=================================================="

python -c "
import sys
try:
    import PyPDF2
    print('✓ PyPDF2')
    import sentence_transformers
    print('✓ sentence-transformers')
    import chromadb
    print('✓ chromadb')
    import streamlit
    print('✓ streamlit')
    import pandas
    print('✓ pandas')
    import numpy
    print('✓ numpy')
    print('')
    print('✅ TODAS LAS DEPENDENCIAS INSTALADAS CORRECTAMENTE')
except ImportError as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

echo ""
echo "=================================================="
echo "✅ Instalación completada exitosamente"
echo "=================================================="
echo ""
echo "Ahora puedes ejecutar:"
echo "  python test_improvements.py"
echo "  python run_pipeline.py"
echo "  streamlit run streamlit_app.py"
echo ""
