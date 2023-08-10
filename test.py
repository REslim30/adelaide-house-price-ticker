from datetime import date
import unittest
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents
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
        self.assertEqual("0.0", poster.format_index_change(0.0))
    
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


def pop_environment_variable(env_name: str) -> str or None:
    original_value = os.environ.get(env_name)
    if env_name in os.environ:
        del os.environ[env_name]
    return original_value

if __name__ == '__main__':
    unittest.main()