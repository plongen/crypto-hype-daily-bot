import requests
import os

def get_trending_news(max_items=10):
    api_key = os.environ.get('CRYPTOPANIC_API_KEY')
    if not api_key:
        raise Exception("Faltando CRYPTOPANIC_API_KEY no ambiente")
    url = f'https://cryptopanic.com/api/developer/v2/posts/?auth_token={api_key}'
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Erro HTTP {resp.status_code} na requisição CryptoPanic: {resp.text}")
        data = resp.json()
    except Exception as e:
        print(f"[ERRO] Falha ao acessar CryptoPanic: {e}")
        return []
    items = []
    for item in data.get("results", [])[:max_items]:
        title = item.get("title", "")
        description = item.get("description", "")
        if title:
            items.append({"title": title, "description": description})
    return items
