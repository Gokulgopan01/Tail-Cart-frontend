import json
import os
import re
import time
import traceback
from venv import logger
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    else:
          #return None,None  
          # Returns auto for manualy opening Autologin  
          return "AutoLogin",None,None   
process_type, hybrid_orderid,hybrid_token = params_check()



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


def get_saved_token():
    app_data_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "HybridBPO")
    #print(app_data_dir)
    logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"app_data_dir-{app_data_dir}",
                    severity="INFO"
                )
    os.makedirs(app_data_dir, exist_ok=True)  # Make sure the directory exists

    # Final path: C:\Users\<User>\AppData\Roaming\HybridBPO\login_data.json
    login_data_file = os.path.join(app_data_dir, "login_data.json")
    try:
        if not os.path.exists(login_data_file):
            #print("Token file does not exist.")
            logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Token file does not exist.",
                    severity="INFO"
                )
            return None

        with open(login_data_file, "r") as file:
            content = file.read().strip()
            if not content:
                #print("Token file is empty.")
                logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Token file is empty.",
                    severity="INFO"
                )
                return None

            data = json.loads(content)
            token = data.get("token", None)
            if token:
                #print("Token loaded successfully.")
                logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Token loaded successfully.",
                    severity="INFO"
                )
            else:
                #print("Token missing in file.")
                logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Token missing in file.",
                    severity="INFO"
                )
            return token

    except (json.JSONDecodeError, ValueError):
        print(" Corrupted token file.")
        logger.log(
                    module="get_saved_token",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Corrupted token file.",
                    severity="INFO"
                )
        return None


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
                return portal_order_id, tfs_orderid
            else:
                logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Invalid Response Format.",
                    severity="INFO"
                )
                return "Invalid Response Format"
                
        else:
            logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Error: {response.status_code} - {response.text}",
                    severity="INFO"
                )
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        logger.log(
                    module="get_order_address_from_assigned_order",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Request Failed: {str(e)}",
                    severity="INFO"
                )
        return f"Request Failed: {str(e)}"
        


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

    script = f"""
        var el = document.evaluate("{elementlocator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (el) {{
            el.value = '';  // Clear existing value
            el.dispatchEvent(new Event('input'));  // Trigger input event
            el.value = '{data}';  // Refill with new value
            el.dispatchEvent(new Event('input'));
            el.dispatchEvent(new Event('change'));  // Trigger change event to ensure UI reacts
        }}
    """
    driver.execute_script(script)

   
def adj_click(driver,data,element_identifier,element_type):
    selector_map=selector_mapping(element_type)
    element=driver.find_elements(selector_map,element_identifier)
    for x in element:
        x.click()



