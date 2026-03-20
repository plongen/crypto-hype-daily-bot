import tweepy, os

def postar_no_x(texto):
    keys = [os.getenv(k) for k in [
        'TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET'
    ]]
    if not all(keys):
        raise Exception("Faltam credenciais do Twitter nas variáveis de ambiente")
    auth = tweepy.OAuth1UserHandler(*keys)
    api = tweepy.API(auth)
    api.update_status(texto)
