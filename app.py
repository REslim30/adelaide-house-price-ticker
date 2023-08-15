import chart
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import traceback
from dynamodb_repository import DynamoDBRepository
from interfaces import Crawler, MessagePoster, Repository
from selenium_crawler import SeleniumCrawler
from tweet_poster import TweetPoster

def main(event, context):
    disable_core_logic_crawl = False
    force_run_proptrack_crawl = False
    force_run_sqm_weekly_rents_crawl = False
    force_run_sqm_total_property_stock = False
    force_run_sqm_vacancy_rate = False
    force_run_quarterly_median_house_sales = False
    is_dry_run = False

    if (isinstance(event, dict)):
        if (event.get("disable_core_logic_crawl") == True):
            disable_core_logic_crawl = True
        if (event.get("force_run_proptrack_crawl") == True):
            force_run_proptrack_crawl = True
        if (event.get("force_run_sqm_weekly_rents_crawl") == True):
            force_run_sqm_weekly_rents_crawl = True
        if (event.get("force_run_sqm_total_property_stock") == True):
            force_run_sqm_total_property_stock = True
        if (event.get("force_run_sqm_vacancy_rate") == True):
            force_run_sqm_vacancy_rate = True
        if (event.get("force_run_quarterly_median_house_sales") == True):
            force_run_quarterly_median_house_sales = True
        if (event.get("is_dry_run") == True):
            is_dry_run = True
    
    crawl_job_failed = False

    message_poster: MessagePoster = TweetPoster(is_dry_run=is_dry_run)
    crawler: Crawler = SeleniumCrawler()
    repository: Repository = DynamoDBRepository()
    
    try:
        if (should_run_median_house_sales_crawl() or force_run_quarterly_median_house_sales):
            index = crawler.crawl_quarterly_median_house_sales()
            img_path = chart.generate_quarterly_median_house_sales_choropleth(index)
            message_poster.post_quarterly_median_house_sales(index, img_path)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if (is_first_day_of_month() or force_run_proptrack_crawl):
            index = crawler.crawl_prop_track_house_prices()
            message_poster.post_prop_track_house_prices(index)
            if not is_dry_run:
                repository.post_prop_track_house_prices(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True
    
    try:
        if (is_first_day_of_month() or force_run_sqm_total_property_stock):
            index = crawler.crawl_sqm_total_property_stock()
            message_poster.post_sqm_total_property_stock(index)
            if not is_dry_run:
                repository.post_sqm_total_property_stock(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True
    
    try:
        if (is_first_day_of_month() or force_run_sqm_vacancy_rate):
            index = crawler.crawl_sqm_vacancy_rate()
            message_poster.post_sqm_vacancy_rate(index)
            if not is_dry_run:
                repository.post_sqm_vacancy_rate(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        # Only run on Saturdays (SQM research updates their indexes on Fridays)
        if (datetime.today().weekday() == 5 or force_run_sqm_weekly_rents_crawl):
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

def is_first_day_of_month() -> bool:
    time_in_adelaide = datetime.utcnow() + timedelta(hours=9, minutes=30)
    return time_in_adelaide.day == 1

def should_run_median_house_sales_crawl() -> bool:
    # We want to run this crawl on the 1st of the 2nd month following the end of a quarter
    # e.g. 1st of Feb, May, Aug, Nov
    time_in_adelaide = datetime.utcnow() + timedelta(hours=9, minutes=30)
    return time_in_adelaide.day == 1 and time_in_adelaide.month in [2, 5, 8, 11]