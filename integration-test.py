import unittest
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents
from dynamodb_repository import DynamoDBRepository
from selenium_crawler import SeleniumCrawler
from datetime import date, timedelta
import boto3

class CrawlerTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.crawler = SeleniumCrawler()
        super(CrawlerTest, self).__init__(*args, **kwargs)
        pass

    def test_crawl_core_logic_daily_home_value(self):
        result = self.crawler.crawl_core_logic_daily_home_value()
        self.assertEqual(result.date, date.today())
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.value, 140)
        self.assertLess(result.value, 210)
        self.assertGreater(result.change_day_on_day, -10)
        self.assertLess(result.change_day_on_day, 10)
        self.assertIsInstance(result.date, date)
        self.assertIsInstance(result.value, float)
        self.assertIsInstance(result.change_day_on_day, float)
        pass

    def test_crawl_prop_track_house_prices(self):
        result = self.crawler.crawl_prop_track_house_prices()
        self.assertEqual(result.month_starting_on, (date.today() - timedelta(days=28)).replace(day=1))
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.median_dollar_value, 500_000)
        self.assertLess(result.median_dollar_value, 1_000_000)
        self.assertGreater(result.monthly_growth_percentage, -1)
        self.assertLess(result.monthly_growth_percentage, 1)
        self.assertIsInstance(result.month_starting_on, date)
        self.assertIsInstance(result.median_dollar_value, float)
        self.assertIsInstance(result.monthly_growth_percentage, float)
        pass

    def test_crawl_sqm_weekly_rents(self):
        result = self.crawler.crawl_sqm_weekly_rents()
        yesterday = date.today() - timedelta(days=1)
        self.assertEqual(result.week_ending_on_date, yesterday)
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.dollar_value, 300)
        self.assertLess(result.dollar_value, 1000)
        self.assertGreater(result.change_on_prev_week, -50)
        self.assertLess(result.change_on_prev_week, 50)
        self.assertIsInstance(result.week_ending_on_date, date)
        self.assertIsInstance(result.dollar_value, float)
        self.assertIsInstance(result.change_on_prev_week, float)
        pass

dynamodb = boto3.client("dynamodb")

class DynamoDBRepositoryTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def test_post_core_logic_daily_home_value(self):
        try:
            repository = DynamoDBRepository()
            index = CoreLogicDailyHomeValue(date(1939, 2, 23), 1.2, 164.25)
            repository.post_core_logic_daily_home_value(index)
            item = dynamodb.get_item(TableName="core_logic_daily_home_value", Key={"date": {"S": index.date.isoformat()}})
            self.assertEqual(item["Item"]["date"]["S"], index.date.isoformat())
            self.assertEqual(item["Item"]["change_day_on_day"]["N"], "1.2")
            self.assertEqual(item["Item"]["value"]["N"], "164.25")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="core_logic_daily_home_value", Key={"date": {"S": index.date.isoformat()}})

    def test_post_prop_track_house_prices(self):
        try:
            repository = DynamoDBRepository()
            index = PropTrackHousePrices(date(1939, 2, 23), 0.67, 417_235)
            repository.post_prop_track_house_prices(index)
            item = dynamodb.get_item(TableName="proptrack_house_prices", Key={"month": {"S": index.month_starting_on.strftime('%Y-%m')}})
            self.assertEqual(item["Item"]["month"]["S"], index.month_starting_on.strftime('%Y-%m'))
            self.assertEqual(item["Item"]["monthly_growth_percentage"]["N"], "0.67")
            self.assertEqual(item["Item"]["median_value_in_dollars"]["N"], "417235")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="proptrack_house_prices", Key={"month": {"S": index.month_starting_on.strftime('%Y-%m')}})

    def test_post_sqm_weekly_rents(self):
        try:
            repository = DynamoDBRepository()
            index = SQMWeeklyRents(date(1939, 2, 23), 5.1, 417_235)
            repository.post_sqm_weekly_rents(index)
            item = dynamodb.get_item(TableName="sqm_research_weekly_rents", Key={"week_ending_on_date": {"S": index.week_ending_on_date.isoformat()}})
            self.assertEqual(item["Item"]["week_ending_on_date"]["S"], index.week_ending_on_date.isoformat())
            self.assertEqual(item["Item"]["change_on_prev_week"]["N"], "5.1")
            self.assertEqual(item["Item"]["value_in_dollars"]["N"], "417235")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="sqm_research_weekly_rents", Key={"week_ending_on_date": {"S": index.week_ending_on_date.isoformat()}})
        pass

if __name__ == '__main__':
    unittest.main()