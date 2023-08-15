from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, Quarter, QuarterlyMedianHouseSales, SQMTotalPropertyStock, SQMVacancyRate, SQMWeeklyRents
from interfaces import Repository
import boto3
from botocore.exceptions import ClientError

# Repository implementation for AWS
class AWSRepository(Repository):
    def __init__(self):
        self.dynamodb = boto3.client("dynamodb")
        self.s3 = boto3.client("s3")
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

    def post_sqm_total_property_stock(self, index: SQMTotalPropertyStock) -> None:
        item_value = {
            "month": {
                "S": index.month_starting_on.strftime("%Y-%m")
            },
            "change_on_prev_month": {
                "N": str(index.month_on_month_change)
            },
            "total_stock": {
                'N': str(index.total_stock)
            }
        }
        self.dynamodb.put_item(TableName="sqm_research_total_property_stock", Item=item_value)
        pass

    def post_sqm_vacancy_rate(self, index: SQMVacancyRate) -> None:
        item_value = {
            "month": {
                "S": index.month_starting_on.strftime("%Y-%m")
            },
            "change_on_prev_month": {
                "N": str(index.month_on_month_change)
            },
            "vacancy_rate": {
                'N': str(index.vacancy_rate)
            }
        }
        self.dynamodb.put_item(TableName="sqm_research_vacancy_rate", Item=item_value)
        pass

    def post_quarterly_median_house_sales(self, index: QuarterlyMedianHouseSales) -> None:
        self.s3.put_object(Bucket="aidand-sa-property-data", Key=f"median-house-prices/{index.year}-Q{index.quarter}.xlsx", Body=index.excel_data)
        return super().post_quarterly_median_house_sales(index)
    
    def quarterly_median_house_sales_exists(self, quarter: Quarter) -> bool:
        try:
            self.s3.head_object(Bucket="aidand-sa-property-data", Key=f"median-house-prices/{quarter.year}-Q{quarter.quarter}.xlsx")
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            raise e
        return True