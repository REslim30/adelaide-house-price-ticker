from selenium import webdriver
from selenium.webdriver.common.by import By
import tweepy
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import boto3

dynamodb = boto3.client("dynamodb")

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
                    median_value_in_dollars = row.find_element_by_css_selector(".td:nth-child(4)").text
                    median_value_in_dollars_stripped = median_value_in_dollars.replace('$', '').replace(",", "")
                    last_month = datetime.today() - timedelta(days=28);
                    tweet(text=f"{last_month.strftime('%b %Y')}\nPropTrack All Dwellings Median Price: {median_value_in_dollars} ({format_index_change(percentage_change)}%)")
                    print("Storing into table")
                    item_value = {
                        "month": {
                            "S": last_month.date().strftime('%Y-%m')
                        },
                        "monthly_growth_percentage": {
                            'N': str(percentage_change)
                        },
                        "median_value_in_dollars": {
                            'N': median_value_in_dollars_stripped
                        }
                    }
                    dynamodb.put_item(TableName="proptrack_house_prices", Item=item_value)
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
            value_in_dollars = row.find_element_by_css_selector("td:nth-child(3)").text
            change_day_on_day = row.find_element_by_css_selector("td:nth-child(4)").text
            yesterday = datetime.now() - timedelta(days=1)
            tweet(f"Week ending {yesterday.strftime('%d %b %Y')}\nSQM Research Weekly Rents: ${value_in_dollars} ({format_index_change(float(change_day_on_day))})")
            print("Storing into table")
            item_value = {
                "week_ending_on_date": {
                    "S": yesterday.date().isoformat()
                },
                "change_on_prev_week": {
                    'N': str(change_day_on_day)
                },
                "value_in_dollars": {
                    'N': value_in_dollars
                }
            }
            dynamodb.put_item(TableName="sqm_research_weekly_rents", Item=item_value)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        print("Crawling Core logic page")
        driver.get("https://www.corelogic.com.au/our-data/corelogic-indices/")

        print("Finding Core Logic indices")
        daily_index = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
        change_day_on_day = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
        change_day_on_day = float(change_day_on_day)
        tweet(f"{datetime.today().strftime('%d %b %Y')}\nCoreLogic Daily Home Value Index: {daily_index} ({format_index_change(change_day_on_day)})")
        
        print("Storing Core Logic index value")
        item_value = {
            "date": {
                "S": datetime.today().date().isoformat()
            },
            "change_day_on_day": {
                'N': str(change_day_on_day)
            },
            "value": {
                'N': daily_index
            }
        }
        dynamodb.put_item(TableName="core_logic_daily_home_value", Item=item_value)
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