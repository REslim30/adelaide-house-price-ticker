from datetime import date
import unittest
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, QuarterlyMedianHouseSales, SQMTotalPropertyStock, SQMVacancyRate, SQMWeeklyRents
from tweet_poster import TweetPoster
import os
import re


class TweetPosterTest(unittest.TestCase):
    
    def test_if_api_key_is_missing_should_throw(self):
        api_key = pop_environment_variable("API_KEY")
        with self.assertRaises(RuntimeError) as context:
            TweetPoster()
        if api_key is not None:
            os.environ["API_KEY"] = api_key

    def test_negative_change(self):
        poster = TweetPoster()
        self.assertEqual("🔴 -12.5", poster.format_index_change(-12.5))
    
    def test_positive_change(self):
        poster = TweetPoster()
        self.assertEqual("🟢 +12.5", poster.format_index_change(12.5))
    
    def test_zero(self):
        poster = TweetPoster()
        self.assertEqual("0", poster.format_index_change(0.0))
    
    def test_custom_decrease_emoji(self):
        poster = TweetPoster()
        self.assertEqual("📉 -12.5", poster.format_index_change(-12.5, decrease_emoji="📉"))
    
    def test_custom_increase_emoji(self):
        poster = TweetPoster()
        self.assertEqual("📈 +12.5", poster.format_index_change(12.5, increase_emoji="📈"))

            
    def test_comma_separate(self):
        poster = TweetPoster()
        self.assertEqual("1,000,000,000", poster.comma_separate(1_000_000_000))
    
    def test_format_core_logic_daily_home_value(self):
        value = CoreLogicDailyHomeValue(date(2023, 5, 12), 0.15, 171.5)
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_core_logic_daily_home_value(value)
        self.assertEqual("12 May 2023\nCoreLogic Daily Home Value Index: 171.5 (🟢 +0.15)", result)
    
    def test_dry_run_format_core_logic_daily_home_value(self):
        value = CoreLogicDailyHomeValue(date(2023, 5, 12), 0.15, 171.5)
        poster = TweetPoster(is_dry_run=True)
        result = poster.format_core_logic_daily_home_value(value)
        self.assertRegex(result, r"Test Tweet .*", result)
    
    def test_format_sqm_weekly_rents(self):
        value = SQMWeeklyRents(date(2023, 5, 12), -12.17, 612.75)
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_sqm_weekly_rents(value)
        self.assertEqual(result, "Week ending 12 May 2023\nSQM Research Weekly Rents: $612.75 (🔴 -$12.17)")
    
    def test_dry_run_format_sqm_weekly_rents(self):
        value = SQMWeeklyRents(date(2023, 5, 12), -12.17, 612.75)
        poster = TweetPoster(is_dry_run=True)
        result = poster.format_sqm_weekly_rents(value)
        self.assertRegex(result, r"Test Tweet .*", result)
    
    def test_format_proptrack_house_prices(self):
        value = PropTrackHousePrices(date(2023, 3, 1), 3.12, 710_234)
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_prop_track_house_price(value)
        self.assertEqual(result, "Mar 2023\nPropTrack All Dwellings Median Price: $710,234 (🟢 +3.12%)")
    
    def test_dry_run_format_proptrack_house_prices(self):
        value = PropTrackHousePrices(date(2023, 3, 1), 3.12, 710_234)
        poster = TweetPoster(is_dry_run=True)
        result = poster.format_prop_track_house_price(value)
        self.assertRegex(result, r"Test Tweet .*", result)
    
    def test_format_sqm_total_property_stock(self):
        value = SQMTotalPropertyStock(date(2023, 3, 1), 9_250, -234)
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_sqm_total_property_stock(value)
        self.assertEqual(result, "Mar 2023\nSQM Research Total Property Stock: 9,250 (📉 -234)")
    
    def test_dry_run_format_proptrack_house_prices(self):
        value = SQMTotalPropertyStock(date(2023, 3, 1), 10000, -234)
        poster = TweetPoster(is_dry_run=True)
        result = poster.format_sqm_total_property_stock(value)
        self.assertRegex(result, r"Test Tweet .*", result)

    def test_format_sqm_vacancy_rate(self):
        value = SQMVacancyRate(date(2023, 3, 1), 0.006512384, 0.00051928374)
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_sqm_vacancy_rate(value)
        self.assertEqual(result, "Mar 2023\nSQM Research Vacancy Rate: 0.65% (📈 +0.05)")
    
    def test_format_quarterly_house_sales(self):
        value = QuarterlyMedianHouseSales(2023, 1, "https://data.sa.gov.au/data/dataset/metro-median-house-sales", b"")
        poster = TweetPoster(is_dry_run=False)
        result = poster.format_quarterly_median_house_sales(value)
        self.assertEqual(result, "Median House Sales 2023 Q1\nFull dataset: https://data.sa.gov.au/data/dataset/metro-median-house-sales")

def pop_environment_variable(env_name: str) -> str or None:
    original_value = os.environ.get(env_name)
    if env_name in os.environ:
        del os.environ[env_name]
    return original_value

if __name__ == '__main__':
    unittest.main()