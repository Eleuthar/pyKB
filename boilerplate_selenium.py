from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


driver_path = '/usr/bin/chromedriver_linux64/chromedriver'
brave_path = '/usr/bin/brave-browser'
drv_svc = Service(driver_path)
option = webdriver.ChromeOptions()
option.binary_location = brave_path
browzer = webdriver.Chrome(options=option, service=drv_svc)


"""
find = browzer.find_element(By.ID|NAME, <str>)
find.send_keys(Keys.RETURN)
    # get the search bar and enter the lookup value
"""


