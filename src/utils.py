import os
from pathlib import Path

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def list_pdfs(folder: str):
    if not os.path.exists(folder):
        return []
    return [str(Path(folder) / f) for f in os.listdir(folder) if f.lower().endswith(".pdf")]
