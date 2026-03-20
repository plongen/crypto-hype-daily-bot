import os
import requests
import random

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 300, 
            "temperature": 0.85 # Temperatura alta para evitar frases clichês
        }
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "System error: Node disconnected."

def resumir_em_gemini(titulos):
    # Limpeza e embaralhamento das notícias
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]
    random.shuffle(noticias)

    # ISOLAMENTO DE DADOS: Cada post recebe um set diferente de notícias
    # Isso impede fisicamente a repetição de tópicos entre os posts.
    split = len(noticias) // 3
    set1 = noticias[:split]
    set2 = noticias[split:split*2]
    set3 = noticias[split*2:]

    # Instrução de Estilo: O "Cínico de Wall Street"
    base_style = (
        "English. Max 260 chars. Style: Cynical, ultra-dense crypto-macro researcher. "
        "NO hashtags, NO emojis, NO 'Here is'. Use $Tickers. "
        "Focus on causality and hidden risks. Be cold and intellectual."
    )

    # --- POST 1: THE TAPE (Market Flow) ---
    prompt_1 = (
        f"{base_style} Analyze the market tape using ONLY: {set1}. "
        "Focus on institutional traps, liquidity theft, and volume anomalies. "
        "Start with a direct, aggressive observation."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (Tech/Infra) ---
    prompt_2 = (
        f"{base_style} Analyze the protocol infrastructure using ONLY: {set2}. "
        "Focus on L1/L2 wars, RWA settlement, and middleware decay. "
        "Ignore Bitcoin price. Talk about the 'pipes' of the system."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (Macro/Verdict) ---
    prompt_3 = (
        f"{base_style} Provide a strategic macro verdict using ONLY: {set3}. "
        "Connect these points to sovereign risk or systemic collapse. "
        "Final sentence must be: 'Logic dictates 42.' (Strictly that)."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"🔥 @crypto42alpha - INTEL REPORT\n\n"
        f"I (THE TAPE):\n{post_1}\n\n"
        f"II (THE PLUMBING):\n{post_2}\n\n"
        f"III (THE DECODING):\n{post_3}\n"
    )
