import requests
import os

def resumir_em_gemini(texto):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")
    # Use o modelo mais recente disponível. "gemini-2.5-flash" é estável na maioria dos casos.
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = (
        "Resuma o seguinte em português, estilo humano, tweetável e com emojis. "
        "Converta em um tweet principal e uma thread curta e informativa (se possível), sem links, bem natural:"
        "\n\n" + texto
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 512}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao acessar Gemini: {e}")
        return "[ERRO: Falcon Gemini request]"

    # Debug: imprime o JSON bruto se falhar
    if 'candidates' not in respj:
        print("[DEBUG] Resposta bruta da Gemini API:", respj)
        return "[ERRO na resposta do Gemini: " + str(respj.get('error', 'Sem detalhes')) + "]"
    try:
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"[ERRO] Estrutura inesperada na resposta Gemini: {e}")
        print("[DEBUG] Resposta bruta da Gemini API:", respj)
        return "[ERRO: Estrutura inesperada na resposta Gemini]"
