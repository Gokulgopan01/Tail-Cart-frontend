import json
import os
import re
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import logging
from selenium.webdriver.chrome.service import Service
import logging
from tkinter import Image, messagebox
import sys
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from config import env
from utils.glogger import GLogger
logger = GLogger()
# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = env.ASSIGNEDORDERS_URL   

def params_check():
    print("123",sys.argv)
    if len(sys.argv) >= 2:
            url = sys.argv[1]  # Example: 'myapp://?arg1=mlsdownloader&arg2=order123'
            parsed_url = urlparse(url)
            args = parse_qs(parsed_url.query)
            arg1 = args.get('arg1', [None])[0]  # Get 'arg1' or None if not present
            arg2 = args.get('arg2', [None])[0]
            arg3 = args.get('arg3', [None])[0]
            print(f"Args : {arg1}")   
            return arg1,arg2,arg3
            #return "SmartEntry","3604","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjI2LCJlbWFpbCI6Im5hbmRodV9rcmlzaG5hQGVjZXNpc2dyb3Vwcy5jb20iLCJyb2xlIjoyLCJpYXQiOjE3NzM3MzkyMzB9.gofoCzJHG-DmjL-j861Sw6XbqGDucs0QUbZMccnAyV4"
    else:
          #return None,None  
          # Returns auto for manualy opening Autologin  

        return "AutoLogin",None,None
        #return "SmartEntry","3854","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjI2LCJlbWFpbCI6Im5hbmRodV9rcmlzaG5hQGVjZXNpc2dyb3Vwcy5jb20iLCJyb2xlIjoyLCJpYXQiOjE3NzU1NDIxMjJ9.MCW6M9dcUrRrdtN-KBXGmRsR-qnuLVhss3UxcWtkRLQ"

process_type, hybrid_orderid, hybrid_token = params_check()


# def initialize_driver(self):
#         """Initialize Selenium WebDriver."""
#         try:
#                 chrome_options = Options()
#                 chrome_options.add_argument("--start-maximized") 
#                 chrome_options.add_argument("--disable-notifications")

#                 service = Service("chromedriver.exe") 
#                 self.driver = webdriver.Chrome(service=service, options=chrome_options)
#                 return self.driver
#         except Exception as e:
#                 logging.error(f"Error initializing WebDriver: {e}")
#                 return None



def handle_login_status(login_title_or_url, username,login_check_keywords, portal_name,driver=None):
    """Handle login success or failure by checking the current URL."""

    # Check if the current URL contains any of the success indicators
    if any(keyword in login_title_or_url for keyword in login_check_keywords):
        #logging.info(f"Successfully logged in to {portal_name} as {username}.")
        logger.log(
                    module=f"{portal_name}-handle_login_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Successfully logged in to {portal_name} as {username}.",
                    severity="INFO"
                )

        messagebox.showinfo("Login Successful", f"Successfully logged in to {portal_name} .")
    else:
        #logging.error(f"Login failed for {username} on {portal_name}. Possible incorrect credentials or login issue.")
        logger.log(
                    module=f"{portal_name}-handle_login_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Login failed for {username} on {portal_name}. Possible incorrect credentials or login issue.",
                    severity="INFO"
                )
        messagebox.showerror("Login Failed", f"Invalid credentials or login error for {portal_name}.")

    # --- Handle unexpected popups (if any) ---
    try:
        if driver:
            main_window = driver.current_window_handle
            all_windows = driver.window_handles

            # If a popup (new tab/window) is open
            for window in all_windows:
                if window != main_window:
                    driver.switch_to.window(window)
                    logging.info("Closing popup window...")
                    driver.close()  # Close only the popup

            driver.switch_to.window(main_window)
    except Exception as e:
        logging.warning(f"Popup handling error: {e}")    
        

def handle_exception(self, e):
        """Handle exceptions and log the error."""
        stack_trace = traceback.format_exc()
        if stack_trace:
            e = stack_trace
        self.update_report_data(None, str(e), 'UNABLE TO LOGIN')        



# Function to fetch stored token (assuming it was saved as JSON)
# def get_saved_token():
#     try:
#         with open("login_data.json", "r") as file:
#             data = json.load(file)
#             return data.get("token", None)
#     except FileNotFoundError:
#         return None

# def get_saved_token():
#     try:
#         if not os.path.exists("login_data.json"):
#             return None

#         with open("login_data.json", "r") as file:
#             content = file.read().strip()
#             if not content:
#                 return None  # File is empty

#             data = json.loads(content)  # Manually parse after checking
#             return data.get("token", None)

#     except (json.JSONDecodeError, ValueError):
#         return None  # Invalid JSON content


# def get_saved_token():
#     app_data_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "HybridBPO")
#     #print(app_data_dir)
#     logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Condition-check",
#                     remarks=f"app_data_dir-{app_data_dir}",
#                     severity="INFO"
#                 )
#     os.makedirs(app_data_dir, exist_ok=True)  # Make sure the directory exists

#     # Final path: C:\Users\<User>\AppData\Roaming\HybridBPO\login_data.json
#     login_data_file = os.path.join(app_data_dir, "login_data.json")
#     try:
#         if not os.path.exists(login_data_file):
#             #print("Token file does not exist.")
#             logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Condition-check",
#                     remarks=f"Token file does not exist.",
#                     severity="INFO"
#                 )
#             return None

#         with open(login_data_file, "r") as file:
#             content = file.read().strip()
#             if not content:
#                 #print("Token file is empty.")
#                 logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Condition-check",
#                     remarks=f"Token file is empty.",
#                     severity="INFO"
#                 )
#                 return None

#             data = json.loads(content)
#             token = data.get("token", None)
#             if token:
#                 #print("Token loaded successfully.")
#                 logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Condition-check",
#                     remarks=f"Token loaded successfully.",
#                     severity="INFO"
#                 )
#             else:
#                 #print("Token missing in file.")
#                 logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Condition-check",
#                     remarks=f"Token missing in file.",
#                     severity="INFO"
#                 )
#             return token

#     except (json.JSONDecodeError, ValueError):
#         print(" Corrupted token file.")
#         logger.log(
#                     module="get_saved_token",
#                     order_id=hybrid_orderid,
#                     action_type="Exception",
#                     remarks=f"Corrupted token file.",
#                     severity="INFO"
#                 )
#         return None


# Fetch order address using stored token
# def get_order_address_from_assigned_order(order_id):
#     arg1,arg2,arg3=params_check()
#     url = f"{ASSIGNEDORDERS_URL}{order_id}"
#     print("token: ",arg3)
#     #headers = {"Authorization": f"Bearer {arg3}"}  # Include token in headers
#     headers = {
#         "Authorization": f"Bearer {arg3}",
#         "Accept": "application/json"
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             data = response.json()
#             if "content" in data and "data" in data["content"]:
#                 return data["content"]["data"].get("portal_order_id", "Address Not Found")
#             else:
#                 return "Invalid Response Format"
#         else:
#             return f"Error: {response.status_code} - {response.text}"
    
#     except Exception as e:
#         return f"Request Failed: {str(e)}"

def get_order_address_from_assigned_order(order_id, token):
    url = f"{ASSIGNEDORDERS_URL}{order_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "content" in data and "data" in data["content"]:
                #return data["content"]["data"].get("portal_order_id", "Address Not Found")
                order_data = data["content"]["data"]
                portal_order_id = order_data.get("portal_order_id", "Address Not Found")
                tfs_orderid = order_data.get("tfs_orderid", "TFS ID Not Found")
                is_qc = order_data.get("is_qc", "no qc varialble")
                print("API")
                return portal_order_id, tfs_orderid, is_qc
                
            else:
                logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Invalid Response Format.",
                    severity="INFO"
                )
                return "Invalid Response Format",None,False
                
        else:
            logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Error: {response.status_code} - {response.text}",
                    severity="INFO"
                )
            return f"Error: {response.status_code} - {response.text}",None, False
    
    except Exception as e:
        logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Request Failed: {str(e)}",
                    severity="INFO"
                )
        return f"Request Failed: {str(e)}",None, False
        
# def get_order_address_from_assigned_order(order_id, token):
#     url = f"{ASSIGNEDORDERS_URL}{order_id}"

#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Accept": "application/json"
#     }

#     try:
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             data = response.json()

#             if "content" in data and "data" in data["content"]:
#                 order_data = data["content"]["data"]

