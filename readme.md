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
````

---

## ⚙️ Requisitos

* Python 3.9 o superior
* Ejecución local (no depende de APIs externas)
* Modelo de lenguaje local en formato **GGUF**

---

## 📦 Instalación

Clonar el repositorio y crear un entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno:

* **Windows**

```bash
.venv\Scripts\activate
```

* **Linux / Mac**

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución de la aplicación

1. Colocar los documentos PDF en la carpeta:

```text
data/pdfs/
```

2. Ejecutar la aplicación Streamlit:

```bash
streamlit run app.py
```

3. En la interfaz:

   * Configurar rutas y parámetros desde la barra lateral
   * (Opcional) reprocesar los documentos
   * Ingresar una pregunta y observar:

     * Contexto recuperado
     * Respuesta generada
     * Fuentes utilizadas

---

## 🧠 Modelo de lenguaje

El sistema utiliza un **LLM local en formato GGUF**, cargado dinámicamente desde la ruta configurada en la interfaz.

> **Nota:**
> El archivo del modelo no se incluye en el repositorio debido a su tamaño.
> La ruta al modelo se especifica directamente en la interfaz Streamlit.

---

## 🔁 Reproducibilidad

* El proyecto es completamente reproducible en entorno local
* No requiere conexión a servicios externos
* Los índices generados se almacenan en `data/indexes/`
* La modularización permite modificar o extender cada etapa del pipeline

---

## 📌 Observaciones finales

Este proyecto demuestra el funcionamiento end-to-end de un sistema RAG, haciendo énfasis en:

* Separación clara de responsabilidades
* Transparencia del proceso de recuperación
* Reducción de alucinaciones mediante generación condicionada al contexto

```

---
