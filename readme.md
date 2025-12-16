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

---

## 📓 Trabajo experimental y evaluación (Notebook)

El notebook `Proyecto_1_Hito_2.ipynb` documenta el desarrollo completo del **Hito 2**, con foco en la **evaluación y mejora de la etapa de recuperación** dentro de un sistema RAG. A diferencia del Hito 1 (baseline), este trabajo se centra en **analizar las limitaciones del pipeline inicial y proponer mejoras fundamentadas**, evaluadas de forma sistemática.

### 1. Análisis inicial del corpus y baseline

El trabajo comienza con la carga y exploración de un corpus compuesto por múltiples artículos académicos sobre preservantes de alimentos. Durante esta etapa se identificó un **desbalance estructural del corpus**, donde algunos documentos aportaban una cantidad significativamente mayor de fragmentos (*chunks*) que otros.

Este fenómeno, denominado en el notebook como **“PDF dominante”**, genera un sesgo en la recuperación: el sistema tiende a recuperar fragmentos repetidamente del mismo documento, aun cuando otros textos contienen información conceptualmente relevante.

Como punto de partida, se construyó un **baseline RAG** que incluye:

* chunking estándar,
* embeddings multilingües,
* vector store,
* recuperación por similitud,
* y evaluación manual mediante **Precision@k**.

Este baseline se conserva como referencia para comparar todas las mejoras posteriores.

---

### 2. Chunking jerárquico: motivación y diseño

Para mitigar el problema del PDF dominante, el notebook propone e implementa una estrategia de **chunking jerárquico**, inspirada en la necesidad de preservar estructura semántica sin perder granularidad.

El enfoque consta de dos niveles:

* **Nivel 1:** fragmentos grandes que representan unidades semánticas amplias (contexto global).
* **Nivel 2:** sub-fragmentos más pequeños, optimizados para la recuperación.

Cada chunk incluye metadatos jerárquicos (`parent_id`, `level1_index`), lo que permite:

* mejorar la diversidad de los documentos recuperados,
* mantener trazabilidad entre fragmentos,
* y facilitar extensiones posteriores (reranking, agrupación por documento).

Este rediseño busca equilibrar representatividad del corpus sin introducir heurísticas manuales dependientes del dominio.

---

### 3. Embeddings y vector store

El notebook utiliza embeddings multilingües (`distiluse-base-multilingual-cased-v2`), adecuados para un corpus que contiene documentos en más de un idioma.

Sobre estos embeddings se construye un **vector store persistente con Chroma**, incluyendo una versión específica para el chunking jerárquico. La persistencia del índice permite:

* reproducibilidad de los experimentos,
* comparación directa entre configuraciones,
* y reutilización eficiente en fases posteriores del pipeline.

---

### 4. Estrategias de recuperación y evaluación comparativa

Con el nuevo esquema de chunking, se evaluaron distintas estrategias de recuperación:

* **Similarity search (baseline)**
* **MMR (Maximal Marginal Relevance)**, con distintos valores de `k`, `fetch_k` y `lambda_mult`
* **BM25**
* **Estrategias híbridas**
* **Query processing y expansión de consultas**
* **Reranking**

La evaluación se realizó mediante **Precision@k**, definida manualmente a partir de un conjunto de consultas y keywords relevantes, permitiendo comparar de forma consistente todas las variantes.

Los resultados muestran que:

* el uso de MMR no genera mejoras significativas en este dominio específico,
* el chunking jerárquico mejora la diversidad estructural, pero no garantiza mejoras métricas por sí solo,
* **el procesamiento y expansión de consultas es la técnica que produce la mayor mejora observada en Precision@5**,
* las estrategias híbridas y con reranking ofrecen los mejores resultados globales dentro del conjunto evaluado.

---

### 5. Generación y trazabilidad (RAG-G)

Finalmente, el notebook integra un **modelo de lenguaje local** para la generación de respuestas condicionadas al contexto recuperado. La generación se diseña con un **prompt restrictivo**, que obliga al modelo a responder únicamente con la información presente en los fragmentos recuperados, mitigando explícitamente el riesgo de alucinaciones.

Cada respuesta generada se guarda junto con:

* los fragmentos utilizados,
* el documento de origen,
* y los identificadores de chunk,

lo que garantiza **trazabilidad completa** y facilita el análisis posterior del comportamiento del sistema.

---

### 6. Relación entre notebook y aplicación Streamlit

El notebook cumple un rol **analítico y experimental**, donde se exploran múltiples variantes del sistema RAG y se comparan cuantitativamente sus resultados.

La aplicación **Streamlit**, en cambio, implementa una **demo final, modular y reproducible**, que:

* refleja el pipeline conceptual trabajado en el notebook,
* permite ejecutar el sistema localmente,
* y muestra de forma clara las etapas de ingesta, recuperación y generación.

De esta forma, el notebook documenta el **proceso de investigación y toma de decisiones**, mientras que la aplicación presenta la **solución final ejecutable**.

---


