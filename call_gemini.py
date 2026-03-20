import os
import requests
import random

def gemini_gerar_tweet(prompt):
    """Realiza a chamada para a API do Gemini com tratamento de erro e timeout."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Erro: Variável de ambiente GEMINI_API_KEY não encontrada!")
    
    # Modelo estável e rápido para Março/2026
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 300, 
            "temperature": 0.7  # Melhora a variabilidade das respostas
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        respj = r.json()
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO Gemini]: {str(e)}"

def resumir_em_gemini(titulos):
    """
    Gera 3 posts técnicos distintos para o @crypto42alpha.
    Implementa Shuffle de notícias para garantir diversidade de aberturas.
    """
    # Segurança: Verifica se há dados suficientes
    if not titulos or len(titulos) < 20:
        return "Erro: Dados de notícias insuficientes para processar."

    # Transforma a string de títulos em uma lista para embaralhar
    # Assume que os títulos vêm separados por '-' conforme o seu main.py
    noticias_list = [n.strip() for n in titulos.split('-') if n.strip()]
    
    base_style = "English. Max 250 chars. No intros, no quotes. Use cynical, high-level researcher tone."

    # --- POST 1: THE TAPE (Persona: Trader Institucional) ---
    random.shuffle(noticias_list)
    contexto_1 = " | ".join(noticias_list)
    prompt_1 = (
        f"{base_style} Act as a cynical hedge fund trader. Focus ONLY on price action, order flow, "
        f"and liquidity sentiment of these news: {contexto_1}. "
        "DO NOT mention tech protocols. Start with a raw market observation."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # --- POST 2: THE PLUMBING (Persona: Engenheiro de Protocolo) ---
    random.shuffle(noticias_list)
    contexto_2 = " | ".join(noticias_list)
    prompt_2 = (
        f"{base_style} Act as a senior protocol engineer. Focus ONLY on infrastructure and RWA plumbing "
        f"from these news: {contexto_2}. MANDATORY: Do NOT start with price or Bitcoin. "
        "Start with middleware, settlement layers, or interoperability specs."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # --- POST 3: THE DECODING (Persona: Estrategista Geopolítico) ---
    random.shuffle(noticias_list)
    contexto_3 = " | ".join(noticias_list)
    prompt_3 = (
        f"{base_style} Act as a geopolitical strategist. Connect these points to the global stage: {contexto_3}. "
        "Focus on sovereign shifts and systemic decay. Avoid repeating words from previous posts. "
        "MANDATORY: End with a clever strategic insight why '42' is the ultimate answer."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
