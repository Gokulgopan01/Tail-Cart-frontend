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
from tkinter import messagebox
import sys
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from config import env


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = env.ASSIGNEDORDERS_URL   

def initialize_driver(self):
        """Initialize Selenium WebDriver."""
        try:
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized") 
                chrome_options.add_argument("--disable-notifications")

                service = Service("chromedriver.exe") 
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                return self.driver
        except Exception as e:
                logging.error(f"Error initializing WebDriver: {e}")
                return None



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
            print(f"Args : {arg1}")   
            return arg1,arg2
    else:
          return None,None        
# Function to fetch stored token (assuming it was saved as JSON)
def get_saved_token():
    try:
        with open("login_data.json", "r") as file:
            data = json.load(file)
            return data.get("token", None)
    except FileNotFoundError:
        return None

# Fetch order address using stored token
def get_order_address_from_assigned_order(order_id):
    token = get_saved_token()
    if not token:

        return "Authentication token not found. Please log in again."
        
    #else:
         
    url = f"{ASSIGNEDORDERS_URL}{order_id}"
    headers = {"Authorization": f"Bearer {token}"}  # Include token in headers

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "content" in data and "data" in data["content"]:
                return data["content"]["data"].get("sub_address", "Address Not Found")
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

def javascript_excecuter_datefilling(driver,data,elementlocator,selector):    
   
        if data=='':
            pass

        else:
            # date=datetime.strptime(data,"%Y-%m-%d")
            # date=date.strftime("%d/%m/%Y")
            script = f"""document.evaluate("{elementlocator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value = '{data}'"""
            driver.execute_script(script)

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
    element.send_keys(data)
    
def data_filling_text_QC(driver,data,elementlocator,selector):
    selector_map=selector_mapping(selector)
    element=find_elem(driver,selector_map,elementlocator)
    element.clear() 
    element.send_keys(data)         

def select_field(driver,data,elementlocator,selector):
    try:
        Select(find_elem(driver,selector,elementlocator)).select_by_visible_text(data)
    except Exception as e:   
            data='' 
            print("no data",e)
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

    def sanitize(value):
        # Remove special characters and whitespace
        return re.sub(r'[^a-zA-Z0-9]', '', str(value))

    for value in values_list:
        try:
            sanitized = sanitize(value)
            checkbox_id = f"{id_prefix}_{sanitized}"
            checkbox = driver.find_element(By.ID, checkbox_id)
            if not checkbox.is_selected():
                checkbox.click()
                logging.info(f" Checked: {checkbox_id}")
            else:
                logging.info(f" Already checked: {checkbox_id}")
        except NoSuchElementException:
            logging.warning(f" Checkbox not found: {checkbox_id}")
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
        
        
   # logging.info("order saved :{}".format(order_id))
def update_order_status(assigned_order_id, status, stage, order_event_status):
   
    status_update_url=env.STATUS_UPDATE_URL
    
    params = {
        "assigned_order_id": assigned_order_id,
        "status": status,
        "stage": stage,
        "order_event_status": order_event_status
    }
    
    try:
        response = requests.get(status_update_url, params=params)
        print(f"{order_event_status} status response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Error while updating status: {e}")
        return None

def update_client_account_status(client_account_id, action_required_reason):
    
    url = f'{env.ACCOUNT_INACTIVE}{client_account_id}'
    
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
    item_id = content.get("itemId")  # Make sure your API returns this

    return {
        "documents": documents,
        "comparables_folder": comparables_folder,
        "item_id": item_id
    }
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

    return sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3