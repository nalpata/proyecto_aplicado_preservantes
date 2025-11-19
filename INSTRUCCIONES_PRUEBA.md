# 🧪 Instrucciones para Probar las Mejoras

## ⚡ Prueba Rápida (Sin Dependencias Completas)

Para validar que el chunking semántico y filtrado funcionen correctamente:

```bash
python3 test_improvements.py
```

**Esto probará:**
- ✅ Detección de secciones (referencias, agradecimientos, apéndices)
- ✅ Filtrado de contenido de bajo valor
- ✅ Chunking semántico respetando párrafos
- ✅ Protección de abreviaciones científicas (e.g., i.e., pH, aW, etc.)
- ✅ Overlap inteligente entre chunks

**Resultado esperado:**
```
🧪 PRUEBAS DE MEJORAS DEL SISTEMA

============================================================
TEST 1: DETECCIÓN DE SECCIONES
============================================================
📊 Estadísticas de Filtrado:
  - Caracteres originales: 1029
  - Caracteres filtrados: 618
  - Reducción: ~40%
  - Secciones removidas: 3
...
✅ TODAS LAS PRUEBAS COMPLETADAS
```

---

## 🔬 Prueba Completa con PDFs

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

O si prefieres usar un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 2: Ejecutar Pipeline Completo

```bash
python run_pipeline.py
```

**Esto ejecutará:**
1. Ingesta de PDFs desde `data/pdfs/`
2. Limpieza y **filtrado de secciones** (referencias, tablas, etc.)
3. **Chunking semántico** (respeta párrafos y oraciones)
4. Extracción de metadata
5. Vectorización e indexación
6. Búsquedas de prueba

**Salida esperada:**
```
🧬 PRESERV-RAG - PIPELINE BASELINE (HITO 1)
============================================================

1️⃣  INGESTA DE PDFs
------------------------------------------------------------
✓ 18 PDFs cargados
  - Total páginas: XXX
  - Total caracteres: XXX,XXX

2️⃣  EXTRACCIÓN, LIMPIEZA Y FILTRADO DE TEXTO
------------------------------------------------------------
✓ Texto procesado (limpieza + filtrado)
  - Reducción de caracteres: XX%
  - Caracteres originales: XXX,XXX
  - Caracteres finales: XXX,XXX

  📝 Secciones filtradas:
    - Referencias: XX
    - Tablas: XX
    - Agradecimientos: XX
    - Apéndices: XX
    - Headers/Footers: XXX

3️⃣  DIVISIÓN EN CHUNKS (SEMÁNTICO)
------------------------------------------------------------
✓ Documentos divididos en chunks semánticos
  - Total chunks: XXX
  - Documentos únicos: 18
  - Tamaño promedio: ~500 caracteres
  - Tamaño mín/máx: XX/XXX
  - Chunks por documento: XX
  - Párrafos por chunk: ~X.X

...

✅ PIPELINE COMPLETADO EXITOSAMENTE

🆕 MEJORAS IMPLEMENTADAS:
  ✓ Filtrado de secciones de bajo valor
  ✓ Chunking semántico
  ✓ Overlap inteligente
  ✓ No corta en abreviaciones científicas
```

### Paso 3: Interfaz Gráfica con Streamlit

```bash
streamlit run streamlit_app.py
```

