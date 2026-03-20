import os
import requests
import random
import json

# --- CONFIGURAÇÕES GERAIS ---
# Usando o modelo flash estável para Março/2026
TEXT_MODEL = "gemini-3.1-flash-lite-preview"
IMAGE_MODEL = "gemini-3-flash-image" # Nano Banana 2

def gemini_gerar_tweet(prompt):
    """Gera o texto denso e cínico para o Intel Report."""
    api_key = os.environ.get('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 320, 
            "temperature": 0.85 # Alta para evitar clichês
        }
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
        r.raise_for_status()
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "System error: Node disconnected."

def gemini_gerar_imagem(intel_report_text):
    """
    Gera uma imagem 'Dark Macro Terminal' baseada no resumo do Intel Report.
    A imagem é otimizada para o feed do X (16:9).
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    # Endpoint específico para geração de imagem
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:generateImage?key={api_key}"
    
    # Cria o prompt visual baseado no texto gerado
    visual_prompt = (
        f"A cinematic, ultra-detailed image for a crypto-macro analyst. Style: Dark, dystopian, "
        f"high-tech Bloomberg Terminal screen. Focus: Overlapping data visualization, green holographic "
        f"graphs, stylized tickers ($BTC, $SOL, $ETH) and abstract liquidity flow patterns. "
        f"NO text visible on screen, just dense symbols. A subtle central motif should represent "
        f"a stylized '42' or a 'key' breaking a digital chain. The mood must be cynical and professional, "
        f"set in a shadowy, futuristic Wall Street war room. Otimizado para X, ratio 16:9."
    )
    
    payload = {
        "requests": [{
            "image_prompt": visual_prompt,
            "aspect_ratio": "16:9" # Formato X
        }]
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
        r.raise_for_status()
        respj = r.json()
        
        # A imagem vem codificada em Base64
        image_base64 = respj['image_bytes'][0]['base64']
        
        # Salva a imagem localmente no GitHub Action
        with open("daily_intel.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
        print("🖼️ daily_intel.png gerada com sucesso!")
        return "daily_intel.png"
    
    except Exception as e:
        print(f"[ERRO Imagem]: {str(e)}")
        return None

def resumir_em_gemini(titulos):
    """Gera o Intel Report e a imagem de acompanhamento."""
    # Limpeza e embaralhamento das notícias
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]
    if not noticias: return "Insufficient data."
    random.shuffle(noticias)

    # ISOLAMENTO DE DADOS: Cada post recebe um set diferente de notícias
    split = len(noticias) // 3
    set1 = noticias[:split]
    set2 = noticias[split:split*2]
    set3 = noticias[split*2:]

    base_style = (
        "English. Max 270 chars. Style: Cynical, ultra-dense crypto-macro researcher. "
        "NO hashtags, NO emojis, NO 'Here is'. Use $Tickers. "
        "Focus on causality and hidden risks. Be cold and intellectual."
    )

    # --- POST I: THE TAPE (Market Flow) ---
    prompt_1 = (f"{base_style} Analyze the market tape using ONLY: {set1}. "
                "Focus on institutional traps and liquidity theft. Start aggressive.")
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST II: THE PLUMBING (Tech/Infra) ---
    prompt_2 = (f"{base_style} Analyze the protocol infrastructure using ONLY: {set2}. "
                "Ignore Bitcoin price. Talk about RWA/L1 settlement rails.")
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST III: THE DECODING (Macro/Verdict) ---
    prompt_3 = (f"{base_style} Provide a strategic macro verdict using ONLY: {set3}. "
                "Connect to sovereign risk. MANDATORY: End with 'Logic dictates 42.'")
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    intel_report = (
        f"🔥 @crypto42alpha - INTEL REPORT\n\n"
        f"I (THE TAPE):\n{post_1}\n\n"
        f"II (THE PLUMBING):\n{post_2}\n\n"
        f"III (THE DECODING):\n{post_3}\n"
    )

    # GERA A IMAGEM baseada no resumo (Post III)
    gemini_gerar_imagem(post_3)

    return intel_report
