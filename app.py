import streamlit as st
from src.config import AppConfig
from src.ingestion import build_or_load_index
from src.retrieval import retrieve_context
from src.generation import generate_answer

st.set_page_config(page_title="RAG Hito 2 - Demo", layout="wide")

cfg = AppConfig()

# ✅ Ruta por defecto del modelo GGUF (para evitar fallback)
cfg.llm_model_path = r"C:\Users\Patricia Patiño\Documents\proyecto_aplicado_preservantes\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"

st.title(" RAG Hito 2 – Presentación Final")
st.caption("Pipeline completo: Ingesta → Recuperación → Generación (local).")

# Sidebar: configuración general
with st.sidebar:
    st.header("⚙️ Configuración")
    cfg.data_dir = st.text_input("Carpeta PDFs", value=cfg.data_dir)
    cfg.persist_dir = st.text_input("Carpeta índice", value=cfg.persist_dir)

    st.subheader("Retriever")
    cfg.retrieval_mode = st.selectbox(
        "Modo de recuperación",
        ["vector", "bm25", "hybrid"],
        index=["vector", "bm25", "hybrid"].index(cfg.retrieval_mode),
    )
    cfg.top_k = st.slider("Top-k", 1, 20, cfg.top_k)

    st.subheader("LLM local (GGUF)")
    cfg.llm_model_path = st.text_input("Ruta modelo GGUF", value=cfg.llm_model_path)
    cfg.temperature = st.slider("Temperature", 0.0, 1.5, float(cfg.temperature))

    st.divider()
    run_ingest = st.button("🔁 Reprocesar / Reindexar PDFs")

# 3 columnas para separación visual
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1) Ingesta")
    st.write("Carga PDFs, chunking y construcción/carga del índice.")
    ingest_status = st.empty()

with col2:
    st.subheader("2) Recuperación")
    st.write("Búsqueda del contexto (vector/BM25/híbrido).")
    retr_status = st.empty()

with col3:
    st.subheader("3) Generación")
    st.write("Respuesta usando el LLM local con el contexto recuperado.")
    gen_status = st.empty()

st.divider()

query = st.text_area(" Pregunta", placeholder="Escribe tu pregunta sobre los documentos...", height=90)
ask = st.button("✨ Preguntar")

# Ingesta: build/load
if "index" not in st.session_state or run_ingest:
    with st.spinner("Ingestando / cargando índice..."):
        index = build_or_load_index(cfg, force_rebuild=run_ingest)
        st.session_state["index"] = index
    ingest_status.success("Índice listo ✅")

if ask:
    if not query.strip():
        st.warning("Escribe una pregunta.")
        st.stop()

    index = st.session_state["index"]

    with st.spinner("Recuperando contexto..."):
        ctx = retrieve_context(cfg, index, query)
    retr_status.success(f"Contexto recuperado ✅ (docs: {len(ctx['sources'])})")

    with st.spinner("Generando respuesta..."):
        answer = generate_answer(cfg, query, ctx["context"])
    gen_status.success("Respuesta generada ✅")

    st.subheader("✅ Respuesta")
    st.write(answer)

    with st.expander("📌 Contexto usado (chunks)"):
        st.write(ctx["context"])

    with st.expander("🧾 Fuentes"):
        for s in ctx["sources"]:
            st.markdown(f"- **{s.get('source','(sin nombre)')}** | chunk={s.get('chunk_id','?')}")

