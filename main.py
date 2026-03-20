import os
import requests
import sys
from datetime import datetime, timedelta

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY não encontrada!")
    sys.exit(1)

def get_market_data():
    print("📊 Buscando preços...")
    prices = {}
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin,ethereum,solana,xrp,toncoin,dogecoin"
            "&vs_currencies=usd&include_24hr_change=true",
            timeout=15
        )
        if r.status_code == 200:
            prices = r.json()
            print(f"✓ Preços carregados: {len(prices)} moedas")
    except Exception as e:
        print("Erro preços:", e)

    print("📰 Buscando notícias...")
    news = []
    try:
        r = requests.get("https://cryptocurrency.cv/api/news?limit=10", timeout=15)
        if r.status_code == 200:
            news = r.json()[:8]
            print(f"✓ {len(news)} notícias carregadas")
    except Exception as e:
        print("Erro notícias:", e)

    return {"prices": prices, "news": news}

def generate_summary(data):
    data_atual = datetime.now().strftime("%d.%m.%y")
    
    prices_text = ""
    for coin, info in data["prices"].items():
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0)
        emoji = "▲" if change > 0 else "▼"
        prices_text += f"{coin.upper()}: ${price:,.0f} {emoji} {change:+.1f}%\n"

    news_text = "\n".join([f"- {item.get('title', item.get('description', 'Notícia'))}" 
                          for item in data["news"] if item])

    prompt = f"""Você é um analista crypto técnico e direto.

Data de hoje: {data_atual}

Preços nas últimas 24h:
{prices_text}

Notícias e tópicos quentes do dia:
{news_text}

Crie um relatório no seguinte formato exato:

C42 ALPHA REPORT | {data_atual}

• On-chain Intel
[2-3 linhas com insights relevantes sobre volume, whales, funding rate, open interest ou on-chain activity]

• Market Narrative
[2-3 linhas explicando qual narrativa está dominando o hype no X hoje (AI agents, RWA, memecoins, adoption, regulation, etc)]

• The 42 Verdict
[1 frase curta e objetiva com sua visão do dia]

Use linguagem técnica, objetiva e confiante. Evite emojis demais e palavras como explosivo, insano, louco.
No final, sempre adicione:
Resumo diário do hype crypto no X • Feito com IA • Não é conselho financeiro"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY
    
    try:
        resp = requests.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.65,
                    "maxOutputTokens": 700,
                }
            },
            timeout=40
        )
        resp.raise_for_status()
        result = resp.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Erro Gemini:", str(e))
        return "Erro ao gerar relatório."

def main():
    print("🚀 Crypto Hype Daily Bot Iniciado\n")
    market = get_market_data()
    summary = generate_summary(market)
    
    print("="*90)
    print(summary)
    print("="*90)
    print("\n✅ Processo finalizado!")

if __name__ == "__main__":
    main()
