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

import base64

def gemini_gerar_imagem(intel_report_text):
    """
    Versão corrigida para o endpoint de imagem.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    # Ajuste do modelo para a versão de produção estável
    MODEL_IMG = "gemini-3-flash-image" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IMG}:predict?key={api_key}"
    
    visual_prompt = (
        "Ultra-detailed cinematic 16:9 image. A dark, futuristic Bloomberg Terminal "
        "in a shadowy war room. Dystopian crypto-macro data visualizations, "
        "holographic charts, glowing tickers like $BTC and $ETH. "
        "Cyberpunk aesthetic, high contrast, professional cynical mood. No text."
    )
    
    # Estrutura de payload para o modelo de imagem (Vertex/AI Studio style)
    payload = {
        "instances": [{"prompt": visual_prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }
    
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
        r.raise_for_status()
        respj = r.json()
        
        # A resposta de imagem geralmente vem em 'predictions'
        image_base64 = respj['predictions'][0]['bytesBase64Encoded']
        
        with open("daily_intel.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
        
        print("🖼️ Imagem daily_intel.png gerada com sucesso!")
        return "daily_intel.png"
    except Exception as e:
        # Se falhar, o bot continua apenas com o texto para não travar o processo
        print(f"⚠️ Falha na imagem (Bot segue apenas com texto): {e}")
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
