import asyncio
import json
from datetime import datetime, timedelta
import os
import requests
from twscrape import API, gather

# ================== CONFIG ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")   # Vamos adicionar no GitHub Secrets
BOT_USERNAME = "SeuBotAqui"                    # Apenas para log

# Queries para capturar o hype de ontem
QUERIES = [
    "crypto OR bitcoin OR btc OR ethereum OR eth OR solana OR sol (hype OR pumping OR narrative OR adoption OR moon OR ai agent) -filter:replies",
    "(memecoin OR $PEPE OR $DOGE OR $HYPE OR $TAO) (pump OR moon OR viral)",
    "crypto news OR adoption OR regulation since:2025-01-01"  # ajuste a data se quiser
]

async def get_yesterday_tweets():
    api = API()
    # Adicione contas se quiser (opcional e mais estável)
    # await api.pool.add_account("user", "pass", "email", "emailpass")
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    all_tweets = []
    
    for q in QUERIES:
        tweets = await gather(api.search(q, limit=30, since=yesterday))
        all_tweets.extend(tweets)
    
    # Remove duplicados e pega os mais relevantes
    unique = {t.id: t for t in all_tweets}
    sorted_tweets = sorted(unique.values(), key=lambda x: x.likeCount + x.retweetCount, reverse=True)[:50]
    
    return [{
        "text": t.rawContent,
        "user": t.user.username,
        "likes": t.likeCount,
        "retweets": t.retweetCount,
        "date": t.date.strftime("%Y-%m-%d")
    } for t in sorted_tweets]

def get_prices_and_news():
    # Preços
    prices = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,xrp&vs_currencies=usd&include_24hr_change=true"
    ).json()
    
    # Notícias free
    news = requests.get("https://cryptocurrency.cv/api/news?limit=8").json()
    
    return {"prices": prices, "news": news[:6]}

def generate_summary_with_gemini(tweets, market):
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    prompt = f"""Você é um analista crypto brasileiro direto, bem-humorado e sem enrolação.
Crie um resumo ATRATIVO em português do Brasil do que foi o HYPE no X ontem ({yesterday_str}).

Dados do mercado:
{json.dumps(market['prices'], indent=2)}

Notícias principais:
{json.dumps(market['news'], indent=2)}

Top tweets / discussões quentes de ontem:
{json.dumps(tweets[:15], indent=2)}

Estrutura:
1. Um tweet principal (máx 280 caracteres) bem chamativo com emojis
2. Uma thread curta (3-5 tweets) explicando os principais narratives do dia.

Tom: empolgado mas realista, use linguagem de trader brasileiro.
Não coloque links nem hashtags demais."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    response = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })
    
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Erro ao gerar resumo. Tente novamente amanhã."

async def main():
    print("🔍 Buscando tweets de ontem...")
    tweets = await get_yesterday_tweets()
    
    print("📊 Pegando preços e notícias...")
    market = get_prices_and_news()
    
    print("🧠 Gerando resumo com IA...")
    summary = generate_summary_with_gemini(tweets, market)
    
    print("\n=== RESUMO GERADO ===\n")
    print(summary)
    
    # Aqui depois adicionamos a postagem (twscrape também permite postar, mas exige conta logada)

if __name__ == "__main__":
    asyncio.run(main())
