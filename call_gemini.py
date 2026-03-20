import requests
import os

def resumir_em_gemini(texto):
    api_key = os.environ.get('GEMINI_API_KEY')  # Defina nas secrets
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = (
        "Resuma o seguinte em português, estilo humano, tweetável e com emojis. "
        "Faça um tweet principal e uma thread curta, tudo bem natural:"
        "\n\n" + texto
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 512}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    return r.json()['candidates'][0]['content']['parts'][0]['text']