def radio_btn_click(driver, btn_value, element_identifier, element_type):
    """
    Deselect any selected radio first, then select the one with the matching value.
    Handles trimming and &nbsp;.
    """
    selector_map = selector_mapping(element_type)
    elements = driver.find_elements(selector_map, element_identifier)
    # Always convert input to string before normalization
    btn_value_normalized = re.sub(r"\s+", " ", str(btn_value).strip().lower())

    # Deselect all first
    for elem in elements:
        if elem.is_selected():
            driver.execute_script("arguments[0].checked = false;", elem)

    # Try matching by 'value' attribute
    for elem in elements:
        elem_value = re.sub(r"\s+", " ", (elem.get_attribute("value") or "").strip().lower())
        if elem_value == btn_value_normalized:
            elem.click()
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

    data = str(data)
    selector_map = selector_mapping(selector)
    element = find_elem(driver, selector_map, elementlocator)

    try:
        # Step 1: Try standard Selenium input
        element.clear()
        element.send_keys(data)

        # Step 2: Trigger input/change events (for JS/React binding)
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, element)

        # Step 3: Verify value actually applied
        current_val = driver.execute_script("return arguments[0].value;", element)
        if current_val.strip() != data.strip():
            # Step 4: Fallback to JavaScript injection
            driver.execute_script("""
                arguments[0].value = '';
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
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


def select_field(driver, data, elementlocator, selector):
    try:
        data = data.strip().lower()
        dropdown = Select(find_elem(driver, selector, elementlocator))

        # If multi-select, deselect all before picking
        if dropdown.is_multiple:
            dropdown.deselect_all()
        
        # Loop through options and match by lowercase text
        for option in dropdown.options:
            if option.text.strip().lower() == data:
                dropdown.select_by_visible_text(option.text)
                return
        #print(f"[select_field] No matching option found for: '{data}'")
        logger.log(
                    module="select_field",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"[select_field] No matching option found for: {data}",
                    severity="INFO"
           
        )
    except Exception as e:
        data='' 
        #print(f"[select_field] Error selecting option: {e}")
        logger.log(
                    module="select_field",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"[select_field] Error selecting option: {e}",
                    severity="INFO"
           
        )


def find_elem(driver,selector,elementlocator):
    
    element=driver.find_element(selector,elementlocator)
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
    Each checkbox should have an ID like: <id_prefix>_<sanitized_value>

    Args:
        driver: Selenium WebDriver
        values_list: list of checkbox values to select (e.g. ['Insurance', 'Water'])
        id_prefix: prefix of the checkbox ID (e.g. "HOAInsurance")
    """
    from selenium.common.exceptions import NoSuchElementException
    import re
    from selenium.common.exceptions import TimeoutException

    def sanitize(value):
        # Remove special characters and whitespace
        return re.sub(r'[^a-zA-Z0-9]', '', str(value))

    for value in values_list:
        try:
            sanitized = sanitize(value)
            checkbox_id = f"{id_prefix}_{sanitized}"
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, checkbox_id))
            )
            if not checkbox.is_selected():
                checkbox.click()
                #logging.info(f"Checked: {checkbox_id}")
                logger.log(
                    module="select_checkboxes_from_list",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Checked: {checkbox_id}",
                    severity="INFO"
           
        )
            else:
                #logging.info(f"Already checked: {checkbox_id}")
                logger.log(
                    module="select_checkboxes_from_list",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Already checked: {checkbox_id}",
                    severity="INFO"
           
        )
        except TimeoutException:
            #logging.warning(f"Checkbox not found (timeout): {checkbox_id}")
            logger.log(
                    module="select_checkboxes_from_list",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Checkbox not found (timeout): {checkbox_id}",
                    severity="INFO"
           
        )
        except Exception as e:
            #logging.error(f"Error clicking checkbox {checkbox_id}: {e}")
            logger.log(
                    module="select_checkboxes_from_list",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Error clicking checkbox {checkbox_id}: {e}",
                    severity="INFO"
           
        )

# def fill_repair_details(driver, repair_list):
#     for idx, repair in enumerate(repair_list):
#         try:
#             comment_xpath = f"//input[@id='ExteriorRepairList_{idx}__RepairComment']"
#             cost_xpath = f"//input[@id='ExteriorRepairList_{idx}__Amount']"

#             # Fill comments
#             comment_elem = driver.find_element(By.XPATH, comment_xpath)
#             comment_elem.clear()
#             comment_elem.send_keys(repair.get("comments", ""))

#             # Fill estimated cost
#             cost_elem = driver.find_element(By.XPATH, cost_xpath)
#             cost_elem.clear()
#             cost_elem.send_keys(str(repair.get("estimated_cost", "")))

