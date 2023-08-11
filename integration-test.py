import unittest
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents
from selenium_crawler import SeleniumCrawler
from datetime import date, timedelta

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

if __name__ == '__main__':
    unittest.main()