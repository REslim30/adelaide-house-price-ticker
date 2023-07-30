from selenium import webdriver
from selenium.webdriver.common.by import By
import keys
import tweepy
from datetime import datetime

driver = webdriver.Chrome()

driver.get("https://www.corelogic.com.au/our-data/corelogic-indices")

daily_index = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text

driver.quit()

client = tweepy.Client(bearer_token=keys.bearer_token, consumer_key=keys.api_key, consumer_secret=keys.api_secret, access_token=keys.access_token, access_token_secret=keys.access_token_secret)

client.create_tweet(text=f"{datetime.today().strftime('%d %b %Y')}\nCore Logic Daily House Value Index: {daily_index}")