import keys
import tweepy

client = tweepy.Client(bearer_token=keys.bearer_token, consumer_key=keys.api_key, consumer_secret=keys.api_secret, access_token=keys.access_token, access_token_secret=keys.access_token_secret)

client.create_tweet(text="testing")