import json
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from tkinter import messagebox
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from utility.helper import log_login_status,initialize_driver
from selenium.webdriver.chrome.service import Service
from utils.helper import clean_address, handle_login_status, setup_driver

# Load environment variables from the .env file
load_dotenv()
class Proteck:
    def __init__(self,username, password, portal_url, portal_name, proxy,session):

        logging.basicConfig(level=logging.INFO)
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None

    # def initialize_driver(self):
    #     """Initialize Selenium WebDriver without version dependency."""
    #     try:
    #         chrome_options = Options()
    #         chrome_options.add_argument("--start-maximized")  #Maximize window
    #         chrome_options.add_argument("--disable-notifications")  #Disable pop-ups

    #         self.driver = webdriver.Chrome(options=chrome_options)  #Auto-detect ChromeDriver
    #         return self.driver
    #     except Exception as e:
    #         logging.error(f"Error initializing WebDriver: {e}")
    #         return None
     
    def login_to_portal(self,username, password, portal_url, portal_name,proxy,session):
        """Login to a generic portal (extendable)."""
        try:
            self.driver =  setup_driver(self)
            if not self.driver:
                raise Exception("WebDriver initialization failed.")

            self.driver.get(portal_url)
            logging.info(f"Navigating to {portal_url}...")
        # Wait for the username field to be visible
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='UserNameOrEmail']"))
            )

            # Enter the username and password
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").clear()
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").send_keys(username)
            self.driver.find_element(By.XPATH, "//*[@id='Password']").send_keys(password)

            # Submit the login form
            self.driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[2]/form/input[3]").click()
            logging.info(f"Clicked login button for {username}")

            # Wait for login success by checking page title
            WebDriverWait(self.driver, 60).until(EC.title_contains("Partner Portal"))

            title = self.driver.title
            login_check_keyword=["Partner Portal"]

            handle_login_status(title, username, login_check_keyword,portal_name)

            # # Maximize the window and set position
            # self.driver.set_window_position(0, 0)
            # self.driver.maximize_window()
            return self.driver
        except Exception as e:
            if self.driver:
                #self.log_login_status(username, portal_name, "Login Failed", None, str(e))
                logging.error(f"Error during login to {portal_name}: {e}")
                messagebox.showerror("Error", f"Login failed: {e}")

        # finally:
        #     pass
        #     # if self.driver:
        #     #     self.driver.quit()
    def proteck_formopen_fill(self, orders, driver, session, merged_json, order_details, order_id):
        logging.info("Starting form open process for ProTeck")
        target_address = clean_address(order_details)
        form_types = [
            'IBPO with MIT', 'Homesteps', 'Homesteps BPO Interior', 'New Chase Exterior BPO on Apollo',
            'Exterior valuation with 3 sales comps and 3 listing comps', 'Exterior BPO', 'Fannie BPO', 'Evaluation'
        ]

        matched, order, status = self.find_matching_order(orders, target_address, form_types, order_id, driver)

        if matched:
            if status == "matched":
                order_url = f"https://www.protk.com/ProTeck.Fulfillment.Order.Web/LegacyCase/{order['caseNumber']}/ViewForm/Vendor"
                logging.info(f"Form matched for order {order['caseNumber']}. Opening form in browser.")
                driver.get(order_url)
                return
            else:
                logging.info(f"Form type mismatch for order {order['caseNumber']}: {order['productType']}")
                return
        else:
            address_list = [order['address'] for order in orders]
            logging.info(f"No exact address match found. Address list: {address_list}")
            logging.info("No AI address match implemented, manual intervention needed.")

    def find_matching_order(self, orders, target_address, form_types, order_id, driver):
        '''Function to match the address and form type for ProTeck orders'''
        try:
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            script_tag = soup.find('script', {'type': 'application/json'})
            if script_tag:
                open_data_json = json.loads(script_tag.string)
            else:
                logging.error("JSON data not found in page.")
                return False, None, None

            orders_list = []
            address_list = []

            for open_subject in open_data_json:
                status_type = open_subject.get('statusType', '')
                if 'Pending' in status_type or 'NeedsRevision' in status_type:
                    order_data = {
                        'caseNumber': open_subject.get('caseNumber'),
                        'statusType': status_type,
                        'orderId': open_subject.get('orderId'),
                    }
                    orders_list.append(order_data)

                    address = open_subject.get('address', {})
                    address1 = address.get('address1', '').replace(" ", "").upper()
                    address2 = address.get('address2', '')
                    address3 = address.get('suite', '')
                    city = address.get('city', '')
                    state = address.get('state', '')
                    zipcode = address.get('zip', '')

                    full_address = f"{address1} {address2} {address3} {city} {state} {zipcode}"
                    cleaned_address = re.sub(r'[\"\'\-,:/]', '', full_address)
                    cleaned_address = re.sub(r'\s+', '', cleaned_address).upper()
                    address_list.append(cleaned_address)

            for order, cleaned_address in zip(orders_list, address_list):
                if target_address == cleaned_address:
                    return True, order, "matched"

            return False, None, None

        except Exception as err:
            logging.error(f"Exception occurred while retrieving orders and addresses: {err}")
            return False, None, None