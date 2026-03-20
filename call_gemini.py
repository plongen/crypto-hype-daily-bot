import requests
import os

def resumir_em_gemini(texto):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")
    # Modelo recomendado p/ março de 2026:
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = (
        "Você é um bot especialista em notícias de criptomoedas. Resuma as tendências abaixo "
        "como um fio de Twitter, começando com um tweet principal chamativo, seguido de pelo menos dois tweets "
        "detalhando destaques importantes. Use português brasileiro, adicione emojis e não coloque links.\n\n"
        "Notícias e tópicos:\n"
        f"{texto}\n\n"
        "Formato esperado:\n"
        "Tweet principal:\n<texto>\n\nThread:\n1. <texto>\n2. <texto>\n"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 768}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao acessar Gemini: {e}")
        return "[ERRO: Falcon Gemini request]"
    print("[DEBUG Gemini] Resposta bruta:", respj)  # Sempre printa a resposta crua para facilitar ajuste.
    if 'candidates' not in respj:
        return "[ERRO na resposta do Gemini: " + str(respj.get('error', 'Sem detalhes')) + "]"
    try:
        texto_saida = respj['candidates'][0]['content']['parts'][0]['text']
        # Se vier vazio, avisa e não deixa seguir em branco
        if not texto_saida.strip():
            return "[ERRO: Gemini retornou resposta vazia. Tente de novo!]"
        return texto_saida
    except Exception as e:
        print(f"[ERRO] Estrutura inesperada na resposta Gemini: {e}")
        return "[ERRO: Estrutura inesperada na resposta Gemini]"
