import os
import requests

def resumir_em_gemini(titulos):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    prompt = (
        "Você é um analista cripto que monitora tendências e tecnologia. Gere uma THREAD de Twitter em português (Brasil) com EXATAMENTE o formato abaixo. "
        "Nunca responda com texto corrido, apenas complete os campos pedidos. "
        "Lembre: obrigatoriamente sempre escreva pelo menos 4 tweets, preenchendo tudo.\n\n"
        "Tweet principal:\n<Resumo impactante e chamativo com emojis>\n\n"
        "Thread:\n"
        "1. <Tendência DeFi, IA, EC-8004, Ondo, Centrifuge, Chainlink, etc (em até 250 caracteres)>\n"
        "2. <Outro ponto quente atual (expanda, analise, contextualize)>\n"
        "3. <Insight final, visão ou oportunidade>\n\n"
        "Proibido links ou datas. Seja engajado, linguagem de analista cripto, nunca repita apenas os títulos!\n\n"
        f"As tendências do dia são:\n{titulos}\n"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1500}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao acessar Gemini: {e}")
        return "[ERRO Gemini]"
    print("[DEBUG Gemini] Resposta bruta:", respj)
    if 'candidates' not in respj:
        return "[ERRO na resposta do Gemini: " + str(respj.get('error', 'Sem detalhes')) + "]"
    try:
        texto_saida = respj['candidates'][0]['content']['parts'][0]['text']
        if not texto_saida.strip():
            return "[ERRO: Gemini retornou resposta vazia. Tente de novo!]"
        return texto_saida
    except Exception as e:
        print(f"[ERRO] Estrutura inesperada na resposta Gemini: {e}")
        return "[ERRO: Estrutura inesperada na resposta Gemini]"
