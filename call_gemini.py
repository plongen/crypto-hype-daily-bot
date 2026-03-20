import os
import requests
import random

def gemini_gerar_tweet(prompt):
    """Realiza a chamada para a API do Gemini com tratamento de erro básico."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")
    
    # Modelo estável para Março/2026
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 280, 
            "temperature": 0.7  # Aumentado levemente para evitar respostas idênticas
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        r.raise_for_status() # Garante que erros 4xx ou 5xx sejam capturados
        respj = r.json()
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO Gemini]: {str(e)}"

def resumir_em_gemini(titulos):
    """
    Gera 3 posts técnicos e distintos. 
    Implementa Shuffle de notícias para evitar inícios repetitivos.
    """
    # 1. Transformar a string em lista e limpar espaços
    noticias_list = [n.strip() for n in titulos.split('-') if n.strip()]
    
    # 2. Base de estilo comum
    base_style = "English. Max 250 chars. No intros, no quotes. Use cynical researcher tone."

    # --- POST 1: THE TAPE (Trader Persona) ---
    # Foco em Preço e Liquidez. Proibido falar de tecnologia profunda.
    random.shuffle(noticias_list)
    contexto_1 = " | ".join(noticias_list)
    prompt_1 = (
        f"{base_style} Act as a cynical hedge fund trader. Focus ONLY on price action, order flow, "
        f"and liquidity sentiment of these news: {contexto_1}. "
        "DO NOT mention specific protocol names or regulatory bills. Start with a market observation."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (Dev/Infra Persona) ---
    # Foco em Tech/RWA. Proibido falar de preço ou BTC.
    random.shuffle(noticias_list)
    contexto_2 = " | ".join(noticias_list)
    prompt_2 = (
        f"{base_style} Act as a senior protocol engineer. Focus ONLY on tech infra and RWA plumbing "
        f"from these news: {contexto_2}. MANDATORY: Do NOT start with Bitcoin or price. "
        "Start with middleware, settlement layers, or interoperability specs."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (Macro Strategy Persona) ---
    # Foco em Geopolítica e Veredito Final.
    random.shuffle(noticias_list)
    contexto_3 = " | ".join(noticias_list)
    prompt_3 = (
        f"{base_style} Act as a geopolitical strategist. Connect these dots: {contexto_3}. "
        "Focus on sovereign shifts and systemic decay. Avoid repeating words from previous summaries. "
        "MANDATORY: End with a clever strategic insight why '42' is the only logical answer."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    # Retorno limpo para cópia manual
    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
