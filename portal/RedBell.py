
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

from form_filler.redbell_form_filler import RedBellFormFiller
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clean_address, clearing, data_filling_text, data_filling_text_QC, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_datefilling, params_check, radio_btn_click, select_field, setup_driver
from config import env

# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class RedBell:
    def __init__(self, username, password, portal_url, portal_name, proxy, session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.order_id = None
        logging.basicConfig(level=logging.INFO)

    def login_to_portal(self):
        try:
            setup_driver(self)
            api_url = env.AUTHENTICATOR_API_URL
            headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
            payload = json.dumps({"username": self.username})

            response = requests.post(api_url, headers=headers, data=payload)
            response.raise_for_status()
            api_response = response.json()

            if api_response.get("status") == "success":
                redbell_cookie = api_response["cookies"].get(".ASPXAUTH")
                if redbell_cookie:
                    self.driver.get(self.portal_url)
                    self.driver.add_cookie({'name': '.ASPXAUTH', 'value': redbell_cookie})
                    self.driver.get(f"{self.portal_url}/Index")

                    title = self.driver.current_url
                    login_check_keyword = ["VendorPortal/Index", "DailyUpdates"]
                    #handle_login_status(title, self.username, login_check_keyword, self.portal_name)

                    # Setup session using cookie
                    session = requests.Session()
                    session.cookies.set('.ASPXAUTH', redbell_cookie, domain="valuationops.homegenius.com")
                    self.session = session

                    arg1, arg2 = params_check()
                    #arg1 = "SmartEntry"  # Manually set for testing
                    if arg1 == "SmartEntry":
                        orders, session = self.fetch_data(self.session)
                        self.redbell_formopen(
                            orders=orders,
                            session=session,
                            merged_json=None,
                            order_details=self.order_details,
                            order_id=self.order_id
                        )
                        print("Completed")
                        # redbell_formopen_fill(self, orders, session,  merged_json=None,
                        #     order_details=self.order_details,
                        #     order_id=self.order_id)
                    else:    
                        handle_login_status(title, self.username, login_check_keyword, self.portal_name)    
                    return self.driver, self.session

                else:
                    logging.error("Cookie '.ASPXAUTH' not found in API response.")
            else:
                logging.error(f"API call failed: {api_response.get('status')}")

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
        except Exception as e:
            logging.exception(f"An error occurred: {e}")

        title = "MFA FAILED"
        login_check_keyword = ["False"]
        handle_login_status(title, self.username, login_check_keyword, self.portal_name)
        return None, None

    def fetch_data(self, session):
        try:
            url = "https://valuationops.homegenius.com/VendorPortal/InprogressOrder"
            response = session.get(url)
            if response.status_code != 200:
                logging.error("Error fetching orders: Invalid response from server")
                return [], session

            cookies = session.cookies.get_dict()
            headers = self.get_headers({
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

    def get_headers(self, additional_headers={}):
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

    def redbell_formopen(self, orders, session, merged_json, order_details, order_id):
        orders_from_api = HybridBPOApi.get_entry_order() 
        if not orders_from_api:  # Check if the order list is empty
            print("No orders found.")
            return
        
        # Process each order
        for order_from_api in orders_from_api:
            portal_name = order_from_api.get("portal_name", "")
            username = order_from_api.get("username", "")
            password = order_from_api.get("password", "")
            portal_url = order_from_api.get("portal_url", "")
            proxy = order_from_api.get("proxy", None)  # Optional proxy
            session=order_from_api.get("session",None)
            order_id=order_from_api.get("order_id","")
            order_details_from_api=get_order_address_from_assigned_order(order_id)
        logging.info("Starting form open process")
        target_address = clean_address(order_details_from_api)
        form_types = ['Interior BPO - W Rentals','Exterior Enhanced BPO','Interior BPO','Exterior BPO','Exterior BPO - W Rentals','5 Day MIT ARBPO','5 Day Interior Appraiser Reconciled BPO','5 Day Exterior Appraiser Reconciled BPO','5 Day Exterior BPO - W Rentals','5 Day Exterior BPO','5 Day Interior BPO','5 Day Interior BPO - W Rentals',"3 Day Exterior BPO - W Rentals"]
        if not orders:
            logging.info("No orders in portal")
            return

        matched, order, status = self.find_matching_order(orders, target_address, form_types, order_id)

        if matched and status == "matched":
            order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
            logging.info("Form matched. Opening in browser.")
            
            self.redbell_launch_browser_and_open_form(order_url, session)
            redbell_formopen_fill(self, order, session, merged_json, order_details, order_id)
        elif not matched:
            logging.info("No exact address match found.")

    def find_matching_order(self, orders, target_address, form_types, order_id, order_details=None):
        address_found = False
        address_list = []

        for order in orders:
            order_address = clean_address(order.get('PropAddress', ''))
            cleaned_target = clean_address(target_address)

            # Address matched
            if cleaned_target == order_address:
                address_found = True
                print(f"Address Found {order['PropAddress']}")
                logging.info(f"Address Found {order['PropAddress']}")

                # Form matched
                if order.get('ProductDesc') in form_types:
                    print("Form matched")
                    print(order.get('OrderId'), order.get('ItemId'))
                    order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
                    print(order_url)
                    logging.info("Form Matched")
                    return True, order, "matched"

                # Form not matched
                else:
                    print("Form not matched---New Type")
                    logging.info(f"Form not Found --New Type {order.get('ProductDesc')}")
                    
                    return False, None, "form_not_matched"

            else:
                print(f"Address Not Found {order.get('PropAddress')}")
                logging.info(f"Address Not Found {order.get('PropAddress')}")
                address_list.append(order_address)

        return False, None, "address_not_found"



    def redbell_launch_browser_and_open_form(self, order_url, session):
        # Navigate to order page
        self.driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        self.driver.get(order_url)

        time.sleep(10)
    from form_filler.redbell_form_filler import RedBellFormFiller

def redbell_formopen_fill(self, order, session, merged_json, order_details, order_id):
    #for order in orders:
        ProductDesc = order['ProductDesc'].strip()
        if 'Rental' in ProductDesc:
            form_url = f"https://valuationops.homegenius.com/VendorBpoForm?ItemId={order['ItemId']}&OrderId={order['OrderId']}&ActivePage=SubjectHistoryAdj"
            self.driver.get(form_url)
            self.driver.implicitly_wait(10)

            with open('json/redbelljson/Redbell_Enhanced.json') as f:
                form_config = json.load(f)
            # with open('json/redbelljson/redbell_rnt data.json') as f:
            #     merged_json = json.load(f)
            # filler = RedBellFormFiller(self.driver)
            # filler.fill_form(merged_json, order_details, form_config)
              # Fetch fresh merged_json if needed, or use the passed one
        url = f"http://192.168.2.70:8001/api/v1/entry-data/?order_id={order_id}"
        response = requests.get(url)
        if response.status_code == 200:
            merged_json = response.json()
            fill_form_multi(self.driver, merged_json, order_details, form_config)
        else:
            logging.error(f"Failed to fetch merged_json, status code: {response.status_code}")

def fill_form_multi(self, merged_json, order_details, form_config):
    data_sources = {
        "Subject_info": merged_json.get("subject_data", {}),
        "Comp_info": merged_json.get("comp_data", {}),
        "Adj_info": merged_json.get("adj_data", {}),
        "Rental_info": merged_json.get("rental_data", {}),
        "Sub_info": merged_json.get("sub_data", {})
    }

    field_actions = {
        "Textbox": data_filling_text,
        "Textbox_default": lambda d, k, x, m: data_filling_text(d, k, x, m),
        "select_data": select_field,
        "select_default": lambda d, k, x, m: select_field(d, k, x, m),
        "radiobutton_data": radio_btn_click,
        "radiobutton_default": lambda d, k, x, m: radio_btn_click(d, k, x, m),
        "date_fill_javascript": javascript_excecuter_datefilling,
        "clearing": lambda d, _, x, m: clearing(d, x, m),
        "Textbox_QC": data_filling_text_QC,
        "Textbox_default_QC": lambda d, k, x, m: data_filling_text_QC(d, k, x, m),
    }

    for page in form_config.get("page", []):
        for section_key, section_data in page.items():
            if section_key not in data_sources:
                logging.info(f"Skipping unknown section key: {section_key}")
                continue

            data_source = data_sources[section_key]
            for section in section_data:
                field_type = section.get("filedtype")
                # Skip 'save_data' or other special types
                if field_type == "save_data":
                    continue

                for item in section.get("values", []):
                    if isinstance(item, dict):
                        # Sometimes item is a dict for special actions (nextpage/save_data)
                        continue

                    if len(item) != 3:
                        logging.warning(f"Invalid field item format: {item}")
                        continue

                    key, xpath, mode = item

                    # If data_source is a dict of dicts (like comp_data with multiple comps)
                    if isinstance(data_source, dict) and (
                        section_key in ["Comp_info", "Rental_info"]
                    ):
                        for subkey, comp_entry in data_source.items():
                            value = comp_entry.get(key, "")
                            if value in [None, ""] and "default" not in field_type:
                                logging.info(f"Skipping empty value for {field_type} - {subkey}:{key}")
                                continue
                            try:
                                action_func = field_actions.get(field_type)
                                if action_func:
                                    action_func(self.driver, value, xpath, mode)
                                else:
                                    logging.warning(f"Unknown field type: {field_type}")
                            except Exception as e:
                                logging.error(f"Error in {subkey} - {key}: {e}")
                    else:
                        # For single dict data_source (subject_data, adj_data, etc)
                        value = data_source.get(key, "")
                        if value in [None, ""] and "default" not in field_type:
                            logging.info(f"Skipping empty value for {field_type} - Key: {key}")
                            continue
                        try:
                            action_func = field_actions.get(field_type)
                            if action_func:
                                action_func(self.driver, value, xpath, mode)
                            else:
                                logging.warning(f"Unknown field type: {field_type}")
                        except Exception as e:
                            logging.error(f"Error processing {field_type} - Key: {key}, XPath: {xpath}, Error: {e}")
            