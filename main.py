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

    news_text = "\n".join([f"- {item.get('title', 'Notícia')}" for item in data["news"] if item])

    prompt = f"""Você é um analista crypto técnico e direto.
Data: {data_atual}

Preços 24h:
{prices_text}

Notícias recentes:
{news_text}

Gere um resumo diário em português usando exatamente este formato:

C42 ALPHA REPORT | {data_atual}

• On-chain Intel
• Market Narrative
• The 42 Verdict

Use tom técnico, objetivo e sem exageros.
No final coloque sempre:
Resumo diário do hype crypto no X • Feito com IA • Não é conselho financeiro"""

    # === MODELOS TESTADOS EM MARÇO 2026 ===
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-flash-latest"
    ]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            print(f"Tentando modelo: {model}...")
            resp = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.6, "maxOutputTokens": 600}
                },
                timeout=35
            )
            if resp.status_code == 200:
                result = resp.json()
                print(f"✓ Sucesso com modelo {model}")
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"  Falhou com {model} → {resp.status_code}")
        except Exception as e:
            print(f"  Erro com {model}: {str(e)}")
            continue

    return "❌ Todos os modelos do Gemini falharam."

def main():
    print("🚀 Crypto Hype Daily Bot Iniciado\n")
    market = get_market_data()
    summary = generate_summary(market)
    
    print("="*85)
    print(summary)
    print("="*85)
    print("\n✅ Processo finalizado!")

if __name__ == "__main__":
    main()
