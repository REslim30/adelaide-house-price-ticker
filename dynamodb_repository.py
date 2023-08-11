from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents
from interfaces import Repository
import boto3

class DynamoDBRepository(Repository):
    def __init__(self):
        self.dynamodb = boto3.client("dynamodb")
        pass

    def post_core_logic_daily_home_value(self, index: CoreLogicDailyHomeValue) -> None:
        print("Storing core logic daily home value index")
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
        self.dynamodb.put_item(TableName="core_logic_daily_home_value", Item=item_value)
        pass

    def post_prop_track_house_prices(self, index: PropTrackHousePrices) -> None:
        print("Storing prop track house prices index")
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
        self.dynamodb.put_item(TableName="proptrack_house_prices", Item=item_value)
        pass
    
    def post_sqm_weekly_rents(self, index: SQMWeeklyRents) -> None:
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
        self.dynamodb.put_item(TableName="sqm_research_weekly_rents", Item=item_value)
        pass

    