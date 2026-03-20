from fetch_trends import get_trending_tweets
from get_coingecko_data import get_top_coins, get_latest_news
from call_gemini import resumir_em_gemini
from post_to_twitter import postar_no_x
import datetime

if __name__ == "__main__":
    hoje = datetime.datetime.utcnow()
    ontem = hoje - datetime.timedelta(days=1)
    keywords = ['crypto', 'bitcoin', 'ethereum', 'hype', 'pumping', 'moon', 'narrative', 'adoption', 'altcoins']
    tweets = get_trending_tweets(keywords, since=ontem.strftime('%Y-%m-%d'), until=hoje.strftime('%Y-%m-%d'), max_tweets=60)
    coins = get_top_coins(5)
    news = get_latest_news(3)

    texto = f"Tweets hype de ontem:\n" + "\n".join([f"- @{t['user']}: {t['content']}" for t in tweets])[:1200]
    texto += "\n\nCoinGecko Top 5 hoje:\n" + ", ".join([f"${c['symbol']} ({c['change_24h']:+.2f}%)" for c in coins])
    texto += "\n\nNotícias rápidas: " + " // ".join(news)

    resumo = resumir_em_gemini(texto)
    postar_no_x(resumo)
