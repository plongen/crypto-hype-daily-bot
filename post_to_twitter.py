import tweepy
import os

def postar_no_x(texto):
    keys = ["TWITTER_CONSUMER_KEY","TWITTER_CONSUMER_SECRET","TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_TOKEN_SECRET"]
    for k in keys:
        if not os.environ.get(k):
            raise Exception("Faltam credenciais do Twitter nas variáveis de ambiente")
    auth = tweepy.OAuth1UserHandler(
        os.environ["TWITTER_CONSUMER_KEY"],
        os.environ["TWITTER_CONSUMER_SECRET"],
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    api = tweepy.API(auth)
    try:
        api.update_status(texto)
    except tweepy.errors.Forbidden as e:
        print("Falha ao tentar postar no X/Twitter. Motivo:", e)
        print("Provavelmente sua conta X/Twitter não tem acesso 'Elevated'. Veja detalhes em https://developer.x.com/en/portal/product")
        return
