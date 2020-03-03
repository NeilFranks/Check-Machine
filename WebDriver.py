from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time


# This method is to open and download the attached report
def download_report(filePath):
    driver = webdriver.Chrome("./chromedriver_mac")
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    driver.get("file://%s" % filePath)
    time.sleep(3)
    os.remove(filePath)  # remove file when you're done with it
