# import os
# import time
# import logging
# import requests
# import json
# import sys
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from dotenv import load_dotenv

# from utils.helper import clean_address, get_order_address_from_assigned_order, handle_login_status, setup_driver


# # Load variables from .env file
# load_dotenv()

# # Retrieve API URLs from environment variables
# ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")    

# class RedBell:
#     def __init__(self,username, password, portal_url, portal_name, proxy,session):
#         self.username = username
#         self.password = password
#         self.portal_url = portal_url
#         self.portal_name = portal_name
#         self.proxy = proxy
#         self.session = session
#         self.driver = None  # Initialize driver to None

#         logging.basicConfig(level=logging.INFO)
#     def RedBell(self, username, password, portal_url, portal_name, proxy, session_cookie):
#         try:
#             driver = None  # Store Selenium WebDriver instance
#             session = requests.Session()  # Use a session for maintaining login state
#             logging.basicConfig(level=logging.INFO)

#             # Set up Chrome options
#             setup_driver(self)

#             # # Initialize Chrome WebDriver
#             # driver = webdriver.Chrome(options=options)

#             # Check or establish session
#             session, session_flag = self.session_check(self,session, session_cookie)

#             if not session_flag:
#                 login_flag, session = self.login_to_portal(self,username, session)
#                 if not login_flag:
#                     logging.error("Login attempt failed")
#                     return [], None  # Return empty orders and None session

#             # Fetch orders if session is valid
#             if session:
#                 orders, session = self.fetch_data(self,session)
#             else:
#                 logging.error("Session error. Unable to fetch data.")
#                 orders = []
#                 session = None

#             return orders, session ,driver # ✅ Return both orders and session

#         except Exception as e:
#             logging.error(f"An error occurred: {e} at line {sys.exc_info()[-1].tb_lineno}")
#             return [], None  # Return defaults in case of exception
#     def get_headers(self, additional_headers={}):
#         """Returns headers used for API requests."""
#         try:
#             headers = {
#                 'authority': 'valuationops.homegenius.com',
#                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#                 'accept-language': 'en-US,en;q=0.5',
#                 'referer': 'https://valuationops.homegenius.com/VendorPortal',
#                 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'document',
#                 'sec-fetch-mode': 'navigate',
#                 'sec-fetch-site': 'same-origin',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
#             }
#             headers.update(additional_headers)
#             return headers
#         except Exception as e:
#             logging.error(f"Error in get_headers: {e}")

#     def session_check(self, session, session_cookie):
#         """Check if the session is still valid."""
#         url = "https://valuationops.homegenius.com/VendorPortalProfileV1"
#         if session_cookie:
#             cookie = {'.ASPXAUTH': session_cookie}
#             headers = self.get_headers(self)
#             resp = session.get(url, headers=headers, cookies=cookie)
#             if 'Profile Information' in resp.text:
#                 session.cookies.set('.ASPXAUTH', session_cookie)
#                 session.headers.update(cookie)
#                 logging.info("Session Cookie Active!!!")
#                 return session, True
#             else:
#                 logging.info("Session Cookie Not Active!!!")
#         return session, False

#     # def login_to_portal(self, username, session):
#     #     """Attempts to log in to the portal using the provided username."""
#     #     try:
#     #         api_url = os.getenv("AUTHENTICATOR_API_URL")
#     #         payload = json.dumps({"username": username})
#     #         headers = {'Content-Type': 'application/json'}

#     #         response = requests.post(api_url, headers=headers, data=payload)
#     #         if response.status_code == 200:
#     #             resp_data = response.json()
#     #             if resp_data.get('status') == 'success' and resp_data.get('cookies'):
#     #                 session.cookies.update(resp_data['cookies'])
#     #                 logging.info(f"Login successful for {username}")
#     #                 return True, session
#     #         logging.error("Login failed: Invalid response from API")
#     #     except Exception as e:
#     #         logging.error(f"Login error: {e}")
#     #     return False, session

#     def login_to_portal(self, username, password, portal_url, portal_name, proxy,session):
#             try:
#                 #setup_driver(self)
#                 # API call to get cookie
#                 api_url = os.getenv("AUTHENTICATOR_API_URL")
#                 headers = {'Content-Type': os.getenv("API_HEADERS_CONTENT_TYPE")}
#                 payload = json.dumps({"username": username})

