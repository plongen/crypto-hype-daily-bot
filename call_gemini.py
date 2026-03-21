import os
import requests
import random
import json

# --- CONFIGURAÇÕES GERAIS ---
# Usando o modelo flash estável para Março/2026
TEXT_MODEL = "gemini-3.1-flash-lite-preview"

def gemini_gerar_tweet(prompt):
    """Gera o texto denso e cínico para o Intel Report."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 320, 
            "temperature": 0.85 
        }
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
        r.raise_for_status()
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"System error: Node disconnected. {str(e)}"

def resumir_em_gemini(titulos):
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]
    if len(noticias) < 3:
        return "Insufficient data stream. Need at least 3 signals."

    random.shuffle(noticias)

    n = len(noticias)
    set1 = noticias[:n//3]
    set2 = noticias[n//3:(2*n)//3]
    set3 = noticias[(2*n)//3:]

    # Cada post tem uma VOZ diferente — isso quebra o genérico
    prompt_1 = (
        f"You are a cynical ex-Goldman quant who lost faith in all institutions. "
        f"Max 270 chars. No hashtags, no emojis, no intro. Use $Tickers. "
        f"Analyze ONLY this data: {set1}. "
        f"Find the institutional trap hidden in plain sight. Start mid-sentence, no warmup."
    )

    prompt_2 = (
        f"You are a cold protocol archaeologist who reads blockchain settlement data like an autopsy. "
        f"Max 270 chars. No hashtags, no emojis, no intro. Use $Tickers. "
        f"Analyze ONLY this data: {set2}. "
        f"Identify what the infrastructure reveals that prices haven't priced yet. "
        f"Never describe what happened — interpret what it means for who gets hurt next."  # <- linha nova
    )

    prompt_3 = (
        f"You are a sovereign risk analyst who treats crypto as geopolitics by other means. "
        f"Max 270 chars. No hashtags, no emojis, no intro. Use $Tickers. "
        f"Analyze ONLY this data: {set3}. "
        f"Connect to macro power dynamics. End exactly with: 'Logic dictates 42.'"
    )

    post_1 = gemini_gerar_tweet(prompt_1).strip()
    post_2 = gemini_gerar_tweet(prompt_2).strip()
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    headers = [
        "🔥 @crypto42alpha — INTEL REPORT",
        "📡 @crypto42alpha — SIGNAL DETECTED",
        "📊 @crypto42alpha — MACRO DECODING",
        "🧿 @crypto42alpha — THE 42 PROTOCOL"
    ]

    bullets_options = [
        ("I", "II", "III"),
        ("01", "02", "03"),
        ("[TAPE]", "[PLUMBING]", "[VERDICT]"),
        ("● ALPHA", "● INFRA", "● MACRO"),
    ]

    header = random.choice(headers)
    b1, b2, b3 = random.choice(bullets_options)

    return (
        f"{header}\n\n"
        f"{b1}:\n{post_1}\n\n"
        f"{b2}:\n{post_2}\n\n"
        f"{b3}:\n{post_3}\n"
    )

    return intel_report
