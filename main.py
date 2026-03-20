from fetch_trends import get_trending_news
from get_coingecko_data import get_top_coins, get_latest_news
from call_gemini import resumir_em_gemini
from post_to_twitter import postar_no_x
import datetime

if __name__ == "__main__":
    # Pega notícias/trends do CryptoPanic em vez de tweets
    news_items = get_trending_news(max_items=15)
    coins = get_top_coins(5)
    news = get_latest_news(3)

    # Monta o texto base para sumarização
    texto = "Tendências de hoje em crypto:\n"
    texto += "\n".join([f"- {i['title']} ({i['url']})" for i in news_items])[:1200]
    texto += "\n\nCoinGecko Top 5:\n" + ", ".join([f"${c['symbol']} ({c['change_24h']:+.2f}%)" for c in coins])
    texto += "\n\nNotícias rápidas: " + " // ".join(news)

    resumo = resumir_em_gemini(texto)
    postar_no_x(resumo)
