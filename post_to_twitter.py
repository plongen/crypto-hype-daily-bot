import tweepy
import os

def postar_no_x(texto):
    keys = [
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    # Checa env
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
        print("\n✅ Tweet postado com sucesso!")
    except tweepy.errors.Forbidden as e:
        print("\n⚠️ Falha ao postar automaticamente no X/Twitter. Motivo:")
        print(e)
        print("Provavelmente sua conta X/Twitter não tem acesso 'Elevated' ou plano pago. Veja detalhes em https://developer.x.com/en/portal/product")
        print("\n📝 Copie e poste manualmente o texto abaixo no X/Twitter:")
        print("="*60)
        print(texto if texto.strip() else "[Nada gerado pelo Gemini! Veja logs ou tente de novo!]")
        print("="*60)
        return
    except Exception as e:
        print(f"[ERRO inesperado ao postar no X/Twitter]: {e}")
        print("\n📝 Copie e poste manualmente o texto abaixo no X/Twitter:")
        print("="*60)
        print(texto if texto.strip() else "[Nada gerado pelo Gemini! Veja logs ou tente de novo!]")
        print("="*60)