#                 portal_order_id = order_data.get("portal_order_id")
#                 tfs_orderid = order_data.get("tfs_orderid")

#                 return portal_order_id, tfs_orderid

#             else:
#                 logger.log(
#                     module="get_order_address_from_assigned_order",
#                     order_id=order_id,
#                     action_type="Condition-check",
#                     remarks="Invalid Response Format",
#                     severity="INFO"
#                 )
#                 return None, None  

#         else:
#             logger.log(
#                 module="get_order_address_from_assigned_order",
#                 order_id=order_id,
#                 action_type="Condition-check",
#                 remarks=f"Error: {response.status_code} - {response.text}",
#                 severity="INFO"
#             )
#             return None, None  

#     except Exception as e:
#         logger.log(
#             module="get_order_address_from_assigned_order",
#             order_id=order_id,
#             action_type="Exception",
#             remarks=f"Request Failed: {str(e)}",
#             severity="INFO"
#         )
#         return None, None  



def clean_address(address):
    """Clean and normalize address for comparison."""
    address = address.replace(",", "")
    address = re.sub(r'[\"\'\-,:/]', '', address)
    address = re.sub(r'\s+', '', address)
    return address.upper()

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    root.geometry(f'{width}x{height}+{x}+{y}')


def format_address(address):
    expanded_words = {
        "st": "street",
        "ave": "avenue",
        "blvd": "boulevard",
        "dr": "drive",
        "s": "south",
        "w": "west",
        "e": "east",
        "n": "north",
        "nw": "northwest",
        "ne": "northeast",
        "sw": "southwest",
        "se": "southeast",
        "pl": "place",
        "cv": "cove",
        "ter": "terrace",
        "trl": "trail",
        "lk": "lake",
        "wy": "way",
        "cir": "circle",
        "ct": "court",
        "ln": "lane",
        "pt": "point",
        "rd": "road"
    }
    
    try:
        parts = address.split()
        first_three_parts = parts[:3]
        address_string = ' '.join(first_three_parts)
        abbrevation_checked_parts= [expanded_words.get(comp.lower(), comp) for comp in address_string.split()]
        formatted_address = ' '.join(abbrevation_checked_parts)
        formatted_address = re.sub(r'\W+', '', formatted_address).lower()
        
        return formatted_address
    
    except Exception as e:
        logging.error(f"error in the format address function in utility : {e}")   




def get_cookie_from_api(username, portal, proxy=None):
    try:
        session = requests.Session()
        if proxy:
            session.proxies.update({
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            })
            #logging.info(f"Using proxy: {proxy}")
            logger.log(
                    module="get_cookie_from_api",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Using proxy: {proxy}",
                    severity="INFO"
                )

        headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
        payload = json.dumps({
            "username": username,
            "portal": portal
        })

        api_url = env.AUTHENTICATOR_API_URL
            
        response = session.post(api_url, headers=headers, data=payload, timeout=60)
        response.raise_for_status()
        print(response.raise_for_status())
        print(response.json())
        return response.json()
    

    except requests.exceptions.RequestException as e:
        #logging.error(f"API request failed: {e}")
        logger.log(
                    module="get_cookie_from_api",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"API request failed: {e}",
                    severity="INFO"
                )

        return None
    
def setup_driver(self):
    try:
        self.login_status = "Starting login process"

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("detach", True)

        if hasattr(self, 'proxy') and self.proxy:
            #logging.info(f"Using proxy: {self.proxy}")
            logger.log(
                    module="setup_driver",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Using proxy: {self.proxy}",
                    severity="INFO"
                )
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
        else:
            #logging.info("No proxy provided. Continuing without proxy.")
            logger.log(
                    module="setup_driver",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"No proxy provided. Continuing without proxy.",
                    severity="INFO"
                )

        self.driver = webdriver.Chrome(options=chrome_options)
        logger.log(
                    module="setup_driver",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Chrome driver initialized successfully.",
                    severity="INFO"
                )
        #logging.info("Chrome driver initialized successfully.")


    except Exception as e:
        #logging.error(f"Failed to initialize Chrome driver: {e}")
        logger.log(
                    module="setup_driver",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Failed to initialize Chrome driver: {e}",
                    severity="INFO"
                )
        self.login_status = "Driver initialization failed"
        raise e    

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from datetime import datetime

# def javascript_excecuter_datefilling(driver,data,elementlocator,selector):    
   
#         if data=='':
#             pass

#         else:
#             # date=datetime.strptime(data,"%Y-%m-%d")
#             # date=date.strftime("%d/%m/%Y")
#             script = f"""document.evaluate("{elementlocator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value = '{data}'"""
#             driver.execute_script(script)

def javascript_excecuter_filling(driver, data, elementlocator, selector):
    if not data:
        return

    # Escape single quotes in data to prevent JS syntax errors
    safe_data = str(data).strip().replace("'", "\\'")

    script = f"""
        var el = document.evaluate("{elementlocator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (el) {{
            el.value = '';  // Clear existing value
            el.dispatchEvent(new Event('input'));  // Trigger input event
            el.value = '{safe_data}';  // Refill with new value
            el.dispatchEvent(new Event('input'));
            el.dispatchEvent(new Event('change'));  // Trigger change event to ensure UI reacts
        }}
    """
    driver.execute_script(script)

   
def adj_click(driver, data, element_identifier, element_type):
    data = str(data).strip()
    element_identifier = element_identifier.strip()
    selector_map = selector_mapping(element_type)
    elements = driver.find_elements(selector_map, element_identifier)
    for x in elements:
        try:
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", x)
            x.click()
        except Exception as e:
            # If interrupted by overlay like 'dimbg', clear and try JS click
            print(f"[adj_click] Click intercepted, attempting clearing and JS fallback: {e}")
            close_validation_popup(driver)
            driver.execute_script("arguments[0].click();", x)



def radio_btn_click(driver, btn_value, element_identifier, element_type):
    """
    Deselect any selected radio first, then select the one with the matching value.
    Handles trimming and &nbsp;.
    """
    selector_map = selector_mapping(element_type)
    elements = driver.find_elements(selector_map, element_identifier)
    # Always convert input to string before normalization
    btn_value = str(btn_value).strip()
    btn_value_normalized = re.sub(r"\s+", " ", btn_value.lower())

    # Deselect all first
    for elem in elements:
        if elem.is_selected():
            driver.execute_script("arguments[0].checked = false;", elem)

    # Try matching by 'value' attribute
    for elem in elements:
        elem_value = re.sub(r"\s+", " ", (elem.get_attribute("value") or "").strip().lower())
        if elem_value == btn_value_normalized:
            try:
                # Scroll into view first
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", elem)
                elem.click()
            except Exception as e:
                # If interrupted by overlay like 'dimbg', clear and try JS click
                print(f"[radio_btn_click] Click intercepted, attempting clearing and JS fallback: {e}")
                close_validation_popup(driver)
                driver.execute_script("arguments[0].click();", elem)
            return

    #print(f"[radio_btn_click] No matching radio found for value: {btn_value}")
    logger.log(
                    module="radio_btn_click",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"[radio_btn_click] No matching radio found for value: {btn_value}",
                    severity="INFO"
                )

# def data_filling_text(driver,data,elementlocator,selector):
#     selector_map=selector_mapping(selector)
#     element=find_elem(driver,selector_map,elementlocator)
#     element.clear() 
#     element.send_keys(str(data))

def data_filling_text(driver, data, elementlocator, selector):
    """
    Fills text-based input fields safely.
    Handles masked/currency/react-controlled inputs by triggering proper JS events.
    """

    if data in [None, ""]:
        return  # Skip empty data

    data = str(data).strip()
    selector_map = selector_mapping(selector)
    element = find_elem(driver, selector_map, elementlocator)

    try:
        # Scroll to element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        
        # Step 1: Try standard Selenium input
        try:
            element.clear()
            element.send_keys(data)
            
            # Trigger events
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, element)
        except Exception as e:
            # Fallback for hidden/read-only/blocked elements
            print(f"[data_filling_text] Selenium filling failed (state issue?), using JS fallback: {e}")
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, element, data)

        # Step 2: Verify value actually applied
        current_val = driver.execute_script("return arguments[0].value;", element)
        if current_val.strip() != data.strip():
            # Force injection if verification fails
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, element, data)

        # Optional: small delay to let UI stabilize (for portals with heavy JS)
        time.sleep(0.1)

    except Exception as e:
        #logging.error(f"[data_filling_text] Error filling element {elementlocator}: {e}")
        
        logger.log(
                    module="data_filling_text",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"[data_filling_text] Error filling element {elementlocator}: {e}",
                    severity="INFO"
           
        )


