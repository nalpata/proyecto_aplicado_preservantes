# RAG – Hito 2 | Presentación Final

Este repositorio implementa una solución completa de **Retrieval-Augmented Generation (RAG)** que se ejecuta **localmente**, con una **interfaz de usuario en Streamlit** que permite visualizar y probar todo el pipeline de forma interactiva.

El objetivo del proyecto es demostrar, de manera modular y reproducible, las tres etapas fundamentales de un sistema RAG:
1. **Ingesta de documentos**
2. **Recuperación de contexto**
3. **Generación de respuestas con un LLM local**

---

## 🧩 Arquitectura general

La solución está diseñada siguiendo un enfoque **modular**, donde cada componente del pipeline está desacoplado y puede evaluarse de forma independiente.

### Pipeline RAG
1. **Ingesta**
   - Carga de documentos PDF
   - Extracción de texto
   - Segmentación en fragmentos (*chunking*)
   - Persistencia del índice

2. **Recuperación**
   - Recuperación basada en similitud vectorial
   - Recuperación léxica con BM25
   - Estrategia híbrida (vector + BM25)

3. **Generación**
   - Uso de un modelo de lenguaje local en formato GGUF
   - Generación de respuestas restringidas exclusivamente al contexto recuperado

La interfaz Streamlit muestra visualmente estas tres etapas, permitiendo configurar parámetros y observar los resultados de cada fase.

---

## 📁 Estructura del repositorio

```text
├── app.py                 # Interfaz Streamlit
├── requirements.txt       # Dependencias del proyecto
├── README.md
│
├── data/
│   ├── pdfs/              # Documentos PDF de entrada
│   └── indexes/           # Índices persistidos del sistema
│
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuración centralizada
│   ├── ingestion.py       # Ingesta y construcción del índice
│   ├── retrieval.py       # Recuperación de contexto
│   ├── generation.py      # Generación con LLM local
│   └── utils.py           # Funciones auxiliares
│
└── notebooks/             # Notebooks de experimentación (opcional)

