import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta

def get_trending_tweets(keywords, since, until, max_tweets=50, lang="pt"):
    query = "(" + " OR ".join(keywords) + f') lang:{lang} until:{until} since:{since}'
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= max_tweets:
            break
        tweets.append({
            'user': tweet.user.username,
            'content': tweet.content,
            'url': tweet.url
        })
    return tweets
