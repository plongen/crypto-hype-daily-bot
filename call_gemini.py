import os
import requests
import random

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 280, "temperature": 0.8} # Temp maior para variar o vocabulário
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Error generating content."

def resumir_em_gemini(titulos):
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 5]
    random.shuffle(noticias)

    # Dividimos as notícias em 3 grupos para garantir que os posts sejam diferentes
    # Se tiver pouca notícia, a gente repete, mas a ordem garante o foco.
    grupo1 = noticias[:min(3, len(noticias))]
    grupo2 = noticias[min(3, len(noticias)):min(6, len(noticias))]
    grupo3 = noticias[min(6, len(noticias)):] or noticias[:2] # Fallback se tiver poucas

    base_style = "English. Max 240 chars. Bloomberg Terminal style. Cynical. Use $Tickers."

    # --- POST 1: MARKET FLOW (Somente Grupo 1) ---
    prompt_1 = (
        f"{base_style} ANALYZE ONLY THESE: {grupo1}. "
        "FORMAT: [SIGNAL]: [Ticker/Fact] | [TARGET]: [Level] | [VIBE]: [Short comment]. "
        "Focus on price/volume only."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: TECH/INFRA (Somente Grupo 2) ---
    prompt_2 = (
        f"{base_style} ANALYZE ONLY THESE: {grupo2}. "
        "FORMAT: [INFRA]: [Protocol] | [EDGE]: [Tech Spec] | [RISK]: [Failure point]. "
        "No Bitcoin here. Focus on L1/L2/RWA."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: MACRO/VERDICT (Somente Grupo 3) ---
    prompt_3 = (
        f"{base_style} ANALYZE ONLY THESE: {grupo3}. "
        "FORMAT: [MACRO]: [Trend] | [DECAY]: [Systemic flaw]. "
        "MANDATORY END: 'Logic dictates 42.' (Nothing else)."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"POST 1 (MARKET FLOW):\n{post_1}\n\n"
        f"POST 2 (TECH/INFRA):\n{post_2}\n\n"
        f"POST 3 (MACRO VERDICT):\n{post_3}\n"
    )
