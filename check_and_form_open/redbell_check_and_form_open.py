import re
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from utils.helper import clean_address

def check_and_open_form(orders, session, merged_json):
    print('==============================')
    options = Options()

    
    raw_address = orders.get('subject_address', '')
    address_from_tfs = clean_address(raw_address)

    logging.info("Subject address after cleaning: %s", address_from_tfs)

    valid_form_types = [
        'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
        'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
        '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals',
        '5 Day Exterior BPO', '5 Day Interior BPO', '5 Day Interior BPO - W Rentals',
        '3 Day Exterior BPO - W Rentals'
    ]

    matched = False
    form_url = ''

    for order in orders:
        portal_address = clean_address(order.get('PropAddress', ''))

        if address_from_tfs == portal_address:
            logging.info(f"Exact address match found: {portal_address}")
            print(f"Address Found: {portal_address}")
            matched = True

            if order.get('ProductDesc') in valid_form_types:
                form_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
                logging.info("Form matched and URL found.")
                print(f"Form matched\nOpening: {form_url}")
                break
            else:
                logging.info(f"Form not matched — Product Type: {order['ProductDesc']}")
                print("Form not matched — New Type")

                break

    if not matched:
        logging.info("Exact address not found among orders.")
        print("Exact address not found.")
    
    # Open the form if a valid URL is found
    if form_url:
        chromedriver_path = "C:\\chromedriver.exe"
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.delete_all_cookies()

        cookies = session.cookies.get_dict()
        driver.get("https://valuationops.homegenius.com")

        cookie = {
            'name': '.ASPXAUTH',
            'value': cookies['.ASPXAUTH'],
            'domain': '.homegenius.com'
        }

        driver.add_cookie(cookie)
        driver.get("https://valuationops.homegenius.com/VendorPortal") 
        driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        driver.get(form_url)
        time.sleep(10)