#         except Exception as e:
#             logging.error(f"Error filling repair at index {idx} ({repair.get('repair_type')}): {e}")

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

        comments = repair.get("comments", "")
        cost = str(repair.get("estimated_cost", ""))

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
            total_elem.send_keys(str(total_cost_from_json))
            logging.info(f"Updated Total_Estimated_Repairs with: {total_cost_from_json}")
        except Exception as e:
            logging.error(f"Error updating Total_Estimated_Repairs: {e}")


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
        "order_event_status": order_event_status
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(status_update_url, params=params, headers=headers)
        #print(f"{order_event_status} status PUT response: {response.status_code} - {response.text}")
        #logging.info(f"{order_event_status} status PUT response: {response.status_code} - {response.text}")
        logger.log(
                    module="update_order_status",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"{order_event_status} status PUT response: {response.status_code} - {response.text}",
                    severity="INFO"
           
        )
         
        return response
    except Exception as e:
        #print(f"Error while updating status via PUT: {e}")
        #logging.info((f"Error while updating status via PUT: {e}"))
        logger.log(
                    module="update_order_status",
                    order_id=hybrid_orderid,
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
    item_id = content.get("itemId")

    return {
        "documents": documents,
        "comparables_folder": comparables_folder,
        "rental_folder": rental_folder,
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
        return None, None, None, None

    first_entry = entry_data[0]  # usually only one or focus on first

    sub_data = first_entry.get("sub_data")
    comp_data = first_entry.get("comp_data")
    adj_data = first_entry.get("adj_data")
    rental_data = first_entry.get("rental_data")
    sold1 = comp_data.get("Sold 1")
    sold2 = comp_data.get("Sold 2")
    sold3 = comp_data.get("Sold 3")
    list1 = comp_data.get("List 1")
    list2 = comp_data.get("List 2")
    list3 = comp_data.get("List 3")
    rental_list1=rental_data.get("List 1")
    rental_list2=rental_data.get("List 2")
    rental_leased1=rental_data.get("Leased 1") 
    rental_leased2=rental_data.get("Leased 2") 
    adj_sold1=adj_data.get("Sold Comp1")
    adj_sold2=adj_data.get("Sold Comp2")
    adj_sold3=adj_data.get("Sold Comp3")
    adj_list1=adj_data.get("Listed Comp1")
    adj_list2=adj_data.get("Listed Comp2")
    adj_list3=adj_data.get("Listed Comp3")

    return sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3


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
    
    :param driver: Selenium WebDriver instance
    :param timeout: Max seconds to wait for popup
    :return: True if popup was found and closed, False otherwise
    """
    try:
        ok_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#OK a.button"))
        )
        ok_button.click()
        print(" Validation popup closed.")
        return True
    except (TimeoutException, NoSuchElementException):
        # Popup not present
        print(" No validation popup detected.")
        return False
    
import requests
import logging
import time


def tfs_statuschange(tfs_order_id,bpo_statusid,tfs_status,tfs_status_reason):
   
    try:
        
                
                data={
                    "strSessionID":"",
                    "ProcParameters":["type","sTFStatusData","stfsOrderId"],
                    "ProcInputData":[1,f"{tfs_status}~{tfs_status_reason}~",tfs_order_id]
                    }

                data1={
                    "strSessionID":"",
                    "ProcInputData": [f"{bpo_statusid}~Na~Na~",tfs_order_id],
                    "ProcParameters": ["sAutoBPOdata", "sOrderId"]
                    }
                
                #response2=requests.post("https://bpotrackers.com/bvupcqp/home/ProcUpdateTFSstatusEntry",data=data)
                response2=requests.post("http://tfs-sandbox.ecesistech.com/autobpo_test/Home/ProcUpdateTFSstatusEntry",data=data)                
                #logging.info(f"response2 :{response2.text} , ordID {tfs_order_id}")
                logger.log(
                    module="tfs_statuschange",
                    order_id=hybrid_orderid,
                    action_type="Status-change",
                    remarks=f"response2 :{response2.text} , ordID {tfs_order_id}",
                    severity="INFO"
           
        )

                #response1 =requests.post("https://bpotrackers.com/bvupcqp/Home/ProcUpdateAutoEntry",data=data1)
                response1 =requests.post("http://tfs-sandbox.ecesistech.com/autobpo_test/Home/ProcUpdateAutoEntry",data=data1)
          
                #logging.info(f"response1 :{response1.text} , ordID: {tfs_order_id}")
                logger.log(
                    module="tfs_statuschange",
                    order_id=hybrid_orderid,
                    action_type="Status-change",
                    remarks=f"response1 :{response1.text} , ordID: {tfs_order_id}",
                    severity="INFO"
           
        )

            
                #print("Status changed succesfully")
                #logging.info("Status changed succesfully")
                logger.log(
                    module="tfs_statuschange",
                    order_id=hybrid_orderid,
                    action_type="Status-change",
                    remarks=f"Status changed succesfully",
                    severity="INFO"
           
        )


            
    except Exception as error:
        #logging.info(f"Exception occured on sttaus change {error}")
        logger.log(
                    module="tfs_statuschange",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Status changed succesfully",
                    severity="INFO"
           
        )

def update_portal_login_confirmation_status(order_id):
    try:
        url = env.PORTAL_LOGIN_CONFIRMATION + str(order_id)
        response = requests.get(url)
        
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

    
