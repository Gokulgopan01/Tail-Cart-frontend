import re
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import json
import time
import logging
import requests
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from exact_address_check.redbell_check_exact_address import find_matching_order
from utils.helper import clean_address


def proteck_formopen_fill(orders, driver, session, merged_json, order_details, order_id):
    logging.info("Starting form open process for ProTeck")

    # Clean the target address from the order details
    target_address = clean_address(order_details)
    form_types = [
        'IBPO with MIT', 'Homesteps', 'Homesteps BPO Interior', 'New Chase Exterior BPO on Apollo',
        'Exterior valuation with 3 sales comps and 3 listing comps', 'Exterior BPO', 'Fannie BPO', 'Evaluation'
    ]
    
    # Check if there are any orders in the portal
    if not orders:
        logging.info("No orders in ProTeck portal")
        return

    # Create a list to store addresses from orders
    address_list = []

    # Attempt to find a matching order by checking against the target address
    matched, order, status = find_matching_order(orders, target_address, form_types, order_id)

    if matched:
        # If a matching order is found, and the form type matches
        if status == "matched":
            # Construct the order URL for the matching form
            order_url = f"https://www.protk.com/ProTeck.Fulfillment.Order.Web/LegacyCase/{order['caseNumber']}/ViewForm/Vendor"
            logging.info(f"Form matched for order {order['caseNumber']}. Opening form in browser.")
            # Open the form in the browser using the provided session
            driver.get(order_url)
            return
        else:
            # If the form type doesn't match, log the mismatch
            logging.info(f"Form type mismatch for order {order['caseNumber']}: {order['productType']}")
            return
    else:
        # If no exact address match is found, collect the addresses from all orders for AI-based matching or further checks
        for order in orders:
            address_list.append(order['address'])

        logging.info(f"No exact address match found. Address list: {address_list}")
        
        # Optional: AI-based address match can be implemented here
        # ai_matched_order = try_ai_address_match(address_list, target_address, orders, form_types, order_details)
        # if ai_matched_order:
        #     order_url = f"https://www.protk.com/ProTeck.Fulfillment.Order.Web/LegacyCase/{ai_matched_order['caseNumber']}/ViewForm/Vendor"
        #     redbell_launch_browser_and_open_form(order_url, session)
        
        # If AI matching is not implemented, log the failure
        logging.info("No AI address match implemented, manual intervention needed.")