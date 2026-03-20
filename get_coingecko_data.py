import requests

def get_top_coins(n=5):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': n,
        'page': 1
    }
    data = requests.get(url, params=params, timeout=10).json()
    return [{
        'symbol': coin['symbol'].upper(),
        'name': coin['name'],
        'price': coin['current_price'],
        'change_24h': coin['price_change_percentage_24h'],
    } for coin in data]

def get_latest_news(n=3):
    url = 'https://api.coingecko.com/api/v3/status_updates'
    news = requests.get(url, timeout=10).json()
    return [x['description'] for x in news['status_updates'][:n]]
