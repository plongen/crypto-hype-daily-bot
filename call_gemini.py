import os
import requests
import random
import json
import time

# --- CONFIGURAÇÕES GERAIS ---
TEXT_MODEL = "gemini-3.1-flash-lite-preview"

def gemini_gerar_tweet(prompt, retries=2):
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

    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
            r.raise_for_status()
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            if attempt < retries:
                time.sleep(3)
                continue
            return f"System error: Node disconnected. {str(e)}"

def resumir_em_gemini(titulos):
    """Gera o Intel Report com isolamento de dados e layout variado."""
    # Garante que temos uma lista limpa
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]
    
    if len(noticias) < 3:
        return "Insufficient data stream for full analysis."
    
    random.shuffle(noticias)

    # Divisão segura dos sets de notícias
    n = len(noticias)
    set1 = noticias[:max(1, n//3)]
    set2 = noticias[n//3:(2*n)//3]
    set3 = noticias[(2*n)//3:]

    # --- Chamadas para o Gemini ---
    post_1 = gemini_gerar_tweet(
        f"You are a cynical ex-Goldman quant. Max 270 chars. No hashtags/emojis. "
        f"Analyze ONLY: {set1}. Find the institutional trap. "
        f"Start with a verb or number. Output ONLY analysis."
    ).strip()

    post_2 = gemini_gerar_tweet(
        f"You are a protocol archaeologist. Max 270 chars. No hashtags/emojis. "
        f"Analyze ONLY: {set2}. Interpret what the infra reveals. "
        f"FORBIDDEN: liquidity, liquidation, exit. Output ONLY analysis."
    ).strip()

    post_3 = gemini_gerar_tweet(
        f"You are a sovereign risk analyst. Max 270 chars. No hashtags/emojis. "
        f"Analyze ONLY: {set3}. Connect to macro power. "
        f"FORBIDDEN: liquidity, liquidation, institutional. "
        f"End with: 'Logic dictates 42.' Output ONLY analysis."
    ).strip()

    # --- FIXED: Post 4 - The Literary Echo (Now in English) ---
    post_4 = gemini_gerar_tweet(
        f"Select a brief, devastating quote from a famous author (e.g., Nietzsche, Bukowski, Orwell, Kafka) "
        f"that reflects the futility, greed, or the struggle for autonomy in these news: {noticias[:3]}. "
        f"The quote MUST be in English. "
        f"Format: 'Quote' — Author. "
        f"Max 200 chars. No intro, no emojis. Output ONLY the quote and author."
    ).strip()

    # --- UI / Formatação ---
    headers = [
        "🔥 @crypto42alpha - INTEL REPORT",
        "📡 @crypto42alpha - SIGNAL DETECTED",
        "📊 @crypto42alpha - MACRO DECODING",
        "🧿 @crypto42alpha - THE 42 PROTOCOL"
    ]
    
    bullets_set = [
        ("I", "II", "III", "IV"),
        ("01", "02", "03", "04"),
        ("[TAPE]", "[PLUMBING]", "[DECODING]", "[ECHO]"),
        ("● ALPHA", "● INFRA", "● MACRO", "● VOX")
    ]
    
    header = random.choice(headers)
    b1, b2, b3, b4 = random.choice(bullets_set)

    return (
        f"{header}\n\n"
        f"{b1}:\n{post_1}\n\n"
        f"{b2}:\n{post_2}\n\n"
        f"{b3}:\n{post_3}\n\n"
        f"{b4}:\n{post_4}"
    )
