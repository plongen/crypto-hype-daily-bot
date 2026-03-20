import requests
import os

def get_trending_news(max_items=20):
    api_key = os.environ.get('CRYPTOPANIC_API_KEY')
    if not api_key:
        raise Exception("Faltando CRYPTOPANIC_API_KEY no ambiente")
    url = f'https://cryptopanic.com/api/developer/v2/posts/?auth_token={api_key}'
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Erro HTTP {resp.status_code} na requisição CryptoPanic: {resp.text}")
    try:
        data = resp.json()
    except Exception:
        raise Exception(f"Resposta inesperada da API CryptoPanic:\n{resp.text}")

    items = []
    for item in data.get("results", [])[:max_items]:
        title = item.get("title", "")
        description = item.get("description", "")
        # Adapte aqui o texto que será passado para a IA (pode incluir description)
        if description:
            items.append({"title": title, "description": description})
        else:
            items.append({"title": title})
    return items
