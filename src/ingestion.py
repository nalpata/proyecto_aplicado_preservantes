import os
import pickle
from pathlib import Path
from src.utils import ensure_dir, list_pdfs

def chunk_text(text: str, chunk_size=900, overlap=150):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+chunk_size])
        i += chunk_size - overlap
    return chunks

def read_pdf_text(pdf_path: str):
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    pages = [page.get_text("text") for page in doc]
    return "\n".join(pages)

def build_or_load_index(cfg, force_rebuild=False):
    ensure_dir(cfg.persist_dir)
    index_path = Path(cfg.persist_dir) / "index.pkl"

    if index_path.exists() and not force_rebuild:
        with open(index_path, "rb") as f:
            return pickle.load(f)

    pdfs = list_pdfs(cfg.data_dir)
    if not pdfs:
        index = {"chunks": [], "metas": []}
        with open(index_path, "wb") as f:
            pickle.dump(index, f)
        return index

    chunks, metas = [], []
    for p in pdfs:
        text = read_pdf_text(p)
        cks = chunk_text(text)
        for j, ck in enumerate(cks):
            chunks.append(ck)
            metas.append({"source": os.path.basename(p), "chunk_id": j})

    index = {"chunks": chunks, "metas": metas}
    with open(index_path, "wb") as f:
        pickle.dump(index, f)

    return index
