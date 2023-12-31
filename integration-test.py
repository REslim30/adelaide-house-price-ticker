import unittest
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, Quarter, QuarterlyMedianHouseSales, \
    SQMTotalPropertyStock, SQMVacancyRate, SQMWeeklyRents
from aws_repository import AWSRepository
from selenium_crawler import SeleniumCrawler
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta, FR, SA
import boto3
import chart


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
        last_saturday = (datetime.now() + relativedelta(weekday=SA(-1))).date()
        friday_before_last_saturday = last_saturday - timedelta(days=1)
        self.assertEqual(result.week_ending_on_date, friday_before_last_saturday)
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.dollar_value, 300)
        self.assertLess(result.dollar_value, 1000)
        self.assertGreater(result.change_on_prev_week, -50)
        self.assertLess(result.change_on_prev_week, 50)
        self.assertIsInstance(result.week_ending_on_date, date)
        self.assertIsInstance(result.dollar_value, float)
        self.assertIsInstance(result.change_on_prev_week, float)
        pass

    def test_crawl_sqm_total_property_stock(self):
        result = self.crawler.crawl_sqm_total_property_stock()
        self.assertEqual(result.month_starting_on, (date.today() - timedelta(days=28)).replace(day=1))
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.total_stock, 5000)
        self.assertLess(result.total_stock, 15000)
        self.assertGreater(result.month_on_month_change, -5000)
        self.assertLess(result.month_on_month_change, 5000)
        self.assertIsInstance(result.month_starting_on, date)
        self.assertIsInstance(result.total_stock, int)

    def test_crawl_sqm_vacancy_rate(self):
        result = self.crawler.crawl_sqm_vacancy_rate()
        self.assertEqual(result.month_starting_on, (date.today() - timedelta(days=28)).replace(day=1))
        # Rough guides to ensure the values are in the right ballpark
        self.assertGreater(result.vacancy_rate, 0)
        self.assertLess(result.vacancy_rate, 0.05)
        self.assertGreater(result.month_on_month_change, -0.01)
        self.assertLess(result.month_on_month_change, 0.01)
        self.assertIsInstance(result.month_starting_on, date)
        self.assertIsInstance(result.vacancy_rate, float)
        self.assertIsInstance(result.month_on_month_change, float)

    def test_crawl_quarterly_median_house_sales(self):
        result = self.crawler.crawl_quarterly_median_house_sales()
        self.assertEqual(result.year, date.today().year)
        self.assertIn(result.quarter, [1, 2, 3, 4])
        self.assertIsInstance(result.year, int)
        self.assertIsInstance(result.quarter, int)
        self.assertIsInstance(result.download_link, str)
        self.assertIsInstance(result.excel_data, bytes)

    def test_check_latest_quarterly_median_house_sales(self):
        result = self.crawler.check_latest_quarterly_median_house_sales()
        self.assertEqual(result.year, date.today().year)
        self.assertIn(result.quarter, [1, 2, 3, 4])
        self.assertIsInstance(result.year, int)
        self.assertIsInstance(result.quarter, int)


dynamodb = boto3.client("dynamodb")
s3 = boto3.client("s3")


class AWSRepositoryTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def test_post_core_logic_daily_home_value(self):
        try:
            repository = AWSRepository()
            index = CoreLogicDailyHomeValue(date(1939, 2, 23), 1.2, 164.25)
            repository.post_core_logic_daily_home_value(index)
            item = dynamodb.get_item(TableName="core_logic_daily_home_value",
                                     Key={"date": {"S": index.date.isoformat()}})
            self.assertEqual(item["Item"]["date"]["S"], index.date.isoformat())
            self.assertEqual(item["Item"]["change_day_on_day"]["N"], "1.2")
            self.assertEqual(item["Item"]["value"]["N"], "164.25")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="core_logic_daily_home_value", Key={"date": {"S": index.date.isoformat()}})

    def test_post_prop_track_house_prices(self):
        try:
            repository = AWSRepository()
            index = PropTrackHousePrices(date(1939, 2, 23), 0.67, 417_235)
            repository.post_prop_track_house_prices(index)
            item = dynamodb.get_item(TableName="proptrack_house_prices",
                                     Key={"month": {"S": index.month_starting_on.strftime('%Y-%m')}})
            self.assertEqual(item["Item"]["month"]["S"], index.month_starting_on.strftime('%Y-%m'))
            self.assertEqual(item["Item"]["monthly_growth_percentage"]["N"], "0.67")
            self.assertEqual(item["Item"]["median_value_in_dollars"]["N"], "417235")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="proptrack_house_prices",
                                 Key={"month": {"S": index.month_starting_on.strftime('%Y-%m')}})

    def test_post_sqm_weekly_rents(self):
        try:
            repository = AWSRepository()
            index = SQMWeeklyRents(date(1939, 2, 23), 5.1, 417_235)
            repository.post_sqm_weekly_rents(index)
            item = dynamodb.get_item(TableName="sqm_research_weekly_rents",
                                     Key={"week_ending_on_date": {"S": index.week_ending_on_date.isoformat()}})
            self.assertEqual(item["Item"]["week_ending_on_date"]["S"], index.week_ending_on_date.isoformat())
            self.assertEqual(item["Item"]["change_on_prev_week"]["N"], "5.1")
            self.assertEqual(item["Item"]["value_in_dollars"]["N"], "417235")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="sqm_research_weekly_rents",
                                 Key={"week_ending_on_date": {"S": index.week_ending_on_date.isoformat()}})
        pass

    def test_post_sqm_total_property_stock(self):
        try:
            repository = AWSRepository()
            index = SQMTotalPropertyStock(date(1939, 2, 1), 9839, 1000)
            repository.post_sqm_total_property_stock(index)
            item = dynamodb.get_item(TableName="sqm_research_total_property_stock",
                                     Key={"month": {"S": index.month_starting_on.strftime("%Y-%m")}})
            self.assertEqual(item["Item"]["month"]["S"], "1939-02")
            self.assertEqual(item["Item"]["total_stock"]["N"], "9839")
            self.assertEqual(item["Item"]["change_on_prev_month"]["N"], "1000")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="sqm_research_total_property_stock",
                                 Key={"month": {"S": index.month_starting_on.strftime("%Y-%m")}})

    def test_post_sqm_vacancy_rate(self):
        try:
            repository = AWSRepository()
            index = SQMVacancyRate(date(1939, 2, 1), 0.006123417, 0.0004346636)
            repository.post_sqm_vacancy_rate(index)
            item = dynamodb.get_item(TableName="sqm_research_vacancy_rate",
                                     Key={"month": {"S": index.month_starting_on.strftime("%Y-%m")}})
            self.assertEqual(item["Item"]["month"]["S"], "1939-02")
            self.assertEqual(item["Item"]["vacancy_rate"]["N"], "0.006123417")
            self.assertEqual(item["Item"]["change_on_prev_month"]["N"], "0.0004346636")
        except Exception as e:
            raise e
        finally:
            dynamodb.delete_item(TableName="sqm_research_vacancy_rate",
                                 Key={"month": {"S": index.month_starting_on.strftime("%Y-%m")}})

    def test_quarterly_median_house_price_exists(self):
        try:
            repository = AWSRepository()
            not_exist = repository.quarterly_median_house_sales_exists(Quarter(1939, 2))
            s3.put_object(Bucket="aidand-sa-property-data", Key="median-house-prices/1939-Q2.xlsx", Body=b"")
            exists = repository.quarterly_median_house_sales_exists(Quarter(1939, 2))
            self.assertFalse(not_exist)
            self.assertTrue(exists)
        except Exception as e:
            raise e
        finally:
            s3.delete_object(Bucket="aidand-sa-property-data", Key="median-house-prices/1939-Q2.xlsx")

    def test_post_quarterly_median_house_price(self):
        try:
            repository = AWSRepository()
            index = QuarterlyMedianHouseSales(1939, 2,
                                              "https://www.domain.com.au/research/quarterly-house-price-report/",
                                              b"testing")
            repository.post_quarterly_median_house_sales(index)
            object = s3.get_object(Bucket="aidand-sa-property-data",
                                   Key=f"median-house-prices/{index.year}-Q{index.quarter}.xlsx")
            self.assertEqual(object["Body"].read(), b"testing")
        except Exception as e:
            raise e
        finally:
            s3.delete_object(Bucket="aidand-sa-property-data", Key="median-house-prices/1939-Q2.xlsx")


class ChartTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def test_chart_quarterly_median_house_sales(self):
        with open("test_median_house_sales_2023_q1.xlsx", "rb") as f:
            index = QuarterlyMedianHouseSales(2023, 1,
                                              "https://www.domain.com.au/research/quarterly-house-price-report/",
                                              f.read())
        file = chart.generate_quarterly_median_house_sales_choropleth(index)
        with open(file, "rb") as f:
            data = f.read()
            # Assert more than 5 MB
            self.assertGreater(len(data), 5 * 1024 * 1024)
        pass


if __name__ == '__main__':
    unittest.main()
