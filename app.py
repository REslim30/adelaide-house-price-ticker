import chart
from datetime import datetime, timedelta
import traceback
from aws_repository import AWSRepository
from domain import Quarter
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
    simulated_date = None

    if isinstance(event, dict):
        if event.get("disable_core_logic_crawl") == True:
            disable_core_logic_crawl = True
        if event.get("force_run_proptrack_crawl") == True:
            force_run_proptrack_crawl = True
        if event.get("force_run_sqm_weekly_rents_crawl") == True:
            force_run_sqm_weekly_rents_crawl = True
        if event.get("force_run_sqm_total_property_stock") == True:
            force_run_sqm_total_property_stock = True
        if event.get("force_run_sqm_vacancy_rate") == True:
            force_run_sqm_vacancy_rate = True
        if event.get("force_run_quarterly_median_house_sales") == True:
            force_run_quarterly_median_house_sales = True
        if event.get("is_dry_run") == True:
            is_dry_run = True
        if event.get("simulated_date") is not None:
            simulated_date = datetime.strptime(event["simulated_date"], "%Y-%m-%d")

    crawl_job_failed = False

    message_poster: MessagePoster = TweetPoster(is_dry_run=is_dry_run)
    crawler: Crawler = SeleniumCrawler()
    repository: Repository = AWSRepository()
    if simulated_date is not None:
        today = simulated_date
    else:
        today = datetime.utcnow() + timedelta(hours=9, minutes=30)

    try:
        if force_run_quarterly_median_house_sales or should_run_median_house_sales_crawl(today, crawler, repository):
            index = crawler.crawl_quarterly_median_house_sales()
            img_path = chart.generate_quarterly_median_house_sales_choropleth(index)
            message_poster.post_quarterly_median_house_sales(index, img_path)
            repository.post_quarterly_median_house_sales(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if is_first_day_of_month() or force_run_proptrack_crawl:
            index = crawler.crawl_prop_track_house_prices()
            message_poster.post_prop_track_house_prices(index)
            if not is_dry_run:
                repository.post_prop_track_house_prices(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if is_first_day_of_month() or force_run_sqm_total_property_stock:
            index = crawler.crawl_sqm_total_property_stock()
            message_poster.post_sqm_total_property_stock(index)
            if not is_dry_run:
                repository.post_sqm_total_property_stock(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if is_first_day_of_month() or force_run_sqm_vacancy_rate:
            index = crawler.crawl_sqm_vacancy_rate()
            message_poster.post_sqm_vacancy_rate(index)
            if not is_dry_run:
                repository.post_sqm_vacancy_rate(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        # Only run on Saturdays (SQM research updates their indexes on Fridays)
        if datetime.today().weekday() == 5 or force_run_sqm_weekly_rents_crawl:
            index = crawler.crawl_sqm_weekly_rents()
            message_poster.post_sqm_weekly_rents(index)
            if not is_dry_run:
                repository.post_sqm_weekly_rents(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    try:
        if not disable_core_logic_crawl:
            index = crawler.crawl_core_logic_daily_home_value()
            message_poster.post_core_logic_daily_home_value(index)
            if not is_dry_run:
                repository.post_core_logic_daily_home_value(index)
    except Exception as e:
        print_stack_trace(e)
        crawl_job_failed = True

    if crawl_job_failed:
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


def should_run_median_house_sales_crawl(cur_date: datetime, crawler: Crawler, repository: Repository) -> bool:
    # We want to check on the 2nd of every month if we should run the median house sales crawl
    # Don't want to run this crawl on the 1st of the month because it's the same day as the proptrack crawl
    time_in_adelaide = cur_date + timedelta(hours=9, minutes=30)
    if time_in_adelaide.day != 2:
        return False

    # Check if we have already run the crawl for this quarter
    current_quarter = Quarter.from_date(time_in_adelaide)
    if repository.quarterly_median_house_sales_exists(current_quarter):
        return False

    # Check if the median house sales has been released for this quarter
    # If it has, then we should run the crawl
    latest_quarter_released = crawler.check_latest_quarterly_median_house_sales()
    return latest_quarter_released == current_quarter.previous_quarter()

