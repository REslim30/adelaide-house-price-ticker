from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMTotalPropertyStock, SQMWeeklyRents
from interfaces import MessagePoster
import os
import uuid
import tweepy
import locale

locale.setlocale(locale.LC_ALL, '')

class TweetPoster(MessagePoster):
    def __init__(self, is_dry_run: bool = True) -> None:
        super().__init__()
        self.api_key = os.environ.get("API_KEY")
        self.api_secret = os.environ.get("API_SECRET")
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.access_secret = os.environ.get("ACCESS_SECRET")
        self.is_dry_run = is_dry_run
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret
        )

        if (self.api_key == None or self.api_secret == None or self.access_token == None or self.access_secret == None):
            raise RuntimeError("Missing key/secret");

    def post_core_logic_daily_home_value(self, index: CoreLogicDailyHomeValue):
        self.client.create_tweet(text=self.format_core_logic_daily_home_value(index))
        return

    def post_sqm_weekly_rents(self, index: SQMWeeklyRents):
        self.client.create_tweet(text=self.format_sqm_weekly_rents(index))
        return

    def post_prop_track_house_prices(self, index: PropTrackHousePrices) -> None:
        self.client.create_tweet(text=self.format_prop_track_house_price(index))
        return
    
    def post_sqm_total_property_stock(self, index: SQMTotalPropertyStock) -> None:
        self.client.create_tweet(text=self.format_sqm_total_property_stock(index))
        return
    
    def format_prop_track_house_price(self, index: PropTrackHousePrices):
        return f"{self.test_tweet_prefix()}{index.month_starting_on.strftime('%b %Y')}\nPropTrack All Dwellings Median Price: ${self.comma_separate(index.median_dollar_value)} ({self.format_index_change(index.monthly_growth_percentage, suffix='%')})"

    def format_sqm_weekly_rents(self, index: SQMWeeklyRents) -> str:
        return f"{self.test_tweet_prefix()}Week ending {index.week_ending_on_date.strftime('%d %b %Y')}\nSQM Research Weekly Rents: ${index.dollar_value} ({self.format_index_change(float(index.change_on_prev_week), prefix='$')})"

    def format_core_logic_daily_home_value(self, index: CoreLogicDailyHomeValue) -> str:
        return f"{self.test_tweet_prefix()}{index.date.strftime('%d %b %Y')}\nCoreLogic Daily Home Value Index: {index.value} ({self.format_index_change(index.change_day_on_day)})"

    def format_sqm_total_property_stock(self, index: SQMTotalPropertyStock) -> None:
        return f"{self.test_tweet_prefix()}{index.month_starting_on.strftime('%b %Y')}\nSQM Research Total Property Stock: {self.comma_separate(index.total_stock)} ({self.format_index_change(index.month_on_month_change, decrease_emoji='📉', increase_emoji='📈')})"

    def test_tweet_prefix(self):
        if (self.is_dry_run):
            return f"Test Tweet {uuid.uuid4()}\n"
        else:
            return ""
    
    def comma_separate(self, number: float or int):
        return "{:,}".format(number)

    def format_index_change(
        self,
        index_change: float or int,
        prefix: str = "",
        suffix: str = "",
        decrease_emoji: str = "🔴",
        increase_emoji: str = "🟢"
    ) -> str:
        padding = " "
        sign_prefix = ""
        if (index_change > 0):
            indicator = increase_emoji
            sign_prefix = "+"
        elif (index_change < 0):
            indicator = decrease_emoji
            sign_prefix = "-"
        else:
            indicator = ""
            padding = ""
        
        return f"{indicator}{padding}{sign_prefix}{prefix}{abs(index_change)}{suffix}"