#                 response = requests.post(api_url, headers=headers, data=payload)
#                 response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

#                 api_response = response.json()
#                 #portal_url="https://valuationops.homegenius.com/VendorPortal"
#                 if api_response.get("status") == "success":
#                     redbell_cookie = api_response["cookies"].get(".ASPXAUTH")
#                     if redbell_cookie:
#                         self.driver.get(portal_url) # Navigate to the site before adding cookie.
#                         self.driver.add_cookie({'name': '.ASPXAUTH', 'value': redbell_cookie})
#                         self.driver.get(f"{portal_url}/Index") # Navigate to index after cookie.
                        
#                         # Wait for the page to load.
#                         # Wait for login success by checking page title
#                         #WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.ID, "Partner portal")))


#                         title = self.driver.current_url
#                         login_check_keyword=["VendorPortal/Index","DailyUpdates"]

#                         handle_login_status(title, self.username, login_check_keyword,self.portal_name)
                        
#                         return True, session  # Return the driver instance
#                     else:
#                         logging.error("Cookie '.ASPXAUTH' not found in API response.")
#                         title="MFA FAILED"
#                         login_check_keyword=["False"]
#                         handle_login_status(title, self.username, login_check_keyword,self.portal_name)
#                         #return False
                    
#                 else:
#                     logging.error(f"API call failed: {api_response.get('status')}")
#                     title="MFA FAILED"
#                     login_check_keyword=["False"]
#                     handle_login_status(title, self.username, login_check_keyword,self.portal_name)
#                     #return False

#             except requests.exceptions.RequestException as e:
#                 logging.error(f"API request failed: {e}")
#                 title="MFA FAILED"
#                 login_check_keyword=["False"]
#                 handle_login_status(title, self.username, login_check_keyword,self.portal_name)
#                 #return False
#             except json.JSONDecodeError as e:
#                 logging.error(f"Failed to decode JSON response: {e}")
#                 title="MFA FAILED"
#                 login_check_keyword=["False"]
#                 handle_login_status(title, self.username, login_check_keyword,self.portal_name)
#                 #return False
#             except Exception as e:
#                 logging.exception(f"An error occurred: {e}")
#                 title="MFA FAILED"
#                 login_check_keyword=["False"]
#                 handle_login_status(title, self.username, login_check_keyword,self.portal_name)
#                 #return False

#     def fetch_data(self, session):
#         """Fetches orders from the portal."""
#         try:
#             url = "https://valuationops.homegenius.com/VendorPortal/InprogressOrder"
#             response = session.get(url)
#             if response.status_code != 200:
#                 logging.error("Error fetching orders: Invalid response from server")
#                 return [], session

#             cookies = session.cookies.get_dict()
#             headers = self.get_headers({
#                 'accept': '*/*',
#                 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
#                 'origin': 'https://valuationops.homegenius.com',
#                 'referer': url,
#                 'x-requested-with': 'XMLHttpRequest',
#             })
#             data = {
#                 '__aweconid': 'Grid',
#                 'pageSize': '1000',
#                 'page': '1',
#                 'tzo': '-330',
#             }
#             order_response = requests.post(
#                 'https://valuationops.homegenius.com/VendorPortal/GetMyOrderItem',
#                 cookies=cookies,
#                 headers=headers,
#                 data=data,
#             )
#             if order_response.status_code == 200:
#                 orders = order_response.json().get('dt', {}).get('it', [])
#                 return orders, session
#             else:
#                 logging.error("Failed to fetch orders. Server returned error.")
#                 return [], session
#         except Exception as e:
#             logging.error(f"Error fetching data: {e}")
#             return [], session

#     #     # Example Usage
#     # order_id = 3  # Replace with actual order_id
#     # address = get_order_address_from_assigned_order(order_id)
#     # print("Order Address:", address)

#     def redbell_formopen_fill(orders, driver,session, merged_json, order_details,order_id):
#         logging.info("Starting form open process")

#         target_address = clean_address(order_details)

#         form_types = [
#             'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
#             'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
#             '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals',
#             '5 Day Exterior BPO', '5 Day Interior BPO', '5 Day Interior BPO - W Rentals',
#             "3 Day Exterior BPO - W Rentals"
#         ]

#         if not orders:
#             logging.info("No orders in portal")
#             return

