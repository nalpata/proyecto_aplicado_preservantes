import streamlit as st
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# === Configuración de rutas y modelo ===
BASE_PATH = Path("/content/proyecto_aplicado_preservantes")
CHROMA_HIER_DIR = BASE_PATH / "chroma_preservantes_hier"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# === Dataset de evaluación) ===
eval_queries = [
    {
  "query": "¿Qué es un preservante antimicrobiano?",
  "relevant_keywords": [
    "preservante antimicrobiano",
    "conservante antimicrobiano",
    "inhibición microbiana",
    "inhibe el crecimiento microbiano",
    "sustancia antimicrobiana",
    "agente antimicrobiano",
    "inhibición de microorganismos",

    "antimicrobial preservative",
    "antimicrobial agent",
    "microbial growth inhibition",
    "inhibits microbial growth"
  ]
},
{
  "query": "¿Cuáles son los factores que afectan la efectividad de los preservantes?",
  "relevant_keywords": [
    "efectividad de los preservantes",
    "factores que afectan la efectividad",
    "actividad de agua",
    "aw",
    "concentración del conservante",
    "concentración inhibitoria",
    "pKa del conservante",
    "interacción con composición del alimento",

    "preservative effectiveness",
    "factors influencing preservative efficacy",
    "water activity",
    "aw value",
    "preservative concentration",
    "food composition interaction",
    "minimum inhibitory concentration"
  ]
},
{
  "query": "¿Qué se entiende por vida útil de un alimento?",
  "relevant_keywords": [
    "vida útil del alimento",
    "vida útil",
    "deterioro microbiano",
    "estabilidad del alimento",
    "seguridad alimentaria",
    "calidad durante el almacenamiento",

    "shelf life",
    "food shelf life",
    "food spoilage",
    "microbial spoilage",
    "quality stability",
    "storage stability"
  ]
}
]

# ========= Funciones auxiliares ===============================================

@st.cache_resource
def load_retriever(k: int = 5, fetch_k: int = 20):
    """
    Carga el vector store jerárquico desde disco y construye
    un retriever MMR con los mismos parámetros que usas en el notebook.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store_hier = Chroma(
        persist_directory=str(CHROMA_HIER_DIR),
        embedding_function=embeddings,
    )

    retriever_hier = vector_store_hier.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k},
    )
    return retriever_hier


def precision_at_k(retriever, query: str, relevant_keywords, k: int = 5) -> float:
    """
    Calcula Precision@k para una query:
    - Usa retriever.invoke(query) (versión nueva de LangChain)
    - Cuenta acierto si el chunk contiene al menos una de las palabras clave.
    """
    docs = retriever.invoke(query)
    docs = docs[:k]

    hits = 0
    normalized_keywords = [kw.lower() for kw in relevant_keywords]

    for d in docs:
        text = d.page_content.lower()
        if any(kw in text for kw in normalized_keywords):
            hits += 1

    return hits / k if k > 0 else 0.0


def evaluate_retriever_precision(retriever, eval_queries, k: int = 5):
    """Evalúa Precision@k para todas las queries de eval."""
    scores = []
    for item in eval_queries:
        p_at_k = precision_at_k(
            retriever,
            query=item["query"],
            relevant_keywords=item["relevant_keywords"],
            k=k,
        )
        scores.append({"query": item["query"], f"precision@{k}": round(p_at_k, 2)})
    return scores


# ========= Interfaz Streamlit =================================================

st.set_page_config(page_title="RAG Preservantes - Retriever Jerárquico (MMR)", layout="wide")
st.title(" RAG de preservantes de alimentos")
st.subheader("Retriever jerárquico + MMR sobre PDFs de preservantes")

st.markdown(
    """
Esta app usa **tu vector store jerárquico** (`chroma_preservantes_hier`) con el
modelo de *embeddings* multilingüe `all-MiniLM-L6-v2` y un **retriever MMR**.
Puedes:

1. Hacer consultas y ver los chunks más relevantes.
2. Calcular un pequeño benchmark de **Precision@k** sobre un set de preguntas.
"""
)

with st.sidebar:
    st.header(" Configuración")
    k = st.slider("k (número de documentos a devolver)", min_value=1, max_value=10, value=5)
    fetch_k = st.slider("fetch_k (documentos candidatos para MMR)", min_value=10, max_value=50, value=20, step=5)

    st.write("---")
    st.write("Recuerda haber ejecutado en Colab el notebook que crea la carpeta:")
    st.code(str(CHROMA_HIER_DIR), language="bash")

# Cargar retriever (se cachea para no recargar todo el tiempo)
retriever = load_retriever(k=k, fetch_k=fetch_k)

tab1, tab2 = st.tabs([" Consulta interactiva", "📈 Benchmark (Precision@k)"])

with tab1:
    st.header(" Consulta interactiva")

    query = st.text_input(
        "Escribe tu pregunta sobre preservantes:",
        value="¿Qué tipos de preservantes se usan en bebidas?",
    )

    if st.button("Buscar documentos relevantes"):
        if not query.strip():
            st.warning("Por favor escribe una pregunta.")
        else:
            docs = retriever.invoke(query)
            docs = docs[:k]

            st.success(f"Se recuperaron {len(docs)} documentos (k = {k}).")

            for i, d in enumerate(docs, start=1):
                with st.expander(f"Documento {i}"):
                    meta = d.metadata or {}
                    source = meta.get("source", "desconocido")
                    page = meta.get("page", "N/A")
                    level1 = meta.get("level1_index", "N/A")

                    st.write(f"**Source:** `{source}`")
                    st.write(f"**Página:** {page}")
                    st.write(f"**Nivel jerárquico (level1_index):** {level1}")
                    st.write("---")
                    st.write(d.page_content)

with tab2:
    st.header(" Benchmark de Precision@k")

    st.markdown(
        """
Se usa un pequeño set de preguntas de evaluación manual (`eval_queries`)
con palabras clave en español e inglés.
"""
    )

    k_bench = st.slider("k para el benchmark", min_value=1, max_value=10, value=5, key="bench_k")

    if st.button("Calcular Precision@k", key="run_bench"):
        results = evaluate_retriever_precision(retriever, eval_queries, k=k_bench)

        # Mostrar tabla
        st.subheader("Resultados por pregunta")
        st.table(results)

        avg = sum(row[f"precision@{k_bench}"] for row in results) / len(results)
        st.subheader("Promedio")
        st.metric(label=f"Precision@{k_bench} promedio", value=f"{avg:.2f}")
