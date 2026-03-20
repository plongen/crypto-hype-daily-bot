import os
import requests

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")
    
    # Modelo atualizado para Março/2026
    MODEL_NAME = "gemini-3.1-flash-lite-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 200, # Reduzido para forçar concisão
            "temperature": 0.6      # Menos "criatividade", mais precisão técnica
        }
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO Gemini]: {e}"

def resumir_em_gemini(titulos):
    """
    Gera três posts distintos em inglês para o @crypto42alpha, 
    focando em diferentes camadas do mercado (Preço, Infra e Macro).
    """

    # Instrução mestre: Define o tom cínico, técnico e o limite de caracteres.
    base_instruction = (
        "Write in English. Max 260 characters. Professional, cynical, and ultra-dense. "
        "NO introductory phrases like 'Here is...', NO quotes, NO repetitive hooks. "
        "Directly address the data. Be a high-level crypto researcher."
    )

    # --- POST 1: THE TAPE (Market Dynamics & Price Action) ---
    prompt_tape = (
        f"{base_instruction}\n"
        f"DATA: {titulos}\n"
        "TASK: Analyze the market 'tape' and institutional flow only. "
        "Ignore specific bill names or tech specs. Focus on liquidity, momentum, and volume vibes. "
        "Start with a raw, bold observation about current market behavior."
    )
    post_1 = gemini_gerar_tweet(prompt_tape).strip()

    # --- POST 2: THE PLUMBING (Tech & Infrastructure Alpha) ---
    prompt_plumbing = (
        f"{base_instruction}\n"
        f"DATA: {titulos}\n"
        "TASK: Ignore price/volatility. Focus EXCLUSIVELY on the infrastructure, RWA (Ondo, Centrifuge), "
        "or regulatory 'plumbing' mentioned. Use developer-centric terminology (APIs, smart contracts, "
        "settlement layers). Explain the 'how' behind the news."
    )
    post_2 = gemini_gerar_tweet(prompt_plumbing).strip()

    # --- POST 3: THE DECODING (Geopolitical & Strategic Verdict) ---
    prompt_decoding = (
        f"{base_instruction}\n"
        f"DATA: {titulos}\n"
        "TASK: Connect these dots to a broader geopolitical or macro trend. Give a contrarian take "
        "on what the retail crowd is missing. Be strategic. "
        "MANDATORY: You must end with a clever, organic reference to '42' being the ultimate answer."
    )
    post_3 = gemini_gerar_tweet(prompt_decoding).strip()

    # Retorno formatado para o seu "copia e cola" manual no console
    return (
        f"POST 1 (THE TAPE):\n{post_1}\n\n"
        f"POST 2 (THE PLUMBING):\n{post_2}\n\n"
        f"POST 3 (THE DECODING):\n{post_3}\n"
    )
