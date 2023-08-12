from time import sleep
from interfaces import Crawler
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMTotalPropertyStock, SQMWeeklyRents
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class SeleniumCrawler(Crawler):
    def __init__(self):
        options = Options()
        options.binary_location = '/opt/headless-chromium'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')

        print("Initializing web driver")
        self.driver = webdriver.Chrome("/opt/chromedriver", options=options)
        pass

    def crawl_core_logic_daily_home_value(self) -> CoreLogicDailyHomeValue:
        print("Crawling Core logic page")
        self.driver.get("https://www.corelogic.com.au/our-data/corelogic-indices/")

        print("Finding Core Logic indices")
        change_day_on_day = self.driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
        change_day_on_day = float(change_day_on_day)
        try:
            daily_index = self.driver.execute_script("return BackSeriesExcelData.worm.filter(worm => worm.label === 'Adelaide')[0].data[0][1]")
        except:
            print("Failed to use Javascript to retrieve index retrieving using other method")
            try:
                daily_index = self.driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
            except:
                pass
        return CoreLogicDailyHomeValue(datetime.today().date(), change_day_on_day, float(daily_index))

    def crawl_sqm_weekly_rents(self) -> SQMWeeklyRents:
        print("Crawling SQM Research Weekly rent indexes")
        self.driver.get("https://sqmresearch.com.au/weekly-rents.php?region=sa-Adelaide&type=c&t=1")

        table = self.driver.find_element_by_class_name("changetable")
        second_row = table.find_element_by_css_selector("tr:nth-child(2)")
        week_ending_on = second_row.find_element_by_css_selector("td:nth-child(1)").text
        week_ending_on = week_ending_on.replace("Week ending\n", "").replace("($)", "").strip()
        week_ending_on = datetime.strptime(week_ending_on, "%d %b %Y").date()

        row = table.find_element_by_css_selector("tr:nth-child(3)")
        value_in_dollars = row.find_element_by_css_selector("td:nth-child(3)").text
        change_on_prev_week = row.find_element_by_css_selector("td:nth-child(4)").text
        return SQMWeeklyRents(week_ending_on, float(change_on_prev_week), float(value_in_dollars))

    def crawl_prop_track_house_prices(self) -> PropTrackHousePrices:
        print("Crawling Prop Track page")
        self.driver.get("https://www.proptrack.com.au/home-price-index/")

        print("Finding Prop Track indices")
        self.driver.execute_script("window.scrollBy(0, 800);")
        iframe = self.driver.find_element_by_css_selector("#latest iframe")
        self.driver.switch_to.frame(iframe)
        nestedIframe = self.driver.find_element_by_css_selector("#story iframe")
        self.driver.switch_to.frame(nestedIframe)
        xpath_selector = "//*[@id='main-container']//*[contains(@class, 'body-row')]"
        element_present = EC.presence_of_element_located((By.XPATH, xpath_selector))
        WebDriverWait(self.driver, 15).until(element_present)
        rows = self.driver.find_elements_by_css_selector("#main-container .body-row")
        for row in rows:
            if ("Adelaide" in row.text):
                percentage_change = float(row.find_element_by_css_selector(".td:nth-child(2)").text.replace("%", ''))
                median_value_in_dollars = row.find_element_by_css_selector(".td:nth-child(4)").text
                median_value_in_dollars_stripped = median_value_in_dollars.replace('$', '').replace(",", "")
                last_month = datetime.today() - timedelta(days=28);
                return PropTrackHousePrices(date(last_month.year, last_month.month, 1), percentage_change, float(median_value_in_dollars_stripped))
        raise RuntimeError("Could not find Adelaide row in Prop Track table")

    def crawl_sqm_total_property_stock(self) -> SQMTotalPropertyStock:
        print("Crawling SQM Research Total Property Stock")
        self.driver.get("https://sqmresearch.com.au/total-property-listings.php?region=sa-Adelaide&type=c&t=1")
        last_data_point = self.driver.find_element_by_css_selector(".highcharts-series.highcharts-series-4 rect:nth-last-child(1)")
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(last_data_point, 0, 0)
        actions.perform()
        # Wait until tooltip is visible
        total_stock = WebDriverWait(self.driver, 15) \
            .until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".highcharts-tooltip text :nth-child(3)"))) \
            .text \
            .replace("Total: ", "") \
            .replace(",", "")
        month = self.driver.find_element_by_css_selector(".highcharts-tooltip text :nth-child(1)").text
        month = datetime.strptime(month, "%b %Y").date()
        half_year_series = self.driver.find_element_by_css_selector(".highcharts-series.highcharts-series-4 rect:nth-last-child(2)")
        actions.move_to_element_with_offset(half_year_series, 0, 0)
        actions.perform()
        previous_month_total_stock = WebDriverWait(self.driver, 15) \
            .until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".highcharts-tooltip text :nth-child(3)"))) \
            .text \
            .replace("Total: ", "") \
            .replace(",", "")
        month_on_month_change = int(total_stock) - int(previous_month_total_stock)

        return SQMTotalPropertyStock(month, int(total_stock), month_on_month_change)

    def __del__(self):
        print("Closing driver")
        self.driver.quit()
        pass