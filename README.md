# Crypto Hype Daily Bot 🇧🇷

> Bot que posta diariamente no Twitter/X o resumo das trends e hype em crypto, tudo de graça usando tiers free de APIs e GitHub Actions.

## Como funciona

- **Busca os tópicos hypados de crypto ontem no X/Twitter** (scraping leve, via snscrape)
- **Pega preços e notícias rápidas** (CoinGecko free API)
- **Resume tudo em linguagem tweetável e humana com IA gratuita** (Google Gemini 1.5 Flash ou Groq/Llama)
- **Posta diariamente** (GitHub Actions agenda e executa)

### Variáveis de ambiente (use GitHub Secrets)

- `GEMINI_API_KEY` — [Pegue aqui](https://ai.google.dev/)
- `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` — [Crie app dev no Twitter/X](https://developer.twitter.com/)

## Rodando local

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
export TWITTER_CONSUMER_KEY=...
...
python main.py
```
---

Código modular e simples para customizar e expandir!  
Qualquer dúvida ou update, só abrir issue 😉
