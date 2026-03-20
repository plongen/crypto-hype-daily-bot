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
        "Você é um analista cripto que monitora tendências e tecnologia. "
        "Com base nos assuntos abaixo, escreva uma thread de Twitter em português (Brasil) usando este formato:\n\n"
        "Tweet principal:\n<Resumo impactante e chamativo com emojis>\n"
        "Thread:\n"
        "1. <Tendência destaque: DeFi, IA, EC-8004, Ondo, Centrifuge, Chainlink, etc>\n"
        "2. <Outro ponto quente do momento (expanda, analise e contextualize algum projeto ou sinal narrativo)>\n"
        "3. <Análise extra: oportunidade/riscos, hype, algo relevante para investidores atentos>\n\n"
        "Regras: SEM links e SEM datas. Nunca repita títulos. Sempre escreva pelo menos 3 tweets completos! Seja engajado e use linguagem cripto de analista. Os assuntos para análise são:\n\n"
        f"{titulos}\n"
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
