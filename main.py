from fetch_trends import get_trending_news
from call_gemini import resumir_em_gemini
# from post_to_twitter import postar_no_x  # Opcional: comente se não quiser o log de erro 403

if __name__ == "__main__":
    print("🚀 Buscando as tendências de hoje...")
    news_items = get_trending_news(max_items=4)
    
    if not news_items:
        print("⚠️ Nenhuma notícia encontrada para processar.")
        exit()

    titulos = ""
    for n in news_items:
        titulos += f"- {n['title']}\n"
    
    print("🤖 Gerando posts com o Gemini...")
    resumo = resumir_em_gemini(titulos)
    
    # Formatação limpa para o terminal
    print("\n" + "="*50)
    print("🔥 CONTEÚDO PARA O @crypto42alpha")
    print("="*50 + "\n")
    
    print(resumo)
    
    print("\n" + "="*50)
    print("✅ Processo finalizado! Copie o texto acima.")
    print("="*50 + "\n")

    # Se quiser manter a tentativa de postagem mesmo sabendo do erro:
    # postar_no_x(resumo)
