def resumir_em_gemini(texto):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Faltando GEMINI_API_KEY no ambiente!")
    MODEL_NAME = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    prompt = (
        "Você é uma IA especialista em tendências CRIPTO e mercados. "
        "Com base nas notícias e dados abaixo, gere uma THREAD do Twitter em português (do Brasil), focando especialmente nos temas QUENTES do momento – como DeFi, IA e criptoativos/padrões/protocolos citados (por exemplo: EC-8004, Ondo, Centrifuge, Chainlink, e outros projetos inquietos ou disruptivos). "
        "Destaque oportunidades, riscos e sinais de hype. "
        "Formate assim:\n\n"
        "Tweet principal:\n<resumo bombástico com emojis e chamada de atenção>\n\n"
        "Thread:\n1. <Tópico importante, detalhado e impactante, de preferência sobre DeFi ou IA>\n"
        "2. <Outro destaque: menção a protocolos, EC-8004, projetos de tokenização, parcerias, on-chain, etc>\n"
        "3. <Aprofundamento com nuances, possíveis riscos ou oportunidades dos temas>\n"
        "4. <Extra: se houver, algo surpreendente do dia>\n\n"
        "Evite links, números de tweet, datas e repetições. Escreva no melhor tom de 'analista cripto antenado'.\n\n"
        f"DADOS PARA ANÁLISE:\n{texto}\n"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1024}
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
