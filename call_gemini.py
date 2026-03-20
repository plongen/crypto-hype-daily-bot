import os
import requests

def gemini_gerar_tweet(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 520}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        respj = r.json()
    except Exception as e:
        return f"[ERRO Gemini]: {e}"
    if 'candidates' not in respj:
        return "[ERRO Gemini]: " + str(respj.get('error', 'Sem detalhes'))
    try:
        return respj['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"[ERRO Gemini]: {e}"

def resumir_em_gemini(titulos):
    # Tweet principal:
    prompt_principal = (
        "Crie um tweet principal, chamativo, curto (máx. 250 caracteres), "
        "em português (Brasil), cheio de hype e com emojis, sobre os temas:\n"
        f"{titulos}\n"
        "Não inclua links, datas ou hashtags."
    )
    tweet_principal = gemini_gerar_tweet(prompt_principal).strip()

    # Thread 1
    prompt_1 = (
        "Crie o primeiro tweet de uma thread, em português (Brasil), detalhando tendências ou fatos quentes dos temas: "
        f"{titulos}\n"
        "Foque em DeFi, IA, EC-8004, Ondo, Centrifuge, Chainlink, ou protocolo em alta. Seja claro e use emojis, máximo 250 caracteres."
    )
    tweet_1 = gemini_gerar_tweet(prompt_1).strip()

    # Thread 2
    prompt_2 = (
        "Crie o segundo tweet de uma thread, em português (Brasil), trazendo outro destaque relevante dos temas: "
        f"{titulos}\n"
        "Mostre análise, novidade ou alerta do dia. Use emojis, máximo 250 caracteres."
    )
    tweet_2 = gemini_gerar_tweet(prompt_2).strip()

    # Thread 3
    prompt_3 = (
        "Crie o terceiro tweet de uma thread, em português (Brasil), trazendo um insight final, visão de risco ou oportunidade ligado aos temas: "
        f"{titulos}\n"
        "Seja engajado, feche a thread animando a comunidade. Emojis, até 250 caracteres."
    )
    tweet_3 = gemini_gerar_tweet(prompt_3).strip()

    # Junta tudo
    return (
        f"Tweet principal:\n{tweet_principal}\n\n"
        f"Thread:\n1. {tweet_1}\n2. {tweet_2}\n3. {tweet_3}\n"
    )
