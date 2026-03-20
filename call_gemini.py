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
    """Gera o Intel Report com isolamento de dados e layout variado."""
    # Limpeza e embaralhamento das notícias
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]
    if not noticias: 
        return "Insufficient data stream."
    random.shuffle(noticias)

    # ISOLAMENTO DE DADOS: Garante que cada post trate de um assunto único
    split = len(noticias) // 3
    set1 = noticias[:split]
    set2 = noticias[split:split*2]
    set3 = noticias[split*2:]

    base_style = (
        "English. Max 270 chars. Style: Cynical, ultra-dense crypto-macro researcher. "
        "NO hashtags, NO emojis, NO 'Here is'. Use $Tickers. "
        "Focus on causality and hidden risks. Be cold and intellectual."
    )

    # --- GERAÇÃO DOS TEXTOS ---
    post_1 = gemini_gerar_tweet(
        f"{base_style} Analyze the market tape using ONLY: {set1}. "
        "Focus on institutional traps and liquidity theft. Start aggressive."
    ).strip()

    post_2 = gemini_gerar_tweet(
        f"{base_style} Analyze the protocol infrastructure using ONLY: {set2}. "
        "Ignore Bitcoin price. Talk about RWA/L1 settlement rails."
    ).strip()

    post_3 = gemini_gerar_tweet(
        f"{base_style} Provide a strategic macro verdict using ONLY: {set3}. "
        "Connect to sovereign risk. MANDATORY: End with 'Logic dictates 42.'"
    ).strip()

    # --- VARIABILIDADE VISUAL (Anti-Pattern) ---
    headers = [
        "🔥 @crypto42alpha - INTEL REPORT",
        "📡 @crypto42alpha - SIGNAL DETECTED",
        "📊 @crypto42alpha - MACRO DECODING",
        "🧿 @crypto42alpha - THE 42 PROTOCOL"
    ]
    header = random.choice(headers)

    # Seleciona um set de marcadores aleatório
    bullets_set = [
        ("I", "II", "III"),
        ("01", "02", "03"),
        ("[TAPE]", "[PLUMBING]", "[DECODING]"),
        ("● ALPHA", "● INFRA", "● MACRO")
    ]
    b1, b2, b3 = random.choice(bullets_set)

    # Montagem final do relatório
    intel_report = (
        f"{header}\n\n"
        f"{b1}:\n{post_1}\n\n"
        f"{b2}:\n{post_2}\n\n"
        f"{b3}:\n{post_3}\n"
    )

    return intel_report