#         address_list = []
#         matched, order, status = self.find_matching_order(orders, target_address, form_types, order_id)

#         if matched:
#             if status == "matched":
#                 order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
#                 logging.info("Form matched. Opening in browser.")
#                 self.redbell_launch_browser_and_open_form(order_url, session)  # Uses same session
#                 return
#             else:
#                 logging.info(f"Form type mismatch: {order['ProductDesc']}")
#                 return
#         else:
#             for order in orders:
#                 address_list.append(order['PropAddress'])

#             logging.info(f"No exact address match found. Address list: {address_list}")


#     def find_matching_order(self,orders, target_address, form_types, order_id):
#         order = get_order_address_from_assigned_order(order_id)
#         order_address = clean_address(order)
        
#         # Iterate through each order
#         for order in orders:
#             # order['PropAddress'] = order['PropAddress'].replace(",", "")
#             # cleaned_text1 = re.sub(r'[\"\'\-,:/]', '', order['PropAddress'])
#             # cleaned_text = re.sub(r'\s+', '', cleaned_text1)
#             # order['PropAddress'] = cleaned_text.upper()
#             order_address_from_portal=clean_address( order['PropAddress'])

#             # Address found on portal
#             if order_address == order_address_from_portal:
#                 address_status = True
#                 print("Address Found {}".format(order['PropAddress']))
#                 logging.info("Address Found {}".format(order['PropAddress']))
#                 return True, order, "matched"
#             else:
#                 # If not matched, continue to next iteration
#                 continue

#         # If no match is found
#         return False, None, "not_found"

#     def redbell_launch_browser_and_open_form(order_url, session):
#         # Set up Chrome options
        
#         options = Options()
#         options.add_argument("--start-maximized")
#         options.add_argument("--disable-extensions")
#         driver = webdriver.Chrome(options=options)
#         driver.delete_all_cookies()
#         cookies = session.cookies.get_dict()

#         driver.get("https://valuationops.homegenius.com")
#         driver.add_cookie({
#             'name': '.ASPXAUTH',
#             'value': cookies['.ASPXAUTH'],
#             'domain': '.homegenius.com',
#             'expires': None
#         })

#         driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
#         driver.get(order_url)
#         time.sleep(10)


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

from utils.helper import clean_address, get_order_address_from_assigned_order, handle_login_status, setup_driver

load_dotenv()

ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")

