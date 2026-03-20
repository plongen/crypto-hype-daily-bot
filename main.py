import json
import os
import requests
import sys
from datetime import datetime, timedelta

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não está configurada nos Secrets!")
    sys.exit(1)

def get_market_data():
    print("📊 Buscando preços do CoinGecko...")
    try:
        prices = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin,ethereum,solana,xrp,toncoin,dogecoin&vs_currencies=usd&include_24hr_change=true",
            timeout=20
        ).json()
    except Exception as e:
        print("Erro CoinGecko:", e)
        prices = {}

    print("📰 Buscando notícias...")
    try:
        news = requests.get("https://cryptocurrency.cv/api/news?limit=10", timeout=20).json()
    except Exception as e:
        print("Erro News API:", e)
        news = []

    return {"prices": prices, "news": news[:8]}

def generate_hype_summary(data):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    prompt = f"""Você é um trader crypto brasileiro direto e bem-humorado.
Escreva um resumo diário atraente sobre o hype do crypto ontem ({yesterday}).

Preços + variação 24h:
{json.dumps(data['prices'], indent=2)}

Notícias recentes:
{json.dumps([n.get('title', '') for n in data['news']], indent=2)}

Crie:
- 1 tweet principal forte (máx 280 caracteres) com emojis
- Uma thread curta de 3 a 5 tweets explicando os principais narratives / movers / hype do dia.

Tom: empolgado, realista, linguagem natural de trader BR. Sem muitas hashtags."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=40)
        resp.raise_for_status()
        result = resp.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        print("❌ Erro Gemini:", str(e))
        return "Erro ao gerar resumo. Verifique a chave Gemini ou limite de uso."

def main():
    print("🚀 Crypto Hype Daily Bot - Iniciando...\n")
    
    market = get_market_data()
    summary = generate_hype_summary(market)
    
    print("\n" + "="*60)
    print(summary)
    print("="*60)
    print("\n✅ Resumo gerado com sucesso!")

if __name__ == "__main__":
    main()
