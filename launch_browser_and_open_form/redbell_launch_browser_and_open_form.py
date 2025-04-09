import re
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from utils.helper import clean_address

def redbell_launch_browser_and_open_form(order_url, session):
    # Set up Chrome options
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies()
    cookies = session.cookies.get_dict()

    driver.get("https://valuationops.homegenius.com")
    driver.add_cookie({
        'name': '.ASPXAUTH',
        'value': cookies['.ASPXAUTH'],
        'domain': '.homegenius.com',
        'expires': None
    })

    driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
    driver.get(order_url)
    time.sleep(10)