class RedBell:
    def __init__(self, username, password, portal_url, portal_name, proxy, session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        #self.driver = None

        logging.basicConfig(level=logging.INFO)

    # def start_session(self, session_cookie):
    #     try:
    #         #self.driver = setup_driver()
    #         #session = requests.Session()
    #         session, session_flag = self.session_check(session, session_cookie)

    #         if not session_flag:
    #             login_flag, session = self.login_to_portal(self.username, self.password, self.portal_url, self.portal_name, self.proxy, session)
    #             if not login_flag:
    #                 logging.error("Login attempt failed")
    #                 return [], None, None

    #         orders, session = self.fetch_data(session) if session else ([], None)
    #         return orders, session, self.driver

    #     except Exception as e:
    #         logging.error(f"An error occurred: {e} at line {sys.exc_info()[-1].tb_lineno}")
    #         return [], None, None

    def get_headers(self, additional_headers={}):
        try:
            headers = {
                'authority': 'valuationops.homegenius.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.5',
                'referer': 'https://valuationops.homegenius.com/VendorPortal',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            }
            headers.update(additional_headers)
            return headers
        except Exception as e:
            logging.error(f"Error in get_headers: {e}")

    def session_check(self, session, session_cookie):
        url = "https://valuationops.homegenius.com/VendorPortalProfileV1"
        if session_cookie:
            cookie = {'.ASPXAUTH': session_cookie}
            headers = self.get_headers()
            resp = session.get(url, headers=headers, cookies=cookie)
            if 'Profile Information' in resp.text:
                session.cookies.set('.ASPXAUTH', session_cookie)
                session.headers.update(cookie)
                logging.info("Session Cookie Active!!!")
                return session, True
            else:
                logging.info("Session Cookie Not Active!!!")
        return session, False

    def login_to_portal(self):
        try:
            setup_driver(self)
            api_url = os.getenv("AUTHENTICATOR_API_URL")
            headers = {'Content-Type': os.getenv("API_HEADERS_CONTENT_TYPE")}
            payload = json.dumps({"username": self.username})

            response = requests.post(api_url, headers=headers, data=payload)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            api_response = response.json()
            #portal_url="https://valuationops.homegenius.com/VendorPortal"
            if api_response.get("status") == "success":
                redbell_cookie = api_response["cookies"].get(".ASPXAUTH")
                if redbell_cookie:
                    self.driver.get(self.portal_url) # Navigate to the site before adding cookie.
                    self.driver.add_cookie({'name': '.ASPXAUTH', 'value': redbell_cookie})
                    self.driver.get(f"{self.portal_url}/Index") # Navigate to index after cookie.
                    
                    # Wait for the page to load.
                    # Wait for login success by checking page title
                    #WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.ID, "Partner portal")))


                    title = self.driver.current_url
                    login_check_keyword=["VendorPortal/Index","DailyUpdates"]

                    handle_login_status(title, self.username, login_check_keyword,self.portal_name)
                     
                    return self.driver  # Return the driver instance
                else:
                    logging.error("Cookie '.ASPXAUTH' not found in API response.")
                    title="MFA FAILED"
                    login_check_keyword=["False"]
                    handle_login_status(title, self.username, login_check_keyword,self.portal_name)
                    #return False
                   
            else:
                logging.error(f"API call failed: {api_response.get('status')}")
                title="MFA FAILED"
                login_check_keyword=["False"]
                handle_login_status(title, self.username, login_check_keyword,self.portal_name)
                #return False

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, self.username, login_check_keyword,self.portal_name)
            #return False
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, self.username, login_check_keyword,self.portal_name)
            #return False
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, self.username, login_check_keyword,self.portal_name)

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

    def redbell_formopen_fill(self, orders, driver, session, merged_json, order_details, order_id):
        logging.info("Starting form open process")
        target_address = clean_address(order_details)
        form_types = [
            'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
            'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
            '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals',
            '5 Day Exterior BPO', '5 Day Interior BPO', '5 Day Interior BPO - W Rentals',
            "3 Day Exterior BPO - W Rentals"
        ]

        if not orders:
            logging.info("No orders in portal")
            return

        matched, order, status = self.find_matching_order(orders, target_address, form_types, order_id)

        if matched:
            if status == "matched":
                order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
                logging.info("Form matched. Opening in browser.")
                self.redbell_launch_browser_and_open_form(order_url, session)
            else:
                logging.info(f"Form type mismatch: {order['ProductDesc']}")
        else:
            address_list = [order['PropAddress'] for order in orders]
            logging.info(f"No exact address match found. Address list: {address_list}")

    def find_matching_order(self, orders, target_address, form_types, order_id):
        order = get_order_address_from_assigned_order(order_id)
        order_address = clean_address(order)

        for order in orders:
            order_address_from_portal = clean_address(order['PropAddress'])
            if order_address == order_address_from_portal:
                logging.info("Address Found: %s", order['PropAddress'])
                return True, order, "matched"

        return False, None, "not_found"

    # def redbell_launch_browser_and_open_form(self, order_url, session):
    #     options = Options()
    #     options.add_argument("--start-maximized")
    #     options.add_argument("--disable-extensions")
    #     driver = webdriver.Chrome(options=options)
    #     driver.delete_all_cookies()
    #     cookies = session.cookies.get_dict()

    #     driver.get("https://valuationops.homegenius.com")
    #     driver.add_cookie({
    #         'name': '.ASPXAUTH',
    #         'value': cookies['.ASPXAUTH'],
    #         'domain': '.homegenius.com',
    #         'expires': None
    #     })

    #     driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
    #     driver.get(order_url)
    #     time.sleep(10)

    def redbell_launch_browser_and_open_form(self, order_url, session):
        if self.driver is None:
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-extensions")
            self.driver = webdriver.Chrome(options=options)

        self.driver.delete_all_cookies()
        cookies = session.cookies.get_dict()

        self.driver.get("https://valuationops.homegenius.com")
        self.driver.add_cookie({
            'name': '.ASPXAUTH',
            'value': cookies['.ASPXAUTH'],
            'domain': '.homegenius.com',
            'expires': None
        })

        self.driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        self.driver.get(order_url)
        time.sleep(10)