from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import boto3
from interfaces import MessagePoster
from tweet_poster import TweetPoster
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents

dynamodb = boto3.client("dynamodb")

def main(event, context):
    disable_core_logic_crawl = False
    force_run_proptrack_crawl = False
    force_run_sqm_research_crawl = False
    is_dry_run = False

    if (isinstance(event, dict)):
        if (event.get("disable_core_logic_crawl") == True):
            disable_core_logic_crawl = True
        if (event.get("force_run_proptrack_crawl") == True):
            force_run_proptrack_crawl = True
        if (event.get("force_run_sqm_research_crawl") == True):
            force_run_sqm_research_crawl = True
        if (event.get("is_dry_run") == True):
            is_dry_run = True
    
    message_poster: MessagePoster = TweetPoster(is_dry_run=is_dry_run)

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
        if (is_first_day_of_month or force_run_proptrack_crawl):
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
                    index = PropTrackHousePrices(date(last_month.year, last_month.month, 1), percentage_change, float(median_value_in_dollars_stripped))
                    message_poster.post_prop_track_house_prices(index)
                    if not is_dry_run:
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
        if (datetime.today().weekday() == 5 or force_run_sqm_research_crawl):
            print("Crawling SQM Research Weekly rent indexes")
            driver.get("https://sqmresearch.com.au/weekly-rents.php?region=sa-Adelaide&type=c&t=1")

            table = driver.find_element_by_class_name("changetable")
            row = table.find_element_by_css_selector("tr:nth-child(3)")
            value_in_dollars = row.find_element_by_css_selector("td:nth-child(3)").text
            change_on_prev_week = row.find_element_by_css_selector("td:nth-child(4)").text
            yesterday = datetime.now() - timedelta(days=1)
            index = SQMWeeklyRents(yesterday.date(), change_on_prev_week, float(value_in_dollars))
            message_poster.post_sqm_weekly_rents(index)
            if not is_dry_run:
                print("Storing into table")
                item_value = {
                    "week_ending_on_date": {
                        "S": yesterday.date().isoformat()
                    },
                    "change_on_prev_week": {
                        'N': str(change_on_prev_week)
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
        if (not disable_core_logic_crawl):
            print("Crawling Core logic page")
            driver.get("https://www.corelogic.com.au/our-data/corelogic-indices/")

            print("Finding Core Logic indices")
            daily_index = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
            change_day_on_day = driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
            change_day_on_day = float(change_day_on_day)
            index = CoreLogicDailyHomeValue(datetime.today().date(), change_day_on_day, daily_index)
            message_poster.post_core_logic_daily_home_value(index)
            if not is_dry_run:
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

def print_stack_trace(e: Exception) -> None:
    stack_trace = traceback.format_exc()
    print(f"An error occurred: {e}")
    print("Stack trace:")
    print(stack_trace)