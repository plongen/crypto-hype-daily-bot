import asyncio
import json
from datetime import datetime, timedelta
import os
import requests
import sys

# ================== CONFIG ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY não encontrada no Secrets!")
    sys.exit(1)

def get_prices_and_news():
    try:
        prices = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin,ethereum,solana,xrp,toncoin&vs_currencies=usd&include_24hr_change=true",
            timeout=15
        ).json()
    except:
        prices = {}

    try:
        news = requests.get("https://cryptocurrency.cv/api/news?limit=8", timeout=15).json()
    except:
        news = []
    
    return {"prices": prices, "news": news[:6]}

def generate_summary_with_gemini(market):
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    prompt = f"""Você é um analista crypto brasileiro direto e bem-humorado.
Resuma em português BR o que provavelmente foi hype no crypto ontem ({yesterday_str}).

Preços atuais + variação 24h:
{json.dumps(market['prices'], indent=2)}

Principais notícias recentes:
{json.dumps(market['news'], indent=2)}

Faça:
- 1 tweet principal chamativo (máx 280 caracteres) com emojis
- Uma thread curta de 3-4 tweets explicando os principais narratives.

Tom: empolgado, realista, linguagem de trader brasileiro. Sem hashtags exageradas."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        }, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        print("❌ Erro ao chamar Gemini:", str(e))
        if "429" in str(e):
            print("Rate limit atingido. Tente amanhã.")
        return "Erro ao gerar resumo com IA. Verifique a chave Gemini."

async def main():
    print("🚀 Iniciando Crypto Hype Daily Bot...")
    
    print("📊 Buscando preços e notícias...")
    market = get_prices_and_news()
    
    print("🧠 Gerando resumo com Gemini...")
    summary = generate_summary_with_gemini(market)
    
    print("\n" + "="*50)
    print(summary)
    print("="*50)
    
    # TODO: Adicionar postagem automática depois que estiver estável

if __name__ == "__main__":
    asyncio.run(main())
