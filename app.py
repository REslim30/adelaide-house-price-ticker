from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import traceback
import boto3
from interfaces import Crawler, MessagePoster
from selenium_crawler import SeleniumCrawler
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
    crawler: Crawler = SeleniumCrawler()

    try:
        time_in_adelaide = datetime.utcnow() + timedelta(hours=9, minutes=30)
        is_first_day_of_month = time_in_adelaide.day == 1

        crawl_job_failed = False
        if (is_first_day_of_month or force_run_proptrack_crawl):
            index = crawler.crawl_prop_track_house_prices()
            message_poster.post_prop_track_house_prices(index)
            if not is_dry_run:
                print("Storing into table")
                item_value = {
                    "month": {
                        "S": index.month_starting_on.strftime('%Y-%m')
                    },
                    "monthly_growth_percentage": {
                        'N': str(index.monthly_growth_percentage)
                    },
                    "median_value_in_dollars": {
                        'N': str(index.median_dollar_value)
                    }
                }
                dynamodb.put_item(TableName="proptrack_house_prices", Item=item_value)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        # Only run on Saturdays (SQM research updates their indexes on Fridays)
        if (datetime.today().weekday() == 5 or force_run_sqm_research_crawl):
            index = crawler.crawl_sqm_weekly_rents()
            message_poster.post_sqm_weekly_rents(index)
            if not is_dry_run:
                print("Storing into table")
                item_value = {
                    "week_ending_on_date": {
                        "S": index.week_ending_on_date.isoformat()
                    },
                    "change_on_prev_week": {
                        'N': str(index.change_on_prev_week)
                    },
                    "value_in_dollars": {
                        'N': str(index.dollar_value)
                    }
                }
                dynamodb.put_item(TableName="sqm_research_weekly_rents", Item=item_value)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if (not disable_core_logic_crawl):
            index = crawler.crawl_core_logic_daily_home_value()
            message_poster.post_core_logic_daily_home_value(index)
            if not is_dry_run:
                print("Storing Core Logic index value")
                item_value = {
                    "date": {
                        "S": index.date.isoformat()
                    },
                    "change_day_on_day": {
                        'N': str(index.change_day_on_day)
                    },
                    "value": {
                        'N': str(index.value)
                    }
                }
                dynamodb.put_item(TableName="core_logic_daily_home_value", Item=item_value)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

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