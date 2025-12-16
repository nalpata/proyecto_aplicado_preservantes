from dataclasses import dataclass

@dataclass
class AppConfig:
    data_dir: str = "data/pdfs"
    persist_dir: str = "data/indexes"

    retrieval_mode: str = "hybrid"   # vector | bm25 | hybrid
    top_k: int = 5

    llm_model_path: str = "models/llama.gguf"
    temperature: float = 0.2
