import json
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
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    prices_text = ""
    for coin, info in data["prices"].items():
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0)
        emoji = "📈" if change > 0 else "📉"
        prices_text += f"{coin.upper()}: ${price:,.0f} {emoji} {change:+.1f}%\n"

    news_text = "\n".join([f"- {item.get('title', 'Notícia')}" 
                          for item in data["news"] if item])

    prompt = f"""Você é um trader crypto brasileiro direto e bem-humorado.
Faça um resumo do que foi hype no crypto ontem ({yesterday}).

PREÇOS:
{prices_text}

NOTÍCIAS / TÓPICOS:
{news_text}

Escreva em português BR:
- 1 tweet principal forte e chamativo (máx 280 caracteres) com emojis
- Uma thread curta de 3 a 5 tweets explicando os principais narratives do dia.

Tom: empolgado, mas realista. Linguagem natural de trader."""

    # === URL CORRIGIDA 2026 ===
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=40)
        resp.raise_for_status()
        result = resp.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Erro Gemini:", str(e))
        return "Erro ao gerar resumo com IA. Verifique a chave ou limite diário."

def main():
    print("🚀 Crypto Hype Daily Bot Iniciado\n")
    market = get_market_data()
    summary = generate_summary(market)
    
    print("="*80)
    print(summary)
    print("="*80)
    print("\n✅ Resumo gerado com sucesso!")

if __name__ == "__main__":
    main()
