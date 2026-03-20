import json
import os
import requests
import sys
from datetime import datetime, timedelta

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada nos Secrets!")
    print("   Vá em Settings → Secrets and variables → Actions e crie GEMINI_API_KEY")
    sys.exit(1)

def get_market_data():
    print("📊 Buscando preços do CoinGecko...")
    prices = {}
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin,ethereum,solana,xrp,toncoin,dogecoin"
            "&vs_currencies=usd&include_24hr_change=true",
            timeout=20
        )
        if r.status_code == 200:
            prices = r.json()
    except Exception as e:
        print("Erro preços:", e)

    print("📰 Buscando notícias...")
    news = []
    try:
        r = requests.get("https://cryptocurrency.cv/api/news?limit=10", timeout=20)
        if r.status_code == 200:
            news = r.json()[:8]
    except Exception as e:
        print("Erro notícias:", e)

    return {"prices": prices, "news": news}

def generate_summary(data):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    # Formata preços de forma bonita
    prices_text = ""
    for coin, info in data["prices"].items():
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0)
        emoji = "📈" if change > 0 else "📉"
        prices_text += f"{coin.upper()}: ${price:,.0f} {emoji} {change:+.1f}%\n"

    # Formata notícias
    news_text = "\n".join([f"- {item.get('title', item.get('description', 'Notícia'))}" 
                           for item in data["news"] if item])

    prompt = f"""Você é um trader crypto brasileiro direto e bem-humorado.
Faça um resumo do hype no crypto de ontem ({yesterday}).

PREÇOS ONTEM:
{prices_text}

NOTÍCIAS / TÓPICOS QUENTES:
{news_text}

Escreva em português BR:
- 1 tweet principal forte e chamativo (máx 280 caracteres) com emojis
- Uma thread curta de 3 a 5 tweets explicando os principais narratives do dia.

Tom: empolgado, realista, linguagem natural de trader. Sem muitas hashtags."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=40)
        resp.raise_for_status()
        result = resp.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("❌ Erro Gemini:", str(e))
        return "Erro ao gerar resumo com IA. Tente novamente amanhã."

def main():
    print("🚀 Crypto Hype Daily Bot Iniciado\n")
    market = get_market_data()
    summary = generate_summary(market)
    
    print("="*75)
    print(summary)
    print("="*75)
    print("\n✅ Resumo gerado com sucesso!")

if __name__ == "__main__":
    main()