**En el navegador (http://localhost:8501):**

1. **Sidebar - Configuración:**
   - ✅ Marcar "Filtrar secciones de bajo valor"
   - ✅ Seleccionar qué filtrar (referencias, tablas, etc.)
   - Ajustar tamaño de chunk y overlap

2. **Tab "Pipeline":**
   - Ejecutar paso a paso
   - Ver estadísticas de filtrado en tiempo real
   - Observar chunks generados

3. **Tab "Búsqueda":**
   - Probar queries
   - Verificar que no se recuperen chunks de referencias

4. **Tab "Métricas Baseline":**
   - Evaluar con queries de prueba
   - Comparar métricas

---

## 🔍 Validación de Mejoras

### Verificar Filtrado Funciona

Después de ejecutar `run_pipeline.py`, busca en la salida:

```
📝 Secciones filtradas:
  - Referencias: > 0
  - Tablas: > 0
  - Agradecimientos: > 0
```

Si los números son > 0, el filtrado está funcionando.

### Verificar Chunking Semántico

Busca en la salida:

```
- Párrafos por chunk: ~2.5 (o similar)
```

Esto indica que los chunks respetan párrafos completos.

### Verificar No Se Cortan Abreviaciones

Ejecuta:
```bash
python3 test_improvements.py
```

Y revisa el **TEST 3** - no debe haber advertencias.

---

## 📊 Comparar con Baseline Original

### Opción 1: Deshabilitar Mejoras en Streamlit

1. Abrir Streamlit
2. **Desmarcar** "Filtrar secciones de bajo valor" en sidebar
3. Ejecutar pipeline
4. Guardar métricas

Luego:
5. **Marcar** "Filtrar secciones de bajo valor"
6. Ejecutar pipeline nuevamente
7. Comparar métricas

### Opción 2: Usar Código

```python
# Baseline (sin filtrado)
extractor_baseline = TextExtractor(filter_sections=False)
chunker_baseline = DocumentChunker(chunk_size=500, overlap=50)

# Mejorado (con filtrado)
extractor_improved = TextExtractor(filter_sections=True)
chunker_improved = DocumentChunker(chunk_size=500, overlap=50, min_chunk_size=100)

# Comparar estadísticas
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'PyPDF2'"

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "FileNotFoundError: Carpeta no encontrada: data/pdfs"

**Solución:**
Verifica que exista la carpeta y tenga PDFs:
```bash
ls data/pdfs/*.pdf
```

### Los tests pasan pero el pipeline falla

**Causa probable:** Dependencias no instaladas completamente.

**Solución:**
```bash
pip install PyPDF2 sentence-transformers chromadb streamlit pandas numpy python-dotenv
```

### Chunks muy pequeños o muy grandes

**Solución:** Ajustar parámetros en `run_pipeline.py`:
```python
chunk_size = 500     # Cambiar a 300, 700, etc.
overlap = 50         # Cambiar a 30, 100, etc.
min_chunk_size = 100 # Cambiar a 50, 150, etc.
```

---

## 📝 Notas Importantes

1. **Primera ejecución:** El pipeline descargará el modelo de embeddings (~22 MB). Esto puede tomar 1-2 minutos.

2. **Vectorización:** Con 18 PDFs, puede tomar 3-5 minutos crear la base vectorial completa.

3. **Configuración por defecto:** El sistema filtra TODAS las secciones de bajo valor por defecto. Esto es intencional para maximizar la calidad.

4. **Memoria:** El proceso puede usar ~500 MB - 1 GB de RAM al vectorizar todos los PDFs.

5. **Base de datos:** Se crea en `data/chroma_db/`. Puedes borrarla y recrearla cuando quieras:
   ```bash
   rm -rf data/chroma_db
   python run_pipeline.py
   ```

---

## ✅ Checklist de Validación

Después de probar, verifica:

- [ ] `test_improvements.py` pasa exitosamente
- [ ] `run_pipeline.py` completa sin errores
- [ ] Se muestran estadísticas de secciones filtradas
- [ ] Los chunks tienen tamaños razonables (100-600 caracteres)
- [ ] El chunking respeta párrafos (avg_paragraphs_per_chunk > 1)
- [ ] Streamlit se ejecuta correctamente
- [ ] Las búsquedas NO retornan chunks de referencias
- [ ] Los chunks contienen información científica útil (pH, aW, microorganismos)

---

## 📞 Soporte

Si encuentras problemas, revisa:

1. **MEJORAS_CHUNKING.md** - Documentación completa
2. **PROBLEMAS_COMUNES.md** - Soluciones a errores comunes
3. **Logs del pipeline** - Ejecutar con output completo

---

**¡Listo para probar!** 🚀

Empieza con `python3 test_improvements.py` para una validación rápida.