# def select_field(driver, data, elementlocator, selector):
#     try:
#         if data is None:
#             data = ""
#         else:
#             data = str(data).strip().lower()
#         selector_map = selector_mapping(selector)
#         element = find_elem(driver, selector_map, elementlocator)
        
#         # Scroll to element to ensure it's in view
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        
#         dropdown = Select(element)

#         # If multi-select, deselect all before picking
#         if dropdown.is_multiple:
#             dropdown.deselect_all()
        
#         # Loop through options and match by lowercase text (including empty string for blank options)
#         matched = False
#         for option in dropdown.options:
#             if option.text.strip().lower() == data:
#                 try:
#                     if option.text.strip() in ["","null"]:
#                         # select_by_visible_text("") fails in Selenium for blank options
#                         # Directly JS-click the option element to select it
#                         driver.execute_script("arguments[0].selected = true;", option)
#                     else:
#                         dropdown.select_by_visible_text(option.text)
#                 except Exception as click_err:
#                     print(f"[select_field] Selection intercepted, clearing overlays: {click_err}")
#                     close_validation_popup(driver)
#                     driver.execute_script("arguments[0].selected = true;", option)
                
#                 matched = True
#                 break
        
#         if matched:
#             # Trigger events to ensure portal Reacts
#             driver.execute_script("""
#                 arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
#                 arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
#             """, element)
#         else:
#             logger.log(
#                 module="select_field",
#                 order_id=hybrid_orderid,
#                 action_type="Condition-check",
#                 remarks=f"[select_field] No matching option found for: {data}",
#                 severity="INFO"
#             )
#     except Exception as e:
#         logger.log(
#             module="select_field",
#             order_id=hybrid_orderid,
#             action_type="Exception",
#             remarks=f"[select_field] Error selecting option: {e}",
#             severity="INFO"
#         )

def select_field(driver, data, elementlocator, selector):
    try:
        data = str(data).strip().lower()
        selector_map = selector_mapping(selector)
        element = find_elem(driver, selector_map, elementlocator)
        
        # Scroll to element to ensure it's in view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        
        dropdown = Select(element)

        # If multi-select, deselect all before picking
        if dropdown.is_multiple:
            dropdown.deselect_all()
        
        # Loop through options and match by lowercase text
        matched = False
        for option in dropdown.options:
            if option.text.strip().lower() == data:
                try:
                    dropdown.select_by_visible_text(option.text)
                except Exception as click_err:
                    print(f"[select_field] Selection intercepted, clearing overlays: {click_err}")
                    close_validation_popup(driver)
                    # Try selecting again or via JS
                    dropdown.select_by_visible_text(option.text)
                
                matched = True
                break
        
        if matched:
            # Trigger events to ensure portal Reacts
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, element)
        else:
            logger.log(
                module="select_field",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"[select_field] No matching option found for: {data}",
                severity="INFO"
            )
    except Exception as e:
        logger.log(
            module="select_field",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"[select_field] Error selecting option: {e}",
            severity="INFO"
        )

def select_empty_field(driver, data, elementlocator, selector):
    try:
        # ----------------------------
        # Normalize input data
        # ----------------------------
        if data is None or str(data).strip().lower() in ["", "none", "null"]:
            data = ""
        else:
            data = str(data).strip().lower()

        selector_map = selector_mapping(selector)
        element = find_elem(driver, selector_map, elementlocator)

        # Scroll into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element
        )

        dropdown = Select(element)

        # Handle multi-select
        if dropdown.is_multiple:
            dropdown.deselect_all()

        # ----------------------------
        # STEP 1: Handle EMPTY case
        # ----------------------------
        if data == "":
            try:
                dropdown.select_by_value("0")
            except Exception:
                # fallback using JS
                for option in dropdown.options:
                    if option.get_attribute("value") == "0":
                        driver.execute_script("arguments[0].selected = true;", option)
                        break

            # Trigger events
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, element)
            return

        # ----------------------------
        # STEP 2: Normal matching
        # ----------------------------
        matched = False

        for option in dropdown.options:
            text = option.text.strip().lower()
            value = option.get_attribute("value")

            # Handle % conversion (e.g., 50 → 50%)
            normalized_data = data
            if data.isdigit() and "%" in text:
                normalized_data = f"{data}%"

            if (
                text == data or
                text == normalized_data or
                value == data
            ):
                try:
                    dropdown.select_by_visible_text(option.text)
                except Exception as click_err:
                    print(f"[select_empty_field] Retry after popup: {click_err}")
                    close_validation_popup(driver)
                    driver.execute_script(
                        "arguments[0].value = arguments[1];",
                        element,
                        value
                    )

                matched = True
                break

        # ----------------------------
        # STEP 3: Fallback
        # ----------------------------
        if not matched:
            try:
                dropdown.select_by_value("0")
                print(f"[select_empty_field] Fallback default selected for: {data}")
            except Exception:
                print(f"[select_empty_field] No match and no default for: {data}")

        # ----------------------------
        # STEP 4: Trigger events
        # ----------------------------
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, element)

    except Exception as e:
        logger.log(
            module="select_empty_field",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"[select_empty_field] Error selecting option: {e}",
            severity="INFO"
        )

def find_elem(driver, selector, elementlocator):
    elementlocator = elementlocator.strip()
    element = driver.find_element(selector, elementlocator)
    return element

def selector_mapping(selector_type):
    
    selector = None
    
    if selector_type == "xpath":
        selector = By.XPATH
    elif selector_type == "id":
        selector = By.ID
    elif selector_type == "name":
        selector = By.NAME
    elif selector_type == "class_name":
        selector = By.CLASS_NAME
    elif selector_type == "tag_name":
        selector = By.TAG_NAME
    elif selector_type == "link_text":
        selector = By.LINK_TEXT
    elif selector_type == "partial_link_text":
        selector = By.PARTIAL_LINK_TEXT
    elif selector_type == "css_selector":
        selector = By.CSS_SELECTOR
    else:
        raise ValueError("Invalid selector type")
    return selector
def select_checkboxes_from_list(driver, values_list, id_prefix):
    """
    Select checkboxes based on a list of values using an ID prefix.
    Handles both unique ID formats (<id_prefix>_<value>) and shared ID/Name formats.

    Args:
        driver: Selenium WebDriver
        values_list: list of checkbox values to select (e.g. ['Insurance', 'Water'])
        id_prefix: prefix of the checkbox ID (e.g. "HOAInsurance")
    """
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    import re

    def sanitize(value):
        # Remove special characters and whitespace
        return re.sub(r'[^a-zA-Z0-9]', '', str(value))

    if not isinstance(values_list, list):
        if values_list:
            values_list = [values_list]
        else:
            return

    for value in values_list:
        try:
            value = str(value).strip()
            sanitized = sanitize(value)
            checkbox_id = f"{id_prefix}_{sanitized}"
            
            checkbox = None
            # Strategy 1: Attempt to find by prefixed ID (e.g., Insurance_Life)
            try:
                checkbox = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.ID, checkbox_id))
                )
            except TimeoutException:
                # Strategy 2: Attempt to find by shared ID/Name and value attribute
                # XPath to find input with matching id/name and value
                xpath = f"//input[(@type='checkbox' or @role='checkbox') and (@id='{id_prefix}' or @name='{id_prefix}') and (normalize-space(@value)='{value}' or normalize-space(..)='{value}')]"
                checkbox = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

            if checkbox:
                if not checkbox.is_selected():
                    try:
                        checkbox.click()
                    except:
                        driver.execute_script("arguments[0].click();", checkbox)
                    
                    logger.log(
                        module="select_checkboxes_from_list",
                        order_id=hybrid_orderid,
                        action_type="Condition-check",
                        remarks=f"Checked: {value} (using prefix {id_prefix})",
                        severity="INFO"
                    )
                else:
                    logger.log(
                        module="select_checkboxes_from_list",
                        order_id=hybrid_orderid,
                        action_type="Condition-check",
                        remarks=f"Already checked: {value}",
                        severity="INFO"
                    )
        except Exception as e:
            logger.log(
                module="select_checkboxes_from_list",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Checkbox for '{value}' not found or clickable with prefix '{id_prefix}'",
                severity="INFO"
            )



