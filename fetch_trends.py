import requests
import os

def get_trending_news(max_items=20):
    api_key = os.environ.get('CRYPTOPANIC_API_KEY')
    if not api_key:
        raise Exception("Faltando CRYPTOPANIC_API_KEY no ambiente")
    url = f'https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&public=true'
    r = requests.get(url, timeout=10).json()
    # Extrai título/hype e url
    return [{"title": item["title"], "url": item["url"]} for item in r.get("results", [])[:max_items]]

