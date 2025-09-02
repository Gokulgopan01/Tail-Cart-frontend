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
import logging
from selenium.webdriver.chrome.service import Service
import logging
from tkinter import Image, messagebox
import sys
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from config import env



# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = env.ASSIGNEDORDERS_URL   

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



def handle_login_status(login_title_or_url, username,login_check_keywords, portal_name):
    """Handle login success or failure by checking the current URL."""

    # Check if the current URL contains any of the success indicators
    if any(keyword in login_title_or_url for keyword in login_check_keywords):
        logging.info(f"Successfully logged in to {portal_name} as {username}.")
        messagebox.showinfo("Login Successful", f"Successfully logged in to {portal_name} .")
    else:
        logging.error(f"Login failed for {username} on {portal_name}. Possible incorrect credentials or login issue.")
        messagebox.showerror("Login Failed", "Invalid credentials or login error for {portal_name}.")
        
        

def handle_exception(self, e):
        """Handle exceptions and log the error."""
        stack_trace = traceback.format_exc()
        if stack_trace:
            e = stack_trace
        self.update_report_data(None, str(e), 'UNABLE TO LOGIN')        


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
    print(app_data_dir)
    os.makedirs(app_data_dir, exist_ok=True)  # Make sure the directory exists

    # Final path: C:\Users\<User>\AppData\Roaming\HybridBPO\login_data.json
    login_data_file = os.path.join(app_data_dir, "login_data.json")
    try:
        if not os.path.exists(login_data_file):
            print("Token file does not exist.")
            return None

        with open(login_data_file, "r") as file:
            content = file.read().strip()
            if not content:
                print("Token file is empty.")
                return None

            data = json.loads(content)
            token = data.get("token", None)
            if token:
                print("Token loaded successfully.")
            else:
                print("Token missing in file.")
            return token

    except (json.JSONDecodeError, ValueError):
        print(" Corrupted token file.")
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
                return data["content"]["data"].get("portal_order_id", "Address Not Found")
            else:
                return "Invalid Response Format"
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
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




def get_cookie_from_api(username, portal="rrr", proxy=None):
    try:
        session = requests.Session()
        if proxy:
            session.proxies.update({
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            })
            logging.info(f"Using proxy: {proxy}")

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
        logging.error(f"API request failed: {e}")
        return None
    
def setup_driver(self):
    try:
        self.login_status = "Starting login process"

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")

        if hasattr(self, 'proxy') and self.proxy:
            logging.info(f"Using proxy: {self.proxy}")
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
        else:
            logging.info("No proxy provided. Continuing without proxy.")

        self.driver = webdriver.Chrome(options=chrome_options)
        logging.info("Chrome driver initialized successfully.")


    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {e}")
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

# import re

# def javascript_excecuter_filling(driver, data, elementlocator, selector):
#     if not data:
#         return

#     # Single regex to escape all special JS chars inside single-quoted string
#     data = re.sub(
#         r"[\\'\n\r\t\b\f\"]",
#         lambda m: {
#             '\\': r'\\',
#             '\'': r'\'',
#             '\n': r'\n',
#             '\r': r'\r',
#             '\t': r'\t',
#             '\b': r'\b',
#             '\f': r'\f',
#             '"': r'\"',
#         }[m.group()],
#         str(data)
#     )

#     script = f"""
#         var el = document.evaluate("{elementlocator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#         if (el) {{
#             el.value = '';  // Clear existing value
#             el.dispatchEvent(new Event('input'));  // Trigger input event
#             el.value = '{data}';  // Refill with new value
#             el.dispatchEvent(new Event('input'));
#             el.dispatchEvent(new Event('change'));  // Trigger change event to ensure UI reacts
#         }}
#     """
#     driver.execute_script(script)

def clearing(driver,element_identifier,element_type):
    selector_map=selector_mapping(element_type)
    element=driver.find_elements(selector_map,element_identifier)
    for x in element:
        x.clear()            
    
    
def adj_click(driver,data,element_identifier,element_type):
    selector_map=selector_mapping(element_type)
    element=driver.find_elements(selector_map,element_identifier)
    for x in element:
        x.click()

def radio_btn_click(driver,btn_value,element_identifier,element_type):#This function is for clicking radio button
    selector_map=selector_mapping(element_type)
    element=driver.find_elements(selector_map,element_identifier)
    for x in element:
        if x.get_attribute("value")==btn_value:
            x.click()

def data_filling_text(driver,data,elementlocator,selector):
    selector_map=selector_mapping(selector)
    element=find_elem(driver,selector_map,elementlocator)
    element.clear() 
    element.send_keys(data)

    
def data_filling_text_QC(driver,data,elementlocator,selector):
    selector_map=selector_mapping(selector)
    element=find_elem(driver,selector_map,elementlocator)
    element.clear() 
    element.send_keys(data)         

# def select_field(driver,data,elementlocator,selector):
#     try:
#         Select(find_elem(driver,selector,elementlocator)).select_by_visible_text(data)
#     except Exception as e:   
#             data='' 
#             print("no data",e)

