from selenium import webdriver
from selenium.webdriver.common.by import By

PATH = "/opt/chromedriver/chromedriver"

driver = webdriver.Chrome()

driver.get("https://www.corelogic.com.au/our-data/corelogic-indices")
print(driver.title)
print(driver.find_element(By.CSS_SELECTOR, "#daily-indices .graph-row:nth-child(4) .graph-column:nth-child(3)").text)
driver.quit()