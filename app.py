from selenium import webdriver
from selenium.webdriver.common.by import By
import tweepy
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

def main(event, context):
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    print("Initializing web driver")
    driver = webdriver.Chrome("/opt/chromedriver", options=options)

    try:
        time_in_adelaide = datetime.utcnow() + timedelta(hours=9, minutes=30)
        is_first_day_of_month = time_in_adelaide.day == 1

        crawl_job_failed = False
        if (is_first_day_of_month):
            print("Crawling Prop Track page")
            driver.get("https://www.proptrack.com.au/home-price-index/")

            print("Finding Prop Track indices")
            driver.execute_script("window.scrollBy(0, 800);")
            iframe = driver.find_element_by_css_selector("#latest iframe")
            driver.switch_to.frame(iframe)
            nestedIframe = driver.find_element_by_css_selector("#story iframe")
            driver.switch_to.frame(nestedIframe)
            xpath_selector = "//*[@id='main-container']//*[contains(@class, 'body-row')]"
            element_present = EC.presence_of_element_located((By.XPATH, xpath_selector))
            WebDriverWait(driver, 15).until(element_present)
            rows = driver.find_elements_by_css_selector("#main-container .body-row")
            for row in rows:
                if ("Adelaide" in row.text):
                    percentage_change = float(row.find_element_by_css_selector(".td:nth-child(2)").text.replace("%", ''))
                    median_value = row.find_element_by_css_selector(".td:nth-child(4)").text
                    last_month = datetime.today() - timedelta(days=28);
                    tweet(text=f"{last_month.strftime('%b %Y')}\nPropTrack All Dwellings Median Price: {median_value} ({format_index_change(percentage_change)}%)")
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        print("Crawling Core logic page")
        driver.get("https://www.corelogic.com.au/our-data/corelogic-indices/")

        print("Finding Core Logic indices")
        daily_index = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
        daily_index_movement = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
        daily_index_movement = float(daily_index_movement)

        tweet(f"{datetime.today().strftime('%d %b %Y')}\nCoreLogic Daily Home Value Index: {daily_index} ({format_index_change(daily_index_movement)})")
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        # Only run on Saturdays (SQM research updates their indexes on Fridays)
        if (datetime.today().weekday == 5):
            print("Crawling SQM Research Weekly rent indexes")
            driver.get("https://sqmresearch.com.au/weekly-rents.php?region=sa-Adelaide&type=c&t=1")

            table = driver.find_element_by_class_name("changetable")
            row = table.find_element_by_css_selector("tr:nth-child(3)")
            rent = row.find_element_by_css_selector("td:nth-child(3)").text
            index_change = row.find_element_by_css_selector("td:nth-child(4)").text
            yesterday = datetime.now() - timedelta(days=1)
            tweet(f"Week ending {yesterday.strftime('%d %b %Y')}\nSQM Research Weekly Rents: ${rent} ({format_index_change(float(index_change))})")
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    print("Closing driver")
    driver.close()
    driver.quit()

    if (crawl_job_failed):
        raise Exception("Crawl failed. From lambda with request id: " + context.aws_request_id)
    else:
        return {
            "statusCode": 200,
            "body": "Index crawling job complete"
        }

def format_index_change(index_change: float or int) -> str:
    padding = " "
    prefix = ""
    if (index_change > 0):
        indicator = "🟢"
        prefix = "+"
    elif (index_change < 0):
        indicator = "🔴"
    else:
        indicator = ""
        padding = ""
    
    return f"{indicator}{padding}{prefix}{index_change}"

def tweet(text: str) -> None:
    print("Sending tweet")
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_secret = os.environ.get("ACCESS_SECRET")

    if (api_key == None or api_secret == None or access_token == None or access_secret == None):
        raise RuntimeError("Missing key/secret");

    client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)
    client.create_tweet(text=text)

def print_stack_trace(e: Exception) -> None:
    stack_trace = traceback.format_exc()
    print(f"An error occurred: {e}")
    print("Stack trace:")
    print(stack_trace)