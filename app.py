from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import traceback
import boto3
from dynamodb_repository import DynamoDBRepository
from interfaces import Crawler, MessagePoster, Repository
from selenium_crawler import SeleniumCrawler
from tweet_poster import TweetPoster

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
    
    crawl_job_failed = False

    message_poster: MessagePoster = TweetPoster(is_dry_run=is_dry_run)
    crawler: Crawler = SeleniumCrawler()
    repository: Repository = DynamoDBRepository()
    
    try:
        time_in_adelaide = datetime.utcnow() + timedelta(hours=9, minutes=30)
        is_first_day_of_month = time_in_adelaide.day == 1

        if (is_first_day_of_month or force_run_proptrack_crawl):
            index = crawler.crawl_prop_track_house_prices()
            message_poster.post_prop_track_house_prices(index)
            if not is_dry_run:
                repository.post_prop_track_house_prices(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        # Only run on Saturdays (SQM research updates their indexes on Fridays)
        if (datetime.today().weekday() == 5 or force_run_sqm_research_crawl):
            index = crawler.crawl_sqm_weekly_rents()
            message_poster.post_sqm_weekly_rents(index)
            if not is_dry_run:
                repository.post_sqm_weekly_rents(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if (not disable_core_logic_crawl):
            index = crawler.crawl_core_logic_daily_home_value()
            message_poster.post_core_logic_daily_home_value(index)
            if not is_dry_run:
                repository.post_core_logic_daily_home_value(index)
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