from interfaces import Crawler
from domain import CoreLogicDailyHomeValue, PropTrackHousePrices, SQMWeeklyRents
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        daily_index = self.driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text
        change_day_on_day = self.driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(2)").text
        change_day_on_day = float(change_day_on_day)
        return CoreLogicDailyHomeValue(datetime.today().date(), change_day_on_day, float(daily_index))

    def crawl_sqm_weekly_rents(self) -> SQMWeeklyRents:
        print("Crawling SQM Research Weekly rent indexes")
        self.driver.get("https://sqmresearch.com.au/weekly-rents.php?region=sa-Adelaide&type=c&t=1")

        table = self.driver.find_element_by_class_name("changetable")
        row = table.find_element_by_css_selector("tr:nth-child(3)")
        value_in_dollars = row.find_element_by_css_selector("td:nth-child(3)").text
        change_on_prev_week = row.find_element_by_css_selector("td:nth-child(4)").text
        yesterday = datetime.now() - timedelta(days=1)
        return SQMWeeklyRents(yesterday.date(), float(change_on_prev_week), float(value_in_dollars))

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

    def __del__(self):
        print("Closing driver")
        self.driver.quit()
        pass