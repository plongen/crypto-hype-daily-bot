import os
import requests

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")
    
    # Modelo atualizado para Março/2026
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 200, # Reduzido para forçar concisão
            "temperature": 0.6      # Menos "criatividade", mais precisão técnica
        }
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO Gemini]: {e}"

def resumir_em_gemini(titulos):
    # Base comum de restrição
    base = "English. Max 255 chars. No intros, no quotes. Be cynical and ultra-dense."

    # --- POST 1: THE TAPE (The Degenerate Trader) ---
    # Foco em: Candles, Volume, Liquidity, Order flow.
    prompt_1 = (
        f"{base} Act as a cynical institutional trader. Focus ONLY on price action and 'the tape' from: {titulos}. "
        "Use terms like: order flow, distribution, liquidity sweeps, funding rates. "
        "DO NOT mention specific company names or tech protocols."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (The Core Dev) ---
    # Foco em: Smart Contracts, L1/L2, APIs, Settlement, RWA.
    # Bloqueamos palavras de preço para forçar o lado técnico.
    prompt_2 = (
        f"{base} Act as a senior protocol engineer. Focus ONLY on the tech and infrastructure from: {titulos}. "
        "Use terms like: settlement layer, L1/L2, middleware, RWA tokenization, interoperability. "
        "DO NOT mention price, BTC value, or 'market sentiment'. Focus on the 'how'."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (The Macro Philosopher) ---
    # Foco em: Geopolitics, Petrodollar, The 'Big Picture', 42.
    # Bloqueamos o vocabulário dos posts anteriores.
    prompt_3 = (
        f"{base} Act as a geopolitical strategist. Connect these dots to the global stage: {titulos}. "
        "Focus on: petrodollars, sovereignty, macro-economic shifts, or systemic rot. "
        "DO NOT repeat words like 'liquidity' or 'accumulation'. "
        "MANDATORY: End with a clever, deep-thought reference to 42 being the answer."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