def select_field(driver, data, elementlocator, selector):
    try:
        data = data.strip().lower()
        dropdown = Select(find_elem(driver, selector, elementlocator))
        
        # Loop through options and match by lowercase text
        for option in dropdown.options:
            if option.text.strip().lower() == data:
                dropdown.select_by_visible_text(option.text)
                return
        print(f"[select_field] No matching option found for: '{data}'")
    except Exception as e:
        data='' 
        print(f"[select_field] Error selecting option: {e}")


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

    # for value in values_list:
    #     try:
    #         sanitized = sanitize(value)
    #         checkbox_id = f"{id_prefix}_{sanitized}"
    #         checkbox = driver.find_element(By.ID, checkbox_id)
    #         if not checkbox.is_selected():
    #             checkbox.click()
    #             logging.info(f" Checked: {checkbox_id}")
    #         else:
    #             logging.info(f" Already checked: {checkbox_id}")
    #     except NoSuchElementException:
    #         logging.warning(f" Checkbox not found: {checkbox_id}")
    #     except Exception as e:
    #         logging.error(f"Error clicking checkbox {checkbox_id}: {e}")

    for value in values_list:
        try:
            sanitized = sanitize(value)
            checkbox_id = f"{id_prefix}_{sanitized}"
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, checkbox_id))
            )
            if not checkbox.is_selected():
                checkbox.click()
                logging.info(f"Checked: {checkbox_id}")
            else:
                logging.info(f"Already checked: {checkbox_id}")
        except TimeoutException:
            logging.warning(f"Checkbox not found (timeout): {checkbox_id}")
        except Exception as e:
            logging.error(f"Error clicking checkbox {checkbox_id}: {e}")

def fill_repair_details(driver, repair_list):
    for idx, repair in enumerate(repair_list):
        try:
            comment_xpath = f"//input[@id='ExteriorRepairList_{idx}__RepairComment']"
            cost_xpath = f"//input[@id='ExteriorRepairList_{idx}__Amount']"

            # Fill comments
            comment_elem = driver.find_element(By.XPATH, comment_xpath)
            comment_elem.clear()
            comment_elem.send_keys(repair.get("comments", ""))

            # Fill estimated cost
            cost_elem = driver.find_element(By.XPATH, cost_xpath)
            cost_elem.clear()
            cost_elem.send_keys(str(repair.get("estimated_cost", "")))

        except Exception as e:
            logging.error(f"Error filling repair at index {idx} ({repair.get('repair_type')}): {e}")

def save_form(driver):
    
    try:
        time.sleep(5)
        element=driver.find_element(By.XPATH,"//*[@id='msg']")
        time.sleep(5)
        value1 = element.text  
        logging.info("Extracted Value in the ok button click:{}".format((value1)))
        time.sleep(3)
        if value1:
            driver.find_element(By.XPATH,"//*[@id='msg']/button").click()
            time.sleep(15)
            driver.find_element(By.XPATH,"//*[@id='btnSave']").click()
        else:
            driver.find_element(By.XPATH,"//*[@id='btnSave']").click()
            logging.info("There is no OK button to click")
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
        logging.info("Extracted Value in the ok button click:{}".format((value1)))
        time.sleep(3)
        if value1:
            driver.find_element(By.XPATH,"//*[@id='msg']/button").click()
        else:
            logging.info("There is no OK button to click")
    except Exception as e:
        logging.info(e)
     
        
        
    logging.info("order saved :{}".format(order_id))        
        
   # logging.info("order saved :{}".format(order_id))
def update_order_status(assigned_order_id, status, stage, order_event_status):
   
    status_update_url = env.STATUS_UPDATE_URL

    params = {
        "assigned_order_id": assigned_order_id,
        "status": status,
        "stage": stage,
        "order_event_status": order_event_status
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(status_update_url, params=params, headers=headers)
        print(f"{order_event_status} status PUT response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Error while updating status via PUT: {e}")
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
        print(f"PUT status response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Error while updating client account status: {e}")
        return None


def fetch_upload_data(self, order_id: int):
    COMP_UPLOAD_URL = f'{env.PIC_PDF_UPLOAD_URL}{order_id}'

    try:
        response = requests.get(COMP_UPLOAD_URL)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        print(f" Failed to fetch data from API: {e}")
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
        print(f"Error fetching files from server: {e}")
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
                            session=None, merged_json=None):


    try:
        with open(resource_path(config_path), 'r') as f:
            form_config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load form config JSON: {e}")
        update_order_status(order_id, "In Progress", "Entry", "Failed")
        return None, None

    if session is None:
        session = requests.Session()

    if not merged_json:
        url = f"{researchpad_data_retrival_url}?order_id={order_id}"
        logging.info(f"Fetching merged_json from API: {url}")
        try:
            response = session.get(url)
            if response.status_code == 200:
                merged_json = response.json()
            else:
                logging.error(f"Failed to fetch merged_json, status code: {response.status_code}")
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return None, None
        except Exception as e:
            logging.error(f"Exception during API call: {e}")
            update_order_status(order_id, "In Progress", "Entry", "Failed")
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
        print("✅ Validation popup closed.")
        return True
    except (TimeoutException, NoSuchElementException):
        # Popup not present
        print("ℹ️ No validation popup detected.")
        return False