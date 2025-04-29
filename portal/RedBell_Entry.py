import os
import time
import logging
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

from utils.helper import get_order_address_from_assigned_order, setup_driver


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")    


def RedBellEntry(self, username, password, portal_url, portal_name, proxy, session_cookie):
    try:
        driver = None  # Store Selenium WebDriver instance
        session = requests.Session()  # Use a session for maintaining login state
        logging.basicConfig(level=logging.INFO)

        # Set up Chrome options
        setup_driver(self)

        # # Initialize Chrome WebDriver
        # driver = webdriver.Chrome(options=options)

        # Check or establish session
        session, session_flag = session_check(self,session, session_cookie)

        if not session_flag:
            login_flag, session = login_to_portal(self,username, session)
            if not login_flag:
                logging.error("Login attempt failed")
                return [], None  # Return empty orders and None session

        # Fetch orders if session is valid
        if session:
            orders, session = fetch_data(self,session)
        else:
            logging.error("Session error. Unable to fetch data.")
            orders = []
            session = None

        return orders, session ,driver # ✅ Return both orders and session

    except Exception as e:
        logging.error(f"An error occurred: {e} at line {sys.exc_info()[-1].tb_lineno}")
        return [], None  # Return defaults in case of exception
def get_headers(self, additional_headers={}):
    """Returns headers used for API requests."""
    try:
        headers = {
            'authority': 'valuationops.homegenius.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5',
            'referer': 'https://valuationops.homegenius.com/VendorPortal',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        headers.update(additional_headers)
        return headers
    except Exception as e:
        logging.error(f"Error in get_headers: {e}")

def session_check(self, session, session_cookie):
    """Check if the session is still valid."""
    url = "https://valuationops.homegenius.com/VendorPortalProfileV1"
    if session_cookie:
        cookie = {'.ASPXAUTH': session_cookie}
        headers = get_headers(self)
        resp = session.get(url, headers=headers, cookies=cookie)
        if 'Profile Information' in resp.text:
            session.cookies.set('.ASPXAUTH', session_cookie)
            session.headers.update(cookie)
            logging.info("Session Cookie Active!!!")
            return session, True
        else:
            logging.info("Session Cookie Not Active!!!")
    return session, False

def login_to_portal(self, username, session):
    """Attempts to log in to the portal using the provided username."""
    try:
        api_url = os.getenv("AUTHENTICATOR_API_URL")
        payload = json.dumps({"username": username})
        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_url, headers=headers, data=payload)
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get('status') == 'success' and resp_data.get('cookies'):
                session.cookies.update(resp_data['cookies'])
                logging.info(f"Login successful for {username}")
                return True, session
        logging.error("Login failed: Invalid response from API")
    except Exception as e:
        logging.error(f"Login error: {e}")
    return False, session

def fetch_data(self, session):
    """Fetches orders from the portal."""
    try:
        url = "https://valuationops.homegenius.com/VendorPortal/InprogressOrder"
        response = session.get(url)
        if response.status_code != 200:
            logging.error("Error fetching orders: Invalid response from server")
            return [], session

        cookies = session.cookies.get_dict()
        headers = get_headers({
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://valuationops.homegenius.com',
            'referer': url,
            'x-requested-with': 'XMLHttpRequest',
        })
        data = {
            '__aweconid': 'Grid',
            'pageSize': '1000',
            'page': '1',
            'tzo': '-330',
        }
        order_response = requests.post(
            'https://valuationops.homegenius.com/VendorPortal/GetMyOrderItem',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        if order_response.status_code == 200:
            orders = order_response.json().get('dt', {}).get('it', [])
            return orders, session
        else:
            logging.error("Failed to fetch orders. Server returned error.")
            return [], session
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return [], session

#     # Example Usage
# order_id = 3  # Replace with actual order_id
# address = get_order_address_from_assigned_order(order_id)
# print("Order Address:", address)
