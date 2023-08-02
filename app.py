from selenium import webdriver
from selenium.webdriver.common.by import By
import tweepy
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

def main(event, context):
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")

    access_token = os.environ.get("ACCESS_TOKEN")
    access_secret = os.environ.get("ACCESS_SECRET")

    if (api_key == None or api_secret == None or access_token == None or access_secret == None):
        raise RuntimeError("Missing key/secret");

    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    print("Initializing web driver")
    driver = webdriver.Chrome("/opt/chromedriver", options=options)

    print("Accessing web page")
    driver.get("https://www.corelogic.com.au/our-data/corelogic-indices")

    print("Finding element")
    daily_index = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
    daily_index_movement = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
    daily_index_movement = float(daily_index_movement)

    daily_index_movement_padding = " "
    daily_index_movement_prefix = ""
    if (daily_index_movement > 0):
        daily_index_movement_indicator = "🟢"
        daily_index_movement_prefix = "+"
    elif (daily_index_movement < 0):
        daily_index_movement_indicator = "🔴"
    else:
        daily_index_movement_indicator = ""
        daily_index_movement_padding = ""

    print("Closing driver")
    driver.close()
    driver.quit()

    print("Initializing Twitter client")
    client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

    print("Creating tweet")
    client.create_tweet(text=f"{datetime.today().strftime('%d %b %Y')}\nCoreLogic Daily Home Value Index: {daily_index} ({daily_index_movement_indicator}{daily_index_movement_padding}{daily_index_movement_prefix}{daily_index_movement})")

    response = {
        "statusCode": 200,
        "body": "Selenium Headless Chrome Initialized"
    }

    return response