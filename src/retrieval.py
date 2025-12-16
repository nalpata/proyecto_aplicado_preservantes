import numpy as np

def _cosine(a, b, eps=1e-9):
    a = a / (np.linalg.norm(a) + eps)
    b = b / (np.linalg.norm(b) + eps)
    return float(np.dot(a, b))

def _embed_texts(texts):
    from sklearn.feature_extraction.text import HashingVectorizer
    vec = HashingVectorizer(n_features=2**12, alternate_sign=False, norm=None)
    X = vec.transform(texts).toarray().astype(np.float32)
    return X

def _bm25_scores(query, docs):
    from rank_bm25 import BM25Okapi
    tokenized = [d.split() for d in docs]
    bm25 = BM25Okapi(tokenized)
    return bm25.get_scores(query.split())

def retrieve_context(cfg, index, query: str):
    chunks = index["chunks"]
    metas = index["metas"]

    if not chunks:
        return {"context": "", "sources": []}

    top_k = cfg.top_k

    if cfg.retrieval_mode in ["vector", "hybrid"]:
        X = _embed_texts(chunks)
        qv = _embed_texts([query])[0]
        sims = np.array([_cosine(qv, X[i]) for i in range(len(chunks))])
    else:
        sims = None

    if cfg.retrieval_mode in ["bm25", "hybrid"]:
        bm = np.array(_bm25_scores(query, chunks), dtype=np.float32)
    else:
        bm = None

    if cfg.retrieval_mode == "vector":
        scores = sims
    elif cfg.retrieval_mode == "bm25":
        scores = bm
    else:
        sims_n = (sims - sims.min()) / (sims.max() - sims.min() + 1e-9)
        bm_n = (bm - bm.min()) / (bm.max() - bm.min() + 1e-9)
        scores = 0.5 * sims_n + 0.5 * bm_n

    idx = np.argsort(scores)[::-1][:top_k]
    selected_chunks = [chunks[i] for i in idx]
    selected_sources = [metas[i] for i in idx]

    context = "\n\n---\n\n".join(selected_chunks)
    return {"context": context, "sources": selected_sources}
