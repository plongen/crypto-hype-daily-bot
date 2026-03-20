from fetch_trends import get_trending_news
from get_coingecko_data import get_top_coins
from call_gemini import resumir_em_gemini
from post_to_twitter import postar_no_x

if __name__ == "__main__":
    news_items = get_trending_news(max_items=15)
    coins = get_top_coins(5)

    texto = "Tendências de hoje em crypto:\n"
    for n in news_items:
        if "description" in n and n["description"]:
            texto += f"- {n['title']}: {n['description']}\n"
        else:
            texto += f"- {n['title']}\n"
    texto += "\nCoinGecko Top 5 hoje:\n"
    texto += ", ".join([f"${c['symbol']} ({c['change_24h']:+.2f}%)" for c in coins])

    resumo = resumir_em_gemini(texto)
    print("\n==== TEXTO GERADO PELO GEMINI PARA POSTAR ====\n")
    print(resumo)
    print("\n==============================================\n")

    postar_no_x(resumo)
