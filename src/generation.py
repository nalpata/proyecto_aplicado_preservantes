# src/generation.py

from typing import Any, Optional


def _get_cfg_value(cfg: Any, key: str, default: Any = None) -> Any:
    """
    Soporta cfg como objeto (atributos) o como dict.
    """
    if cfg is None:
        return default
    # objeto con atributos
    if hasattr(cfg, key):
        val = getattr(cfg, key)
        return default if val is None else val
    # dict-like
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return default


def generate_answer(cfg: Any, query: str, context: str) -> str:
    """
    Generación de respuesta.
    - Usa llama-cpp-python si está disponible (generación real con GGUF).
    - Si falla por cualquier motivo, retorna fallback estable (no rompe la app).
    """

    # Resolver parámetros de configuración (compatibles con tu app.py)
    model_path: Optional[str] = (
        _get_cfg_value(cfg, "llm_model_path", None)
        or _get_cfg_value(cfg, "model_path", None)
    )

    n_ctx: int = int(_get_cfg_value(cfg, "n_ctx", 2048))
    n_threads: int = int(_get_cfg_value(cfg, "n_threads", 4))
    max_tokens: int = int(_get_cfg_value(cfg, "max_tokens", 256))

    # Normalizar entradas
    query = (query or "").strip()
    context = (context or "").strip()

    if not query:
        return "Por favor escribe una pregunta."

    if not context:
        return (
            "No encontré contexto relevante en los documentos para esa pregunta. "
            "Prueba reformulando la pregunta o ajustando los parámetros de recuperación (top_k)."
        )

    # Intentar generación real
    try:
        from llama_cpp import Llama  # proviene de llama-cpp-python

        if not model_path:
            return (
                "No está configurada la ruta del modelo GGUF. "
                "Verifica `cfg.llm_model_path` en la configuración."
            )

        llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
        )

        prompt = f"""Eres un asistente experto en preservantes.
Si la respuesta no está en el contexto, di: "No encontré esa información en los documentos".

Contexto:
{context}

Pregunta:
{query}

Respuesta:"""

        out = llm(prompt, max_tokens=max_tokens)
        text = out["choices"][0]["text"].strip()
        return text if text else "No encontré esa información en los documentos."

    except Exception:
        # Fallback estable para entrega (si algo falla con el LLM)
        # (Ej: modelo no encontrado, error de carga, etc.)
        return (
            "⚠️ Modo fallback: no fue posible ejecutar el LLM local en este entorno.\n\n"
            "Aun así, la recuperación (RAG) encontró contexto relevante. Aquí tienes un extracto:\n\n"
            f"{context[:1200]}..."
        )
