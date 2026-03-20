from fetch_trends import get_trending_news
from call_gemini import resumir_em_gemini
from post_to_twitter import postar_no_x

if __name__ == "__main__":
    news_items = get_trending_news(max_items=4)
    titulos = ""
    for n in news_items:
        titulos += f"- {n['title']}\n"
    resumo = resumir_em_gemini(titulos)
    print("\n==== TEXTO GERADO PELO GEMINI PARA POSTAR ====\n")
    print(resumo)
    print("\n==============================================\n")
    postar_no_x(resumo)