def single_checkbox(driver, data, element_locator, selector):
    """
    Sets a single checkbox state based on boolean-like data.
    
    Args:
        driver: Selenium WebDriver
        data: Value to decide check/uncheck (True/False, "Yes"/"No", etc.)
        element_locator: The locator string (ID, XPath, etc.)
        selector: The type of selector ("id", "xpath", etc.)
    """
    try:
        # Normalize data to boolean
        should_check = False
        if isinstance(data, bool):
            should_check = data
        elif str(data).strip().lower() in ["yes", "true", "1", "checked", "on"]:
            should_check = True

        selector_map = selector_mapping(selector)
        
        checkbox = None
        try:
            checkbox = find_elem(driver, selector_map, element_locator)
        except Exception:
            # Fallback: if ID fails, try XPath search for that ID (robust against special chars)
            if selector == "id":
                xpath_fallback = f"//*[@id=\"{element_locator}\"]"
                checkbox = driver.find_element(By.XPATH, xpath_fallback)
            else:
                raise

        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", checkbox)

        # Only click if state change is needed
        if checkbox.is_selected() != should_check:
            try:
                # Attempt standard click first
                checkbox.click()
            except Exception:
                close_validation_popup(driver)
                # Comprehensive JS fallback: set state AND dispatch events
                driver.execute_script("""
                    var elem = arguments[0];
                    var val = arguments[1];
                    elem.checked = val;
                    elem.dispatchEvent(new Event('change', { bubbles: true }));
                    elem.dispatchEvent(new Event('input', { bubbles: true }));
                    elem.dispatchEvent(new Event('click', { bubbles: true }));
                """, checkbox, should_check)

        logger.log(
            module="single_checkbox",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"Set checkbox {element_locator} to {should_check}",
            severity="INFO"
        )

    except Exception as e:
        logger.log(
            module="single_checkbox",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Error setting checkbox {element_locator}: {e}",
            severity="ERROR"
        )


# Mapping to normalize repair type differences between JSON and form text
repair_type_mapping = {
    "cleaningtrashremoval": "Cleaning/Trash Removal",
    "repairbid": "Repair Bid",
    "foundation": "Foundation",
    "landscaping": "Landscaping",
    "painting": "Painting",
    "roof": "Roof",
    "windows": "Windows",
    "pool": "Pool",
    "other": "Other"
}

