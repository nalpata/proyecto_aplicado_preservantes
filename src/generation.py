def generate_answer(cfg, question: str, context: str):
    from llama_cpp import Llama

    prompt = f"""Eres un asistente experto. Responde usando SOLO el contexto.
Si no está en el contexto, di: "No encuentro esa información en los documentos".

### CONTEXTO
{context}

### PREGUNTA
{question}

### RESPUESTA
"""

    llm = Llama(
        model_path=cfg.llm_model_path,
        n_ctx=4096,
        n_threads=8,
        verbose=False,
    )

    out = llm(
        prompt,
        temperature=float(cfg.temperature),
        max_tokens=512,
        stop=["###"],
    )
    return out["choices"][0]["text"].strip()
