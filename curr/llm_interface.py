import ollama


# ============================================================
# OLLAMA INTERFACE
# ============================================================
def ollama_chat(prompt: str, model="llama3.1", temperature: float = 0.9):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"LLM error: {e}")
        return "Get Drunk"  # fallback

