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
    # Instrução global para o Gemini: Inglês, Curto, Denso, Sem introduções.
    instrucao_global = (
        "Write in English. Be concise, technical, and high-impact (Alpha style). "
        "STRICT LIMIT: Max 260 characters per post. Do not include quotes, intros, or options. "
        "Start directly with the content. Use emojis sparingly."
    )

    # Post 1: The Macro/Market Signal
    prompt_1 = (
        f"{instrucao_global}\nCreate a high-hype main tweet about the biggest signal in these news: {titulos}. "
        "Focus on market implications. No hashtags."
    )
    post_1 = gemini_gerar_tweet(prompt_1).strip()

    # Post 2: The Infrastructure/Tech Alpha
    prompt_2 = (
        f"{instrucao_global}\nAnalyze the technical or infrastructure side of these topics: {titulos}. "
        "Mention DeFi, RWA (Ondo/Centrifuge), or Automation. Use technical terms. No hashtags."
    )
    post_2 = gemini_gerar_tweet(prompt_2).strip()

    # Post 3: The Verdict/Future Outlook
    prompt_3 = (
        f"{instrucao_global}\nProvide a final strategic verdict or future outlook based on: {titulos}. "
        "Be bold and engaging for the dev/investor community. End with a 42-related pun. No hashtags."
    )
    post_3 = gemini_gerar_tweet(prompt_3).strip()

    # Retorno limpo para o main.py
    return (
        f"POST 1 (MARKET SIGNAL):\n{post_1}\n\n"
        f"POST 2 (INFRA & TECH):\n{post_2}\n\n"
        f"POST 3 (THE VERDICT):\n{post_3}\n"
    )