def normalize(text):
    """Normalize text for matching: lowercase and remove non-alphanumeric chars."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())

def fill_repair_details(driver, repair_list):
    """
    Fill the exterior repair table based on JSON repair_list.
    repair_list = [
        {"repair_type": "repairbid", "comments": "some comment", "estimated_cost": 200},
        ...
    ]
    """
    rows = driver.find_elements(By.XPATH, "//table[@id='exteriorRepairTable']/tbody/tr")
    
    for repair in repair_list:
        # Normalize JSON repair_type and map to table text
        r_type_key = normalize(repair.get("repair_type"))
        r_type_form = repair_type_mapping.get(r_type_key)
        if not r_type_form:
            #print(f"Warning: Repair type '{repair.get('repair_type')}' has no mapping.")
            logger.log(
                    module="fill_repair_details",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Warning: Repair type '{repair.get('repair_type')}' has no mapping.",
                    severity="INFO"
           
        )
            continue

        comments = str(repair.get("comments", "")).strip()
        cost = str(repair.get("estimated_cost", "")).strip()

        matched = False

        for row in rows:
            type_elem = row.find_element(By.XPATH, "./td[1]/div")
            type_text = type_elem.text.strip()
            if type_text == r_type_form:
                # Fill comment
                comment_input = row.find_element(By.XPATH, ".//input[contains(@id,'RepairComment')]")
                comment_input.clear()
                if comments:
                    comment_input.send_keys(comments)
                
                # Fill amount
                amount_input = row.find_element(By.XPATH, ".//input[contains(@id,'Amount')]")
                amount_input.clear()
                if cost:
                    amount_input.send_keys(cost)
                
                matched = True
                break  # stop after filling this repair

        if not matched:
            #print(f"Warning: Repair type '{r_type_form}' not found in table.")
            logger.log(
                    module="fill_repair_details",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Warning: Repair type '{r_type_form}' not found in table.",
                    severity="INFO"
           
        )


# Map JSON repair types to portal input IDs
REPAIR_FIELD_MAP = {
    "Foundation": "PS_FORM/REPAIR_ADDENDUM/Foundation_Cost",
    "Landscaping": "PS_FORM/REPAIR_ADDENDUM/Landscaping_Cost",
    "Roof": "PS_FORM/REPAIR_ADDENDUM/Roof_Cost",
    "FireDamage": "PS_FORM/REPAIR_ADDENDUM/Fire_Damage",
    "ExteriorDoors": "PS_FORM/REPAIR_ADDENDUM/Exterior_Doors_Cost",
    "Garage": "PS_FORM/REPAIR_ADDENDUM/Garage_Cost",
    "Fencing": "PS_FORM/REPAIR_ADDENDUM/Fencing_Cost",
    "Siding/TrimRepair": "PS_FORM/REPAIR_ADDENDUM/Siding_Repair_Cost",
    "CleaningTrashRemoval": "PS_FORM/REPAIR_ADDENDUM/Landscaping_Cost",
    "Pool": "PS_FORM/REPAIR_ADDENDUM/Pool_Cost",
    "Painting": "PS_FORM/REPAIR_ADDENDUM/Exterior_Paint_Cost",
    "Windows": "PS_FORM/REPAIR_ADDENDUM/Windows_Cost",
    "Other":"PS_FORM/REPAIR_ADDENDUM/Exterior_Other1_Cost",
    "Other2":"PS_FORM/REPAIR_ADDENDUM/Exterior_Other2_Cost",
    "Other3":"PS_FORM/REPAIR_ADDENDUM/Exterior_Other3_Cost",
}

def SS_fill_repair_details(driver, repair_details):
    """
    Fill repair fields using JSON.
    Skips 'Other' entries and fills totalRepairCost from JSON.
    """
    if not isinstance(repair_details, dict):
        logging.error(f"Expected dict for repair_details, got {type(repair_details)}")
        return

    repairs_list = repair_details.get("repairs", [])
    total_cost_from_json = repair_details.get("totalRepairCost", "")

    for repair in repairs_list:
        repair_type = repair.get("repair_type")
        estimated_cost = repair.get("estimated_cost", "").strip()

        # Skip 'Other' repair types
        if repair_type not in REPAIR_FIELD_MAP:
            logging.info(f"Skipping repair type: {repair_type}")
            continue

        field_id = REPAIR_FIELD_MAP[repair_type]

        try:
            input_elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, field_id))
            )
            input_elem.clear()
            if estimated_cost:
                input_elem.send_keys(estimated_cost)
            logging.info(f"Filled {repair_type}: {estimated_cost}")
        except Exception as e:
            logging.error(f"Error filling {repair_type} ({field_id}): {e}")

    # Fill totalRepairCost
    if total_cost_from_json:
        try:
            total_elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "PS_FORM/REPAIR_ADDENDUM/Total_Estimated_Repairs"))
            )
            driver.execute_script("arguments[0].removeAttribute('readonly')", total_elem)
            total_elem.clear()
            total_elem.send_keys(str(total_cost_from_json).strip())
            logging.info(f"Updated Total_Estimated_Repairs with: {total_cost_from_json}")
        except Exception as e:
            logging.error(f"Error updating Total_Estimated_Repairs: {e}")


def rrr_fill_repair_details(driver, repair_list):
    """
    Fills Repair Information Tab (RRReview) ONLY for fields available in merged JSON.
    Missing portal fields remain blank.
    """

    # Portal fixed mapping
    portal_map = {
        "exteriorfinish": ("txtExteriorFinish", "txtExteriorFinishLow"),
        "painting": ("txtExteriorPainting", "txtExteriorPaintingLow"),
        "windows": ("txtExteriorWindows", "txtExteriorWindowsLow"),
        "roof": ("txtExteriorRoof", "txtExteriorRoofLow"),
        "structural": ("txtExteriorStructural", "txtExteriorStructuralLow"),
        "landscaping": ("txtExteriorLandscaping", "txtExteriorLandscapingLow"),
        "outbuildings": ("txtExteriorOutbuildings", "txtExteriorOutbuildingsLow"),
        "CleaningTrashRemoval": ("txtExteriorDebris_Removal", "txtExteriorDebris_RemovalLow"),
        "utility": ("txtExteriorUtility", "txtExteriorUtilityLow"),
        "other": ("txtExteriorOther", "txtExteriorOtherLow"),
    }

    def normalize(txt):
        if not txt:
            return ""
        return txt.lower().strip().replace(" ", "").replace("_", "")

    # Normalized portal mapping
    normalized_portal = {normalize(k): v for k, v in portal_map.items()}

    # RPAD repair list may contain only some fields
    for item in repair_list:
        r_type_raw = item.get("repair_type", "")
        r_type = normalize(r_type_raw)

        if r_type not in normalized_portal:
            continue  # skip items not relevant to portal

        desc_value = str(item.get("comments", "")).strip()
        cost_value = str(item.get("estimated_cost", "")).strip()

        desc_id, cost_id = normalized_portal[r_type]

        # Fill Description
        try:
            elem = driver.find_element(By.ID, desc_id)
            elem.clear()
            if desc_value:
                elem.send_keys(desc_value)
        except:
            pass

        # Fill Cost
        try:
            elem = driver.find_element(By.ID, cost_id)
            elem.clear()
            if cost_value:
                elem.send_keys(str(cost_value))
        except:
            pass
def rrr_fill_listing_history(driver, history_list, add_link_id, mode="id"):
    """
    Specialized helper for RRR Prior Listing History popups.
    Iterates through the history list, fills the modal fields, and clicks 'Save'.
    Handles the first record differently as 'Yes' radio might have already opened it.
    """
    if not history_list or not isinstance(history_list, list):
        print("--- [DEBUG] No prior history list to process.")
        return True

    # Check if 'Yes' (value 1) is actually selected before proceeding
    try:
        # ID is based on the radio button control 'rbl_ListingHistoryExists'
        yes_radio = driver.find_element(By.ID, "rbl_ListingHistoryExists_1")
        if not yes_radio.is_selected():
            print("--- [DEBUG] 'Yes' option Not selected for Prior Listing History. Skipping additional fill/clear logic.")
            return True
    except Exception as e:
        print(f"--- [DEBUG] Warning: Could not find/check 'Yes' radio status: {e}")
        # Proceed anyway as a fallback if we can't find the radio button
        pass

    # STEP 0: CLEAR existing records first (Fresh refill concept)
    try:
        # Loop until all 'Delete' links are gone
        while True:
            # We look for links with text 'Delete' and relaction='DELETE'
            delete_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Delete') and @relaction='DELETE']")
            if not delete_links:
                break # No more records to delete
            
            print(f"--- [DEBUG] Found {len(delete_links)} existing history record(s) to clear. Deleting first one...")
            
            # Click the first delete link found
            target_link = delete_links[0]
            # Use JS click as it's more stable for these small links
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link)
            driver.execute_script("arguments[0].click();", target_link)
            
            # Wait for and handle the confirmation alert
            try:
                alert_wait = WebDriverWait(driver, 5)
                alert = alert_wait.until(EC.alert_is_present())
                alert.accept()
                print("--- [DEBUG] Delete alert accepted.")
            except:
                # No alert or something went wrong?
                pass
                
            time.sleep(3) # Allow record to delete and table to refresh
    except Exception as e:
        print(f"--- [DEBUG] Error during Prior History clearing phase: {e}")

    # Process new records as before...

    for index, history in enumerate(history_list):
        if not history or not any(history.values()):
            continue
            
        print(f"--- [DEBUG] Processing Prior History entry {index + 1}...")

        # 1. Open the popup
        try:
            wait = WebDriverWait(driver, 10)
            popup_open = False
            
            # Check if popup is already open (Status dropdown is visible and displayed)
            try:
                status_elem = driver.find_element(By.ID, "ddl_slh_ListingStatus")
                if status_elem.is_displayed():
                    popup_open = True
                    print(f"--- [DEBUG] Popup for entry {index + 1} is already open.")
            except:
                pass

            if not popup_open:
                if index == 0:
                    # For the first record, clicking 'Yes' (if already yes) might re-trigger the popup
                    # or we use the 'Add New Record' link if the radio doesn't work.
                    print(f"--- [DEBUG] First record popup not open. Attempting 'Yes' radio click...")
                    try:
                        yes_radio = driver.find_element(By.ID, "rbl_ListingHistoryExists_1")
                        driver.execute_script("arguments[0].click();", yes_radio)
                        time.sleep(3)
                        # Check again
                        status_elem = driver.find_element(By.ID, "ddl_slh_ListingStatus")
                        if status_elem.is_displayed():
                            popup_open = True
                    except:
                        pass
                
                if not popup_open:
                    # Click Add New Record link
                    print(f"--- [DEBUG] Clicking '{add_link_id}' to open popup for record {index + 1}...")
                    selector = By.ID if mode == "id" else By.XPATH
                    add_link = wait.until(EC.element_to_be_clickable((selector, add_link_id)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_link)
                    driver.execute_script("arguments[0].click();", add_link)
                    
                    # Wait for popup elements to be visible
                    wait.until(EC.visibility_of_element_located((By.ID, "ddl_slh_ListingStatus")))
                    time.sleep(2) # Extra stabilization
        except Exception as e:
            print(f"--- [DEBUG] Error opening popup for record {index + 1}: {e}")
            continue

        # 2. Define field mappings (ID in popup : Key in backend data)
        mappings = {
            "ddl_slh_ListingStatus": "PriorStatus",
            "txt_slh_ListingStartDate": "PriorOriginalListDate",
            "txt_slh_SoldDate": "EndDate",
            "txt_slh_ListEndPrice": "EndPrice",
            "txt_slh_ListStartPrice": "PriorOriginalListPrice",
            "txt_slh_AgentName": "AgentName",
            "txt_slh_Agency": "Agency",
            "ddl_slh_SaleType": "SaleType",
            "txt_slh_Concessions": "Concessions",
            "ddl_slh_Financing": "Financing"
        }

        # 3. Fill the fields
        for elem_id, key in mappings.items():
            val = history.get(key)
            if val is None or val == "":
                continue
            
            try:
                elem = driver.find_element(By.ID, elem_id)
                tag = elem.tag_name.lower()
                if tag == "select":
                    select_field(driver, val, elem_id, "id")
                else:
                    data_filling_text(driver, val, elem_id, "id")
            except Exception as e:
                print(f"--- [DEBUG] Error filling {elem_id} with {val}: {e}")

        # 4. Click Save
        try:
            # Re-wait for save button to be sure
            save_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "saveButtonForNewLH"))
            )
            driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(2) # Wait for popup to close
        except Exception as e:
            print(f"--- [DEBUG] Error clicking Save in Prior History popup: {e}")

    return True


def rrr_select_hoa_amenities(driver, amenities_str, id_prefix, mode="id"):
    """
    Specialized helper for RRR HOA Amenities checkboxes.
    Maps text values to index-based IDs with a robust JS click and label fallback.
    CLEARS all checkboxes first, then selects only the ones from backend data.
    """
    if not amenities_str:
        return True

    print(f"--- [DEBUG] HOA Amenities processing started for: '{amenities_str}' using prefix '{id_prefix}'")

    # Portal index mapping (Order from HTML: Water, Cable, Trash, Maintenance, Security, Mowing, Snow Removal, Recreational Facilities)
    rrr_hoa_map = {
        "Water": "0",
        "Cable": "1",
        "Trash": "2",
        "Maintenance": "3",
        "Security": "4",
        "Mowing": "5",
        "Snow Removal": "6",
        "Recreational Facilities": "7"
    }
    
    # Create a lower-case version of the map for easier matching
    lookup_map = {k.lower(): v for k, v in rrr_hoa_map.items()}

    # Process input: handle string "water, trash" or list
    if isinstance(amenities_str, str):
        selected_items = [item.strip().lower() for item in amenities_str.split(",") if item.strip()]
    elif isinstance(amenities_str, list):
        selected_items = [str(item).strip().lower() for item in amenities_str]
    else:
        selected_items = []

    # Stabilization sleep
    time.sleep(2)

    # STEP 1: Uncheck ALL checkboxes first (clean slate)
    print(f"--- [DEBUG] [HOA] Clearing all checkboxes first...")
    for index in rrr_hoa_map.values():
        checkbox_id = f"{id_prefix}_{index}"
        try:
            checkbox = driver.find_element(By.ID, checkbox_id)
            if checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)
                print(f"--- [DEBUG] [HOA] Unchecked checkbox ID: {checkbox_id}")
        except Exception as e:
            # Checkbox might not exist, skip
            pass

    # STEP 2: Select only the checkboxes from backend data
    success = True
    for item in selected_items:
        found = False
        # 1. Attempt ID-based selection (Robust JS click + Scrolling)
        # item is already lowercased, check against lookup_map
        if item in lookup_map:
            index = lookup_map[item]
            checkbox_id = f"{id_prefix}_{index}"
            try:
                wait = WebDriverWait(driver, 5)
                checkbox = wait.until(EC.presence_of_element_located((By.ID, checkbox_id)))
                
                # Scroll and Click via JS
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                time.sleep(0.5)
                
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    print(f"--- [DEBUG] [ID Path] Selected '{item}' via JS ID: {checkbox_id}")
                else:
                    print(f"--- [DEBUG] [ID Path] '{item}' was already selected.")
                found = True
            except Exception as e:
                print(f"--- [DEBUG] [ID Path] Failed for {item} ({checkbox_id}): {e}")

        # 2. Attempt Label-based matching (robust fallback)
        if not found:
            print(f"--- [DEBUG] [Label Fallback] Trying label match for '{item}'...")
            try:
                labels = driver.find_elements(By.TAG_NAME, "label")
                for label in labels:
                    if item.lower() in label.text.lower():
                        label_for = label.get_attribute("for")
                        if label_for:
                            checkbox = driver.find_element(By.ID, label_for)
                            if not checkbox.is_selected():
                                driver.execute_script("arguments[0].click();", checkbox)
                            print(f"--- [DEBUG] [Label Path] Selected '{item}' via label match: '{label.text}' (ID: {label_for})")
                            found = True
                            break
            except Exception as e:
                print(f"--- [DEBUG] [Label Path] Failed for {item}: {e}")
        if not found:
            print(f"--- [DEBUG] WARNING: Could not find checkbox for HOA Amenity: '{item}'")
            # success = False 
    
    return True


def rrr_select_amenities(driver, values, locator, selector="xpath"):
    """
    Robust helper for RRReview amenities (Subject and Comps).
    Handles both ListBox (select) and CheckBoxList (table of checkboxes with labels).
    """
    if not values:
        return True
    
    # Ensure values is a list
    if isinstance(values, str):
        selected_items = [v.strip().lower() for v in values.split(",") if v.strip()]
    elif isinstance(values, list):
        selected_items = [str(v).strip().lower() for v in values]
    else:
        selected_items = []
        
    if not selected_items:
        return True

    try:
        element = find_elem(driver, selector, locator)
        tag_name = element.tag_name.lower()
        
        if tag_name == "select":
            # Multi-select ListBox
            dropdown = Select(element)
            if dropdown.is_multiple:
                dropdown.deselect_all()
            
            for item in selected_items:
                found = False
                for option in dropdown.options:
                    if item in option.text.lower():
                        dropdown.select_by_visible_text(option.text)
                        found = True
                        print(f"--- [DEBUG] Selected ListBox option: '{option.text}'")
                if not found:
                    print(f"--- [DEBUG] Could not find ListBox option for: '{item}'")
        else:
            # CheckBoxList - search for labels inside/near the element
            
            # STEP 1: Clear existing selections first (Clean Slate)
            try:
                existing_checkboxes = element.find_elements(By.TAG_NAME, "input")
                for cb in existing_checkboxes:
                    if cb.get_attribute("type") == "checkbox" and cb.is_selected():
                        driver.execute_script("arguments[0].click();", cb)
                print(f"--- [DEBUG] Cleared existing checkboxes in container: {locator}")
            except Exception as e:
                print(f"--- [DEBUG] Notice: Container clear skipped or failed: {e}")

            # STEP 2: Select the ones from backend data
            for item in selected_items:
                found = False
                try:
                    # Search specifically within the container for better performance and accuracy
                    labels = element.find_elements(By.TAG_NAME, "label")
                    for label in labels:
                        # CRITICAL: Remove spaces from both sides for flexible matching
                        # Backend: "Guest House" | Portal HTML: "GuestHouse"
                        # Without this normalization, the match FAILS and form becomes invalid
                        item_normalized = item.replace(" ", "")
                        label_normalized = label.text.lower().replace(" ", "")
                        if item_normalized in label_normalized:
                            label_for = label.get_attribute("for")
                            if label_for:
                                checkbox = driver.find_element(By.ID, label_for)
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].click();", checkbox)
                                print(f"--- [DEBUG] Selected Checkbox via label: '{label.text}' (ID: {label_for})")
                                found = True
                                break
                    
                    if not found:
                        # Fallback: search all labels on page if element search failed
                        all_labels = driver.find_elements(By.TAG_NAME, "label")
                        for label in all_labels:
                            if item in label.text.lower():
                                label_for = label.get_attribute("for")
                                if label_for:
                                    # locator might be an xpath like //*[@id='rrrSale1_lbAmenities']
                                    base_id = locator.replace("//*[@id='", "").replace("']", "")
                                    prefix = base_id.split("_")[0]
                                    if prefix in label_for:
                                        checkbox = driver.find_element(By.ID, label_for)
                                        if not checkbox.is_selected():
                                            driver.execute_script("arguments[0].click();", checkbox)
                                        print(f"--- [DEBUG] Selected Checkbox via global label fallback: '{label.text}' (ID: {label_for})")
                                        found = True
                                        break
                except Exception as e:
                    print(f"--- [DEBUG] Error matching label for '{item}': {e}")
                
                if not found:
                    print(f"--- [DEBUG] Could not find checkbox/label for amenity: '{item}'")

    except Exception as e:
        print(f"--- [DEBUG] Error in rrr_select_amenities: {e}")
        return False
        
    return True


def save_form(driver):
    
    try:
        time.sleep(5)
        element=driver.find_element(By.XPATH,"//*[@id='msg']")
        time.sleep(5)
        value1 = element.text  
        #logging.info("Extracted Value in the ok button click:{}".format((value1)))
        logger.log(
                    module="save_form",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Extracted Value in the ok button click:{format((value1))}",
                    severity="INFO"
           
        )
        time.sleep(3)
        if value1:
            driver.find_element(By.XPATH,"//*[@id='msg']/button").click()
            time.sleep(15)
            driver.find_element(By.XPATH,"//*[@id='btnSave']").click()
        else:
            driver.find_element(By.XPATH,"//*[@id='btnSave']").click()
            #logging.info("There is no OK button to click")
            logger.log(
                    module="save_form",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"There is no OK button to click",
                    severity="INFO"
           
        )
    except Exception as e:
    # value = element.text
        driver.find_element(By.XPATH,"//*[@id='btnSave']").click()
        #element=driver.find_element(By.XPATH,'//*[@id="SAVE_BPO"]/a')
        #element.click()

    #For msg click form
def save_form_adj(driver,order_id):
    try:
        element=driver.find_element(By.XPATH,"//*[@id='msg']")
        value1 = element.text  
        #logging.info("Extracted Value in the ok button click:{}".format((value1)))
        logger.log(
                    module="save_form_adj",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Extracted Value in the ok button click:{format((value1))}",
                    severity="INFO"
           
        )
        time.sleep(3)
        if value1:
            driver.find_element(By.XPATH,"//*[@id='msg']/button").click()
        else:
            #logging.info("There is no OK button to click")
            logger.log(
                    module="save_form_adj",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"There is no OK button to click",
                    severity="INFO"
           
        )
    except Exception as e:
        #logging.info(e)
        logger.log(
                    module="save_form_adj",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Exception-{e}",
                    severity="INFO"
           
        )
     
        
        
    #logging.info("order saved :{}".format(order_id))        
    logger.log(
                    module="save_form_adj",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"order saved :{format(order_id)}",
                    severity="INFO"
           
        )
         
   # logging.info("order saved :{}".format(order_id))
def update_order_status(assigned_order_id, status, stage, order_event_status,token):
   
    status_update_url = env.STATUS_UPDATE_URL

    params = {
        "assigned_order_id": assigned_order_id,
        "status": status,
        "stage": stage,
        "order_event_status": order_event_status,
        # "token":f"Bearer {token}"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(status_update_url, params=params, headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS", response.status_code)
        else:
            print(f"FAILURE {response.status_code}: {response.text}")

        #print(f"{order_event_status} status PUT response: {response.status_code} - {response.text}")
        #logging.info(f"{order_event_status} status PUT response: {response.status_code} - {response.text}")
        logger.log(
                    module="update_order_status",
                    order_id=assigned_order_id,
                    action_type="Condition-check",
                    remarks=f"{order_event_status} status PUT response: {response.status_code} - {response.text}",
                    severity="INFO"
           
        )
         
        return response
    except Exception as e:
        print(f"Exception in update_order_status: {e}")
        #print(f"Error while updating status via PUT: {e}")
        #logging.info((f"Error while updating status via PUT: {e}"))
        logger.log(
                    module="update_order_status",
                    order_id=assigned_order_id,
                    action_type="Exception",
                    remarks=f"Error while updating status via PUT: {e}",
                    severity="INFO"
           
        )
        return None

def update_client_account_status(client_account_id):
    
    url = f'{env.ACCOUNT_INACTIVE}{client_account_id}'
    action_required_reason="login error"
    payload = {
        "action_required_reason": action_required_reason
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        #print(f"PUT status response: {response.status_code} - {response.text}")
        logger.log(
                    module="update_client_account_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"PUT status response: {response.status_code} - {response.text}",
                    severity="INFO"
           
        )
        return response
    except Exception as e:
        #print(f"Error while updating client account status: {e}")
        logger.log(
                    module="update_client_account_status",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Error while updating client account status: {e}",
                    severity="INFO"
           
        )
        return None


def fetch_upload_data(self, order_id: int):
    COMP_UPLOAD_URL = f'{env.PIC_PDF_UPLOAD_URL}{order_id}'

    try:
        response = requests.get(COMP_UPLOAD_URL)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        #print(f" Failed to fetch data from API: {e}")
        logger.log(
                    module="fetch_upload_data",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f" Failed to fetch data from API: {e}",
                    severity="INFO"
           
        )
        return None

    content = json_data.get("content", {}).get("data", {})
    documents = content.get("documents", [])
    comparables_folder = content.get("comparables", "")
    rental_folder = content.get("rental", "")
    signature_folder=content.get("signature","")
    item_id = content.get("itemId")

    return {
        "documents": documents,
        "comparables_folder": comparables_folder,
        "rental_folder": rental_folder,
        "signature_folder":signature_folder,
        "item_id": item_id
    }

def list_files_from_server(folder: str):
    """
    Fetches the list of files from the file server API for the given folder.
    Returns a list of filenames.
    """
    url = f"{env.FILE_SERVER_URL}{folder}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()   # server should return JSON
        # Assuming response: {"files": ["a1.jpg", "a2.jpg", "s1.jpg"]}
        return data.get("files", [])
    except Exception as e:
        #print(f"Error fetching files from server: {e}")
        logger.log(
                    module="list_files_from_server",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f" Error fetching files from server: {e}",
                    severity="INFO"
           
        )
        return []

label_to_file_map = {}
def extract_data_sections(merged_json):
    """
    Extract key data sections from merged_json.
    """
    entry_data = merged_json.get("entry_data", [])
    if not entry_data:
        return (None,) * 23

    first_entry = entry_data[0]  # usually only one or focus on first

    sub_data = first_entry.get("sub_data", {})
    comp_data = first_entry.get("comp_data", {})
    adj_data = first_entry.get("adj_data", {})
    rental_data = first_entry.get("rental_data", {})
    
    # Extract Subject Prior History and flatten first 3 entries
    history_list = sub_data.get("SubjectPriorHistory", [])
    prior1 = history_list[0] if len(history_list) > 0 else {}
    prior2 = history_list[1] if len(history_list) > 1 else {}
    prior3 = history_list[2] if len(history_list) > 2 else {}

    sold1 = comp_data.get("Sold 1", {})
    sold2 = comp_data.get("Sold 2", {})
    sold3 = comp_data.get("Sold 3", {})
    list1 = comp_data.get("List 1", {})
    list2 = comp_data.get("List 2", {})
    list3 = comp_data.get("List 3", {})
    rental_list1=rental_data.get("List 1", {})
    rental_list2=rental_data.get("List 2", {})
    rental_leased1=rental_data.get("Leased 1", {}) 
    rental_leased2=rental_data.get("Leased 2", {}) 
    adj_sold1=adj_data.get("Sold Comp1", {})
    adj_sold2=adj_data.get("Sold Comp2", {})
    adj_sold3=adj_data.get("Sold Comp3", {})
    adj_list1=adj_data.get("Listed Comp1", {})
    adj_list2=adj_data.get("Listed Comp2", {})
    adj_list3=adj_data.get("Listed Comp3", {})

    return (sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3, 
            rental_list1, rental_list2, rental_leased1, rental_leased2, adj_sold1, adj_sold2, adj_sold3, 
            adj_list1, adj_list2, adj_list3, prior1, prior2, prior3)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# def single_source_save_form(driver):
    
#     try:
#         element=driver.find_element(By.XPATH,"/html/body/form/div[4]/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td[2]")
#         value1 = element.text
#         logging.info("Extracted Value in the ok button click:{}".format((value1)))
#         time.sleep(3)
#         if value1:
#             driver.find_element(By.XPATH,"/html/body/form/div[4]/table/tbody/tr[2]/td/table/tbody/tr/td/a").click()
#             time.sleep(15)
#             driver.switch_to.parent_frame()
#             time.sleep(1) 
#             driver.switch_to.frame("_TOP_MENU")
#             time.sleep(1) 
#             element=driver.find_element(By.XPATH,'//*[@id="SAVE_BPO"]/a')
#             element.click()
#             time.sleep(15)
#             driver.switch_to.parent_frame()
#             time.sleep(1) 
#             driver.switch_to.frame("_MAIN")
#             time.sleep(1)
#             try:
#                 element=driver.find_element(By.XPATH,"//*[@id='form_viewer']/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr/td[4]")
#                 value2 = element.text
                
#                 if value2:
#                     logging.info("order saved successfully")
#                     pass
#                 else:
#                     time.sleep(10)
#             except:
#                 pass
#         else:
#             logging.info("There is no OK button to click")
#     except Exception as e:
#     # value = element.text
#         logging.info("No need to click ok button :{}".format(e))
#         time.sleep(4)
#         driver.switch_to.parent_frame()
#         time.sleep(1) 
#         driver.switch_to.frame("_TOP_MENU")
#         time.sleep(1) 
#         element=driver.find_element(By.XPATH,'//*[@id="SAVE_BPO"]/a')
#         element.click()
#         time.sleep(15) 
#         driver.switch_to.parent_frame()
#         time.sleep(1) 
#         driver.switch_to.frame("_MAIN")
#         time.sleep(1)
#         try:
#             element=driver.find_element(By.XPATH,"//*[@id='form_viewer']/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr/td[4]")
#             value2 = element.text
#             if value2:
#                     logging.info("order saved successfully")
#                     pass
#             else:
#                     time.sleep(10)
#         except:
#             pass
        
#     logging.info("order saved")


def single_source_save_form(driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    def switch_to_frame(frame_name):
        driver.switch_to.default_content()
        driver.switch_to.frame(frame_name)

    try:
        # Step 1: Check for OK button/value in _MAIN frame
        switch_to_frame("_MAIN")
        try:
            ok_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "/html/body/form/div[4]/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td[2]"))
            )
            if ok_elem.text.strip():
                logging.info(f"OK button detected with value: {ok_elem.text}")
                ok_button = driver.find_element(By.XPATH, "/html/body/form/div[4]/table/tbody/tr[2]/td/table/tbody/tr/td/a")
                ok_button.click()
        except:
            logging.info("No OK button found; continuing to SAVE")

        # Step 2: Click SAVE via JavaScript in _TOP_MENU frame
        switch_to_frame("_TOP_MENU")
        wait.until(lambda d: d.execute_script("return typeof toolBarClick !== 'undefined';"))
        driver.execute_script("toolBarClick(462, 'SAVE_BPO');")
        logging.info("SAVE button clicked via JavaScript")

        # Step 3: Verify order saved in _MAIN frame
        switch_to_frame("_MAIN")
        saved_elem = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='form_viewer']/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr/td[4]"))
        )
        if saved_elem.text.strip():
            logging.info("Order saved successfully")
        else:
            logging.warning("Order might not be saved: value missing")

    except Exception as e:
        logging.error(f"Error while saving order: {e}")


def load_form_config_and_data(order_id, config_path, researchpad_data_retrival_url,
                            session=None, merged_json=None,token=None):


    try:
        with open(resource_path(config_path), 'r') as f:
            form_config = json.load(f)
    except Exception as e:
        logger.log(
                    module="load_form_config_and_data",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f" Failed to load form config JSON: {e}",
                    severity="INFO"
           
        )
        #logging.error(f"Failed to load form config JSON: {e}")
        update_order_status(order_id, "In Progress", "Entry", "Failed",token)
        return None, None

    if session is None:
        session = requests.Session()

    if not merged_json:
        url = f"{researchpad_data_retrival_url}?order_id={order_id}"
        logger.log(
                    module="load_form_config_and_data",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f" Fetching merged_json from API: {url}",
                    severity="INFO"
           
        )
        #logging.info(f"Fetching merged_json from API: {url}")
        try:
            response = session.get(url)
            if response.status_code == 200:
                merged_json = response.json()
            else:
                #logging.error(f"Failed to fetch merged_json, status code: {response.status_code}")
                logger.log(
                    module="load_form_config_and_data",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f" Failed to fetch merged_json, status code: {response.status_code}",
                    severity="INFO"
           
        )
                update_order_status(order_id, "In Progress", "Entry", "Failed",token)
                return None, None
        except Exception as e:
            #logging.error(f"Exception during API call: {e}")
            logger.log(
                    module="load_form_config_and_data",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Exception during API call: {e}",
                    severity="INFO"
           
        )
            update_order_status(order_id, "In Progress", "Entry", "Failed",token)
            return None, None
    
    return form_config, merged_json
    
def get_nested(data, path_list, default=""):
    """Safely get nested dictionary data with a list of keys."""
    for key in path_list:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

from selenium.common.exceptions import TimeoutException, NoSuchElementException
def close_validation_popup(driver, timeout=5):
    """
    Detect and close the SingleSource validation popup if it appears.
    Also handles hiding the 'dimbg' overlay if it persists.
    """
    try:
        # 1. Try to find and click the OK button in the validation panel
        ok_selectors = [
            (By.CSS_SELECTOR, "#OK a.button"),
            (By.XPATH, "//div[@id='validation_panel']//button"),
            (By.XPATH, "//div[@id='validation_panel']//a[contains(text(), 'OK')]"),
            (By.XPATH, "//div[@id='msg']//button"),
        ]
        
        popup_found = False
        for by, selector in ok_selectors:
            try:
                ok_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((by, selector))
                )
                driver.execute_script("arguments[0].click();", ok_button)
                print(f" Validation popup closed via {selector}.")
                popup_found = True
                break
            except:
                continue

        # 2. Force-hide the overlays if they are blocking
        # Added 'image_modal' and broad cleanup
        driver.execute_script("""
            ['dimbg', 'validation_panel', 'image_modal', 'ui-widget-overlay'].forEach(id => {
                var el = document.getElementById(id) || document.querySelector('.' + id);
                if (el) { 
                    el.style.display = 'none'; 
                    el.style.visibility = 'hidden'; 
                    el.style.zIndex = '-1';
                }
            });
        """)

        return popup_found
    except Exception as e:
        print(f" Error in close_validation_popup: {e}")
        return False
    

def tfs_statuschange(tfs_order_id, bpo_statusid, tfs_status, tfs_status_reason):
    '''Status change on TFS'''

    tfs_order_id = str(tfs_order_id).strip()
    bpo_statusid = str(bpo_statusid).strip()
    tfs_status = str(tfs_status).strip()
    tfs_status_reason = str(tfs_status_reason).strip()
    EmpId="11023"
   
    try:
        tfs_status_data = {
            "strSessionID": "",
            "ProcParameters": ["type", "sTFStatusData", "stfsOrderId", "sEmpId"],
            "ProcInputData": [1, f"{tfs_status}~{tfs_status_reason}~", tfs_order_id, EmpId]
        }

        bpo_status_data = {
            "strSessionID": "",
            "ProcInputData": [f"{bpo_statusid}~Na~Na~", tfs_order_id, EmpId],
            "ProcParameters": ["sAutoBPOdata", "sOrderId", "sEmpId"]
        }
        
        tfs_statuschange_url = env.tfs_statuschange_url
        tfs_status_resp = requests.post(tfs_statuschange_url,data=tfs_status_data)
        logger.log(module="tfs_statuschange", order_id=hybrid_orderid, action_type="Status-change", remarks=f"tfs_statuschange_response :{tfs_status_resp.text} , ordID {tfs_order_id}",severity="INFO")

        bpo_statuschange_url = env.bpo_statuschange_url
        bpo_status_resp = requests.post(bpo_statuschange_url,data=bpo_status_data)
        logger.log(module="tfs_statuschange", order_id=hybrid_orderid, action_type="Status-change", remarks=f"bpo_statuschange_response :{bpo_status_resp.text} , ordID: {tfs_order_id}",severity="INFO")

        logger.log(module="tfs_statuschange", order_id=hybrid_orderid, action_type="Status-change",remarks="Status changed succesfully",severity="INFO")
        return

    except Exception as error:
        logger.log(module="tfs_statuschange", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception on status changing: {error}",severity="INFO")
        return


def update_portal_login_confirmation_status(order_id):
    try:
        url = env.PORTAL_LOGIN_CONFIRMATION + str(order_id)
        response = requests.put(url)
        
        if response.status_code == 200:
            data = response.json()
            #logging.info(f"Portal login update success: {data}")
            logger.log(
                    module="update_portal_login_confirmation_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Portal login update success: {data}",
                    severity="INFO"
           
        )
            return True
        else:
            #logging.error(f"Portal login update failed: {response.status_code}")
            logger.log(
                    module="update_portal_login_confirmation_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Portal login update failed: {response.status_code}",
                    severity="INFO"
           
        )
            return False

    except Exception as e:
        #logging.error(f"Exception occurred: {e}")
        logger.log(
                    module="update_portal_login_confirmation_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Exception occurred: {e}",
                    severity="INFO"
           
        )
        return False

def select_radio_button(driver, btn_value, element_identifier, span_xpath, disagree_xpath, element_type):
    selector_map = selector_mapping(element_type)
    try:
        elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((selector_map, span_xpath)))
        element_agree = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, element_identifier)))
        element_disagree = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, disagree_xpath)))
        
        for element in elements:
            if element.text == btn_value:
                driver.execute_script("arguments[0].click();", element_agree)
                logger.log(
                    module="select_radio_button",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Agree selected: {btn_value}",
                    severity="INFO"
                )
                return
        
        # Click disagree if the value is not found
        driver.execute_script("arguments[0].click();", element_disagree)
        logger.log(
            module="select_radio_button",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"Disagree selected: {btn_value}",
            severity="INFO"
        )
        
    except NoSuchElementException as e:
        logger.log(
            module="select_radio_button",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Element not found: {e}",
            severity="INFO"
        )
    except ElementClickInterceptedException as e:
        logger.log(
            module="select_radio_button",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Element click intercepted: {e}",
            severity="INFO"
        )
    except Exception as e:
        logger.log(
            module="select_radio_button",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"An error occurred: {e}",
            severity="INFO"
        )

def select_drop_button(driver, btn_value, element_identifier, span_xpath, dropdown_xpath, element_type):
    selector_map = selector_mapping(element_type)
    try:
        elements = driver.find_elements(selector_map, span_xpath)
        dropdown_element = driver.find_element(By.XPATH, element_identifier)
        
        for element in elements:
            if element.text != btn_value:
                select = Select(dropdown_element)
                select.select_by_visible_text('Tax Records')
                
                input_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                )
                input_element.clear()
                input_element.send_keys("Verified From Tax")
                return

        # If btn_value is not found, you might want to handle it
        logger.log(
            module="select_drop_button",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"Value not found in dropdown: {btn_value}",
            severity="INFO"
        )

    except Exception as e:
        logger.log(
            module="select_drop_button",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"An error occurred: {e}",
            severity="INFO"
        )


