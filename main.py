import json
import os
import requests
import sys
from datetime import datetime, timedelta

# ================== CONFIG ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada!")
    print("   Vá em Settings → Secrets and variables → Actions e crie o secret GEMINI_API_KEY")
    sys.exit(1)

def get_market_data():
    print("📊 Buscando preços...")
    try:
        prices = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin,ethereum,solana,xrp,toncoin,dogecoin"
            "&vs_currencies=usd&include_24hr_change=true",
            timeout=20
        ).json()
    except Exception as e:
        print("Erro ao pegar preços:", e)
        prices = {}

    print("📰 Buscando notícias...")
    try:
        news = requests.get("https://cryptocurrency.cv/api/news?limit=10", timeout=20).json()
    except Exception as e:
        print("Erro ao pegar notícias:", e)
        news = []

    return {"prices": prices, "news": news[:8]}

def generate_summary(data):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    prompt = f"""Você é um trader crypto brasileiro, direto e bem-humorado.
Escreva um resumo diário do hype no crypto de ontem ({yesterday}).

Preços + variação 24h:
{json.dumps(data['prices'], indent=2)}

Notícias recentes:
{json.dumps([n.get('title', n.get('description', '')) for n in data['news']], indent=2)}

Crie em português BR:
- 1 tweet principal chamativo (máx 280 caracteres) com emojis
- Uma thread curta de 3-5 tweets explicando os principais narratives e o que estava em alta.

Tom: empolgado mas realista, linguagem de trader. Sem muitas hashtags."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=40)
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("❌ Erro Gemini:", str(e))
        return "Erro ao gerar resumo com IA. Verifique sua chave Gemini."

def main():
    print("🚀 Crypto Hype Daily Bot Iniciado\n")
    market = get_market_data()
    summary = generate_summary(market)
    
    print("="*70)
    print(summary)
    print("="*70)
    print("\n✅ Resumo gerado com sucesso!")

if __name__ == "__main__":
    main()
