import os
import requests
import random

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY!")
    
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 280, 
            "temperature": 0.5 # Menor temperatura = mais foco em fatos, menos em "poesia"
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        respj = r.json()
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO]: {str(e)}"

def resumir_em_gemini(titulos):
    if not titulos or len(titulos) < 20:
        return "Insufficient data."

    noticias_list = [n.strip() for n in titulos.split('-') if n.strip()]
    
    # Instrução Anti-Grok: Foco em lógica, métricas e tickers.
    base_style = (
        "English. Max 240 chars. Be a cold, data-driven quant. "
        "Use specific tickers ($BTC, $SOL, $CELO). "
        "NO adjectives like 'desperate', 'pathetic', or 'amazing'. "
        "Focus on causality: If A happens, B is the result."
    )

    # --- POST 1: THE TAPE (Quant/Flow) ---
    random.shuffle(noticias_list)
    ctx1 = " | ".join(noticias_list)
    prompt_1 = (
        f"{base_style} Analyze market flow: {ctx1}. "
        "Focus on spot vs futures divergence or liquidity clusters. "
        "Start with a raw data point. No hashtags."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (Tech/Settlement) ---
    random.shuffle(noticias_list)
    ctx2 = " | ".join(noticias_list)
    prompt_2 = (
        f"{base_style} Analyze infrastructure: {ctx2}. "
        "Identify specific protocol changes, RWA yields, or bridge TVL. "
        "DO NOT start with Bitcoin. Focus on the settlement layer specs."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (Strategic Alpha) ---
    random.shuffle(noticias_list)
    ctx3 = " | ".join(noticias_list)
    prompt_3 = (
        f"{base_style} Provide a strategic verdict on: {ctx3}. "
        "Link news to macro sovereign shifts. Avoid generic buzzwords. "
        "Final sentence MUST be: 'Logic dictates 42.' (Nothing more)."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
