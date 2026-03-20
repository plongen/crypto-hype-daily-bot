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
    
    # Nova Instrução: Terminal de Dados. Proibido conectivos gramaticais longos.
    base_style = (
        "English. Max 240 chars. Style: Bloomberg Terminal / Professional Quant. "
        "Use Tickers ($BTC, $SOL). No 'In conclusion', no 'If this happens'. "
        "Structure: [SIGNAL] vs [NOISE] or [DATA POINT] -> [IMPACT]."
    )

    # --- POST 1: THE TAPE (Focus: Flow & Liquidity) ---
    random.shuffle(noticias_list)
    ctx1 = " | ".join(noticias_list)
    prompt_1 = (
        f"{base_style} Identify the primary LIQUIDITY SIGNAL in these news: {ctx1}. "
        "Format: SIGNAL: [Fact] | TARGET: [Price/Level] | VIBE: [Cynical Comment]. "
        "Example: SIGNAL: $BTC spot absorption | TARGET: $72k | VIBE: Retail is sleeping."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (Focus: Infrastructure) ---
    random.shuffle(noticias_list)
    ctx2 = " | ".join(noticias_list)
    prompt_2 = (
        f"{base_style} Identify the structural ALPHA in: {ctx2}. "
        "Format: INFRA: [Protocol] | EDGE: [Technical Change] | RISK: [Failure point]. "
        "MANDATORY: Do not start with Bitcoin. Focus on $DOT, $CELO or $SOL specs."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (Focus: Macro/Sovereign) ---
    random.shuffle(noticias_list)
    ctx3 = " | ".join(noticias_list)
    prompt_3 = (
        f"{base_style} Decode the macro rot: {ctx3}. "
        "Format: MACRO: [Trend] | DECAY: [What is failing] | VERDICT: 42. "
        "Be short. Be aggressive. No fluff."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
