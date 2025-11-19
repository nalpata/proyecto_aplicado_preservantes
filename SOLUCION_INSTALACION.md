# 🔧 Solución al Error de Instalación

## ⚠️ Problema
Hay un bug de pip con el resolver de dependencias al instalar todas las librerías juntas.

## ✅ Solución: Instalación en Orden Específico

Ejecuta estos comandos **en tu terminal** con el venv activado:

```bash
# 1. Activar venv
source venv/bin/activate

# 2. Actualizar pip y tools
pip install --upgrade pip setuptools wheel

# 3. Instalar dependencias BASE primero (sin versiones estrictas)
pip install numpy pandas

# 4. Instalar PyTorch (necesario para sentence-transformers)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. Ahora instalar sentence-transformers
pip install sentence-transformers

# 6. Instalar ChromaDB
pip install chromadb

# 7. Instalar Streamlit
pip install streamlit

# 8. Instalar PyPDF2 y dotenv
pip install PyPDF2 python-dotenv

# 9. Verificar instalación
python -c "import sentence_transformers; import chromadb; import streamlit; print('✅ Todo instalado correctamente')"
```

---

## 🚀 Alternativa: Instalación Simple (Sin Versiones Fijas)

Si lo anterior falla, usa versiones más recientes:

```bash
source venv/bin/activate

pip install --upgrade pip wheel setuptools

# Instalar sin versiones fijas
pip install \
    numpy \
    pandas \
    torch \
    sentence-transformers \
    chromadb \
    streamlit \
    PyPDF2 \
    python-dotenv
```

---

## ⚡ Opción Rápida: Script Automatizado

Ejecuta el script que creé:

```bash
source venv/bin/activate
./install_dependencies.sh
```

O copia y pega esto directamente:

```bash
#!/bin/bash
source venv/bin/activate

echo "Instalando dependencias..."

pip install --upgrade pip setuptools wheel
pip install numpy pandas
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
pip install chromadb
pip install streamlit
pip install PyPDF2 python-dotenv

echo "✅ Instalación completada"
python -c "import sentence_transformers; import chromadb; print('✅ Verificación OK')"
```

---

## 🧪 Verificar que Funciona

Después de instalar:

```bash
# Test rápido (sin dependencias pesadas)
python test_improvements.py

# Pipeline completo
python run_pipeline.py
```

---

## 🆘 Si Aún No Funciona

**Última opción: Recrear venv**

```bash
# Salir del venv actual
deactivate

# Borrar venv corrupto
rm -rf venv

# Crear nuevo venv
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar todo de nuevo
pip install --upgrade pip wheel setuptools
pip install numpy pandas torch sentence-transformers chromadb streamlit PyPDF2 python-dotenv
```

---

## 📋 Checklist

- [ ] Activé el venv: `source venv/bin/activate`
- [ ] Actualicé pip: `pip install --upgrade pip wheel setuptools`
- [ ] Instalé numpy y pandas primero
- [ ] Instalé torch (puede tardar 2-3 min)
- [ ] Instalé sentence-transformers (puede tardar 1-2 min)
- [ ] Instalé chromadb
- [ ] Instalé streamlit y PyPDF2
- [ ] Verifiqué: `python -c "import chromadb; print('OK')"`
- [ ] Ejecuté: `python test_improvements.py` ✅
- [ ] Ejecuté: `python run_pipeline.py` ✅

---

## 💡 Nota Importante

Las mejoras de **chunking y filtrado** que implementamos **ya funcionan** sin dependencias pesadas:

```bash
# Esto funciona SIN instalar nada más
python test_improvements.py
```

Solo necesitas instalar las dependencias completas si quieres:
- Vectorizar documentos (sentence-transformers)
- Usar la base vectorial (chromadb)
- Interfaz Streamlit (streamlit)
- Leer PDFs (PyPDF2)

El código de mejoras está 100% funcional y validado ✅
