
import os
import re
import time
import logging
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

from condtions.redbell import generate_condition_data
from form_filler.redbell_form_filler import RedBellFormFiller
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clean_address, clearing, data_filling_text, data_filling_text_QC, extract_data_sections, fetch_upload_data, fill_repair_details, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_datefilling, params_check, radio_btn_click, save_form, select_checkboxes_from_list, select_field, setup_driver, update_order_status
from config import env

# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   
arg1, arg2 = params_check()
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

                    #arg1, arg2 = params_check()
                    arg1 = "SmartEntry"  # Manually set for testing
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

        orders_from_api = HybridBPOApi.get_entry_order(arg2) 
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
        form_types = ["Interior Enhanced BPO",'Interior BPO - W Rentals','Exterior Enhanced BPO','Interior BPO','Exterior BPO','Exterior BPO - W Rentals','5 Day MIT ARBPO','5 Day Interior Appraiser Reconciled BPO','5 Day Exterior Appraiser Reconciled BPO','5 Day Exterior BPO - W Rentals','5 Day Exterior BPO','5 Day Interior BPO','5 Day Interior BPO - W Rentals',"3 Day Exterior BPO - W Rentals"]
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
                    update_order_status(4, "In Progress", "Entry", "Failed")
                    return False, None, "form_not_matched"
                    

            else:
                print(f"Address Not Found {order.get('PropAddress')}")
                logging.info(f"Address Not Found {order.get('PropAddress')}")
                address_list.append(order_address)
        update_order_status(4, "In Progress", "Entry", "Failed")
        return False, None, "address_not_found"
        


    def redbell_launch_browser_and_open_form(self, order_url, session):
        # Navigate to order page
        self.driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        self.driver.get(order_url)

        time.sleep(10)
    from form_filler.redbell_form_filler import RedBellFormFiller



def get_nested(data, path_list, default=""):
    """Safely get nested dictionary data with a list of keys."""
    for key in path_list:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data






# def fill_form_multi(self, merged_json, order_id, form_config, session, page_urls):
#     field_actions = {
#         "Textbox": data_filling_text,
#         "Textbox_default": data_filling_text,
#         "Textbox_QC": data_filling_text_QC,
#         "Textbox_default_QC": data_filling_text_QC,
#         "select_data": select_field,
#         "select_default": select_field,
#         "radiobutton_data": radio_btn_click,
#         "radiobutton_default": radio_btn_click,
#         "date_fill_javascript": javascript_excecuter_datefilling,
#         "clearing": clearing,
#         "checkbox":select_checkboxes_from_list
#     }

#     try:
#         sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3 = extract_data_sections(merged_json)
#         if sub_data is None:
#             logging.error("'entry_data' missing or empty in merged_json")
#             return

#         # Add generated condition_data for possible use in the form filling logic
#         condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3)

#         for page in form_config.get("page", []):
#             for section_name, controls in page.items():
#                 page_url = page_urls.get(section_name)
#                 if not page_url:
#                     logging.warning(f"URL not found for section: {section_name}")
#                     continue

#                 logging.info(f"Navigating to section: {section_name} => {page_url}")
#                 self.driver.get(page_url)
#                 time.sleep(3)

#                 for control in controls:
#                     field_type = control.get("filedtype")
#                     values = control.get("values", [])

#                     if field_type == "save_data":
#                         save_form(self.driver)
#                         logging.info(" Form saved.")
#                         for cookie in self.driver.get_cookies():
#                             session.cookies.set(cookie['name'], cookie['value'])
#                         time.sleep(10)
#                         continue

#                     for field in values:
#                         if not (isinstance(field, list) and len(field) == 3):
#                             logging.warning(f" Invalid field format: {field}")
#                             continue

#                         key_expr, xpath, mode = field
#                         value = ""

#                         try:
#                             if key_expr.startswith("sub_data"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(sub_data, keys, "")

#                             elif key_expr.startswith("comp_data"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(comp_data, keys, "") if comp_data else ""

#                             elif key_expr.startswith("adj_data"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(adj_data, keys, "") if adj_data else ""

#                             elif key_expr.startswith("rental_data"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(rental_data, keys, "") if rental_data else ""

#                             elif key_expr.startswith("condition_data"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(condition_data, keys, "")

#                             elif key_expr.startswith("entry_data[0]"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr[len("entry_data[0]"):])
#                                 first_entry = merged_json.get("entry_data", [{}])[0]
#                                 value = get_nested(first_entry, keys, "")

#                             elif key_expr.startswith("sold1"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(sold1, keys, "")

#                             elif key_expr.startswith("sold2"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(sold2, keys, "")

#                             elif key_expr.startswith("sold3"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(sold3, keys, "")

#                             elif key_expr.startswith("list1"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(list1, keys, "")

#                             elif key_expr.startswith("list2"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(list2, keys, "")

#                             elif key_expr.startswith("list3"):
#                                 keys = re.findall(r"\['(.*?)'\]", key_expr)
#                                 value = get_nested(list3, keys, "")

#                             else:
#                                 value = key_expr

                    
#                             if not value:
#                                 logging.info(f"ℹ Skipping empty value for {key_expr}")
#                                 continue

#                             action_func = field_actions.get(field_type)
#                             if action_func:
#                                 logging.debug(f" Executing [{field_type}] at {xpath} with value: {value}")
#                                 action_func(self.driver, value, xpath, mode)
#                                 logging.info(f" Filled [{field_type}] {key_expr} = {value}")
#                             else:
#                                 logging.warning(f" Unknown field type: {field_type}")

#                         except Exception as e:
#                             logging.error(f" Exception filling field {key_expr}: {e}")
#     except Exception as e:
#         logging.error(f" Critical error in fill_form_multi: {e}")

def fill_form_multi(self, merged_json, order_id, form_config, session, page_urls):
    field_actions = {
        "Textbox": data_filling_text,
        "Textbox_default": data_filling_text,
        "Textbox_QC": data_filling_text_QC,
        "Textbox_default_QC": data_filling_text_QC,
        "select_data": select_field,
        "select_default": select_field,
        "radiobutton_data": radio_btn_click,
        "radiobutton_default": radio_btn_click,
        "date_fill_javascript": javascript_excecuter_datefilling,
        "clearing": clearing,
        "checkbox": select_checkboxes_from_list,

    }

    try:
        sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3 = extract_data_sections(merged_json)
        if sub_data is None:
            logging.error("'entry_data' missing or empty in merged_json")
            return

        condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3)

        for page in form_config.get("page", []):
            for section_name, controls in page.items():
                page_url = page_urls.get(section_name)
                if not page_url:
                    logging.warning(f"URL not found for section: {section_name}")
                    continue

                logging.info(f"Navigating to section: {section_name} => {page_url}")
                self.driver.get(page_url)
                time.sleep(3)

                for control in controls:
                    field_type = control.get("filedtype")
                    values = control.get("values", [])

                    if field_type == "save_data":
                        save_form(self.driver)
                        logging.info("Form saved.")
                        for cookie in self.driver.get_cookies():
                            session.cookies.set(cookie['name'], cookie['value'])
                        time.sleep(10)
                        continue

                    if field_type == "checkbox_list":
                        # Checkbox list uses a value list of format: [key, id_prefix, mode]
                        for field in values:
                            if not (isinstance(field, list) and len(field) == 3):
                                logging.warning(f"Invalid checkbox_list field: {field}")
                                continue
                            key_expr, id_prefix, mode = field
                            try:
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sub_data, keys, [])
                                if value:
                                    select_checkboxes_from_list(self.driver, value, id_prefix)
                                    logging.info(f" Checkboxes selected for {key_expr} with prefix {id_prefix}")
                                else:
                                    logging.info(f"ℹ Skipping empty checkbox list for {key_expr}")
                            except Exception as e:
                                logging.error(f" Error selecting checkboxes for {key_expr}: {e}")
                        continue  # skip normal field handling for checkbox_list
                    if field_type == "repair_details_fill":
                        for field in values:
                            key_expr, _, _ = field
                            try:
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                repair_list = get_nested(sub_data, keys, [])
                                if isinstance(repair_list, list):
                                    fill_repair_details(self.driver, repair_list)
                                else:
                                    logging.warning(f"Expected list of repair details for {key_expr}, got {type(repair_list)}")
                            except Exception as e:
                                logging.error(f"Error processing repair_details_fill: {e}")
                        continue
                    for field in values:
                        if not (isinstance(field, list) and len(field) == 3):
                            logging.warning(f"Invalid field format: {field}")
                            continue

                        key_expr, xpath, mode = field
                        value = ""

                        try:
                            # ----------- VALUE EXTRACTION -----------
                            if key_expr.startswith("sub_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sub_data, keys, "")
                            elif key_expr.startswith("comp_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(comp_data, keys, "")
                            elif key_expr.startswith("adj_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(adj_data, keys, "")
                            elif key_expr.startswith("rental_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(rental_data, keys, "")
                            elif key_expr.startswith("condition_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(condition_data, keys, "")
                            elif key_expr.startswith("entry_data[0]"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr[len("entry_data[0]"):])
                                value = get_nested(merged_json.get("entry_data", [{}])[0], keys, "")
                            elif key_expr.startswith("sold1"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sold1, keys, "")
                            elif key_expr.startswith("sold2"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sold2, keys, "")
                            elif key_expr.startswith("sold3"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sold3, keys, "")
                            elif key_expr.startswith("list1"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(list1, keys, "")
                            elif key_expr.startswith("list2"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(list2, keys, "")
                            elif key_expr.startswith("list3"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(list3, keys, "")
                            else:
                                value = key_expr  # literal fallback

                            # ----------- FILL FIELD -----------
                            if not value:
                                logging.info(f"ℹ Skipping empty value for {key_expr}")
                                continue

                            action_func = field_actions.get(field_type)
                            if action_func:
                                logging.debug(f"Executing [{field_type}] at {xpath} with value: {value}")
                                action_func(self.driver, value, xpath, mode)
                                logging.info(f"Filled [{field_type}] {key_expr} = {value}")
                            else:
                                logging.warning(f"Unknown field type: {field_type}")

                        except Exception as e:
                            logging.error(f"Exception filling field {key_expr}: {e}")
    except Exception as e:
        logging.error(f"Critical error in fill_form_multi: {e}")


def upload_files_for_order(self, order_id: int, upload_page_url: str):
    data = fetch_upload_data(self,order_id)
    if not data:
        return

    documents = data["documents"]
    comparables_folder = data["comparables_folder"]

    file_paths = {}

    # Subject PDFs
    for doc in documents:
        doc_type = doc.get("type")
        doc_path = doc.get("path")
        if doc_type == "MLS":
            file_paths["MLSPdfIdSubject"] = doc_path
        elif doc_type == "Tax":
            file_paths["TaxPdfIdSubject"] = doc_path

    # Comp PDFs (s1–s3, a1–a3)
    if os.path.exists(comparables_folder):
        for fname in os.listdir(comparables_folder):
            full_path = os.path.join(comparables_folder, fname)
            fname_lower = fname.lower()

            if not fname_lower.endswith(".pdf"):
                continue

            if match := re.match(r"s([1-3])\.pdf", fname_lower):
                file_paths[f"MLSPdfIdSoldComp{match.group(1)}"] = full_path
            elif match := re.match(r"a([1-3])\.pdf", fname_lower):
                file_paths[f"MLSPdfIdListedComp{match.group(1)}"] = full_path
    else:
        print(" Comparables folder not found!")

    #  Navigate to upload page
    self.driver.get(upload_page_url)
    time.sleep(3)

    # Upload PDFs
    for input_id, file_path in file_paths.items():
        if not os.path.exists(file_path):
            print(f" File not found: {file_path}")
            continue
        try:
            file_input = self.driver.find_element(By.ID, input_id)
            file_input.send_keys(file_path)
            print(f"Uploaded {file_path} to {input_id}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed to upload {file_path} to {input_id}: {e}")


def count_non_subject_photos(self):
    photo_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'photo-thumbnail')]//img")
    count = 0
    for img in photo_elements:
        alt = (img.get_attribute("alt") or "").lower()
        aria = (img.get_attribute("aria-label") or "").lower()
        if "subject" in alt or "subject" in aria:
            continue
        count += 1
    return count

def upload_photos_to_order(self, comparables_folder, photos_url):
    self.driver.get(photos_url)
    time.sleep(3)  # wait for page to load

    if not os.path.exists(comparables_folder):
        print("Comparables folder not found!")
        return {}

    photos_before = count_non_subject_photos(self)
    print(f"📸 Non-subject photos before upload: {photos_before}")

    # Label mapping from filename pattern
    label_to_file_map = {}
    for fname in os.listdir(comparables_folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        match = re.match(r'([asl])([1-3])\.(jpg|jpeg|png)', fname.lower())
        if match:
            prefix, idx, _ = match.groups()
            label = {
                'a': f"Listing Comp {idx}",
                's': f"Sold Comp {idx}",
                'r': f"Leased Comp {idx}",
                'l':f"Active Comp {idx}"
            }.get(prefix)
            if label:
                label_to_file_map[label.lower()] = os.path.join(comparables_folder, fname)

    print(f" Photos to upload: {len(label_to_file_map)}")

    upload_results = {}
    labels_sorted = sorted(label_to_file_map.keys())

    for label in labels_sorted:
        file_path = label_to_file_map[label]
        try:
            current_select_count = len(self.driver.find_elements(By.NAME, "fileType"))

            file_input_xpath = "(//input[@type='file' and @name='qqfile'])[1]"
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, file_input_xpath))
            )
            file_input.send_keys(file_path)
            print(f" Uploaded {file_path} for label {label}")
            upload_results[label] = {"success": None, "file": file_path}

            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.NAME, "fileType")) > current_select_count
            )
            all_selects = self.driver.find_elements(By.NAME, "fileType")
            select_element = all_selects[-1]

            if select_element.get_attribute("disabled"):
                self.driver.execute_script("arguments[0].removeAttribute('disabled');", select_element)

            photo_names_select = Select(select_element)
            options_text = [opt.text.strip() for opt in photo_names_select.options]

            base_name = label.title()
            corresponding_name_with_asterisk = f"* {base_name}"

            if corresponding_name_with_asterisk in options_text:
                photo_names_select.select_by_visible_text(corresponding_name_with_asterisk)
                logging.info(f" Selected verified label: {corresponding_name_with_asterisk}")
            elif base_name in options_text:
                photo_names_select.select_by_visible_text(base_name)
                logging.info(f" Selected base label: {base_name}")
            else:
                print(f" Label '{label}' not found in dropdown.")
                upload_results[label]["success"] = False
                continue

            time.sleep(1)

        except Exception as e:
            print(f" Error handling '{label}': {e}")
            upload_results[label] = {"success": False, "file": file_path}

    # Trigger upload
    try:
        upload_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'trigger-upload'))
        )
        upload_button.click()
        print(" Triggered upload for all photos.")
    except Exception as e:
        print(f" Error clicking upload button: {e}")
        for label in upload_results:
            if upload_results[label]["success"] is None:
                upload_results[label]["success"] = False

    # Wait for upload confirmation
    try:
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src,'blob:') or contains(@src,'http')]"))
        )
        for label in upload_results:
            if upload_results[label]["success"] is None:
                upload_results[label]["success"] = True
        print(" Upload confirmation detected.")
    except Exception as e:
        print(f" Upload wait timeout: {e}")
        for label in upload_results:
            if upload_results[label]["success"] is None:
                upload_results[label]["success"] = False

    photos_after = count_non_subject_photos(self)
    print(f"📸 Non-subject photos after upload: {photos_after}")

    expected_new_photos = sum(1 for r in upload_results.values() if r["success"])
    actual_new_photos = photos_after - photos_before
    upload_valid = actual_new_photos == expected_new_photos

    print(f" Expected: {expected_new_photos}, Actual: {actual_new_photos}")
    print(f" Upload Valid: {'PASS' if upload_valid else 'FAIL'}")

    # Extract required non-subject photo labels from UI
    try:
        required_labels = set()
        required_tables = self.driver.find_elements(By.ID, "requiredphototable")
        for table in required_tables:
            td_elements = table.find_elements(By.TAG_NAME, "td")
            for td in td_elements:
                label_text = td.text.strip()
                if not label_text.lower().startswith("subject"):
                    required_labels.add(label_text.lower())

        uploaded_labels = {
            label.lower()
            for label, result in upload_results.items()
            if result["success"]
        }

        missing_labels = required_labels - uploaded_labels
        extra_labels = uploaded_labels - required_labels

        print(f" Required labels from UI: {sorted(required_labels)}")
        print(f" Uploaded labels: {sorted(uploaded_labels)}")

        if missing_labels:
            print(f" Missing uploads for labels: {sorted(missing_labels)}")
        else:
            print(" All required non-subject photos were uploaded successfully.")

    except Exception as e:
        print(f" Error validating required photo labels: {e}")

    return {
        "photos_before": photos_before,
        "photos_after": photos_after,
        "photos_uploaded_count": actual_new_photos,
        "upload_results": upload_results,
        "upload_valid": upload_valid,
    }

def load_form_config_and_data(order_id, config_path, researchpad_data_retrival_url,
                              session=None, merged_json=None):


    try:
        with open(config_path, 'r') as f:
            form_config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load form config JSON: {e}")
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
                return None, None
        except Exception as e:
            logging.error(f"Exception during API call: {e}")
            return None, None

    return form_config, merged_json



def build_url(base_url, item_id, order_id, page):
    return f"{base_url}?ItemId={item_id}&OrderId={order_id}&ActivePage={page}"

# def redbell_formopen_fill(self, order, session=None, merged_json=None, order_details=None, order_id=None):
#     ProductDesc = order.get('ProductDesc', '').strip()
#     item_id = order.get('ItemId')
#     order_id_url = order.get('OrderId')

#     base_url = env.BASE_URL_ENTRY
#     page_urls = {
#         "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "SubjectHistoryAdj"),
#         "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "NeighborhoodInfoAdj"),
#         "ComparablesAdj": build_url(base_url, item_id, order_id_url, "ComparablesAdj"),
#         "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
#         "Repairs": build_url(base_url, item_id, order_id_url, "Repairs"),
#         "Rental Comparables": build_url(base_url, item_id, order_id_url, "Rental%20Comparables"),
#         "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
#         "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
#     }

    
#     researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
#     if ProductDesc=="Exterior BPO" or ProductDesc=="5 Day Exterior BPO"  or  ProductDesc=="5 Day Interior BPO" or ProductDesc=="5 Day Exterior Appraiser Reconciled BPO" or ProductDesc=="3 Day Exterior BPO"  or  ProductDesc=="3 Day Interior BPO":
#         config_path = 'json/redbelljson/Redbell_Exterior.json'
#     elif 'Rental' in ProductDesc:
#         config_path = 'json/redbelljson/Redbell_Rental.json'

#     else:
#         logging.warning(f"No matching config path for ProductDesc: {ProductDesc}")
#         return
#     form_config, merged_json = load_form_config_and_data(
#         order_id=order_id,
#         config_path=config_path,
#         researchpad_data_retrival_url=researchpad_data_retrival_url,
#         session=session,
#         merged_json=merged_json
#     )
#     # Optional: Check if loading was successful
#     if not form_config or not merged_json:
#         return
#     # Extract and generate condition_data, attach it inside merged_json for usage if needed
#     sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3 = extract_data_sections(merged_json)
#     condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3)
#     if "entry_data" in merged_json and merged_json["entry_data"]:
#         merged_json["entry_data"][0]["condition_data"] = condition_data

#     print(merged_json)    
#     # Fill all pages except ComparablesAdj first
#     try:
#         for page_key, url in page_urls.items():
#             if page_key == "ComparablesAdj":
#                 continue
#             logging.info(f"Loading page: {page_key} -> {url}")
#             self.driver.get(url)
#             self.driver.implicitly_wait(10)
#             fill_form_multi(self, merged_json, order_id_url, form_config, session, {page_key: url})
#             time.sleep(2)
#     except Exception as e:
#         logging.exception(f"Error while navigating and filling forms (non-ComparablesAdj): {e}")
#         return

#     # Fill ComparablesAdj page separately
#     try:
#         comparables_url = page_urls["ComparablesAdj"]
#         logging.info(f"Loading ComparablesAdj page: {comparables_url}")
#         self.driver.get(comparables_url)
#         self.driver.implicitly_wait(10)
#         fill_form_multi(self, merged_json, order_id_url, form_config, session, {"ComparablesAdj": comparables_url})
#         time.sleep(2)
#     except Exception as e:
#         logging.exception(f"Error filling ComparablesAdj page: {e}")
#         return

#     # Upload files for ComparablesAdj page
#     try:
#         upload_files_for_order(self, order_id, comparables_url)
#         data = fetch_upload_data(self, order_id)
#         if not data:
#             logging.warning(f"No upload data found for order {order_id}")
#             return

#         comparables_folder = data.get("comparables_folder")
#         if isinstance(comparables_folder, str) and comparables_folder.strip():
#             photos_url = page_urls["Photos"]
#             upload_photos_to_order(self, comparables_folder.strip(), photos_url)
#         else:
#             logging.warning(f"Comparables folder is missing or invalid for order {order_id_url}: {comparables_folder!r}")

#     except Exception as e:
#         logging.exception(f"Error during photo upload steps: {e}")
#         return



def redbell_formopen_fill(self, order, session=None, merged_json=None, order_details=None, order_id=None):
    ProductDesc = order.get('ProductDesc', '').strip()
    item_id = order.get('ItemId')
    order_id_url = order.get('OrderId')

    base_url = env.BASE_URL_ENTRY
    
    researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
    if ProductDesc=="Exterior BPO" or ProductDesc=="5 Day Exterior BPO"  or  ProductDesc=="5 Day Interior BPO" or ProductDesc=="5 Day Exterior Appraiser Reconciled BPO" or ProductDesc=="3 Day Exterior BPO"  or  ProductDesc=="3 Day Interior BPO":
         # Exterior URLs
        page_urls = {
            "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "Subject%20History"),
            "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "Neighborhood%20Info"),
            "ComparablesAdj": build_url(base_url, item_id, order_id_url, "Comparables"),
            "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
            "Repairs": build_url(base_url, item_id, order_id_url, "Repairs"),
            "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
            "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
        }

        config_path = 'json/redbelljson/Redbell_Exterior.json'

    elif "Rental" in ProductDesc:
        # Rental URLs
        page_urls = {
            "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "SubjectHistoryAdj"),
            "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "NeighborhoodInfoAdj"),
            "ComparablesAdj": build_url(base_url, item_id, order_id_url, "ComparablesAdj"),
            "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
            "Repairs": build_url(base_url, item_id, order_id_url, "Repairs"),
            "Rental Comparables": build_url(base_url, item_id, order_id_url, "Rental%20Comparables"),
            "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
            "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
        }

        config_path = 'json/redbelljson/Redbell_Rental.json'

    else:
        logging.warning(f"No matching config path for ProductDesc: {ProductDesc}")
        return
    form_config, merged_json = load_form_config_and_data(
        order_id=order_id,
        config_path=config_path,
        researchpad_data_retrival_url=researchpad_data_retrival_url,
        session=session,
        merged_json=merged_json
    )
    # Optional: Check if loading was successful
    if not form_config or not merged_json:
        return
    # Extract and generate condition_data, attach it inside merged_json for usage if needed
    sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3 = extract_data_sections(merged_json)
    condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3)
    if "entry_data" in merged_json and merged_json["entry_data"]:
        merged_json["entry_data"][0]["condition_data"] = condition_data

    print(merged_json)    
    # Fill all pages except ComparablesAdj first
    try:
        for page_key, url in page_urls.items():
            # if page_key == "ComparablesAdj":
            #     continue
            logging.info(f"Loading page: {page_key} -> {url}")
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            fill_form_multi(self, merged_json, order_id_url, form_config, session, {page_key: url})
            time.sleep(2)
    except Exception as e:
        logging.exception(f"Error while navigating and filling forms (non-ComparablesAdj): {e}")
        return

    # # Fill ComparablesAdj page separately
    # try:
    #     comparables_url = page_urls["ComparablesAdj"]
    #     logging.info(f"Loading ComparablesAdj page: {comparables_url}")
    #     self.driver.get(comparables_url)
    #     self.driver.implicitly_wait(10)
    #     fill_form_multi(self, merged_json, order_id_url, form_config, session, {"ComparablesAdj": comparables_url})
    #     time.sleep(2)
    # except Exception as e:
    #     logging.exception(f"Error filling ComparablesAdj page: {e}")
    #     return

    # Upload files for ComparablesAdj page
    try:
        comparables_url = page_urls["ComparablesAdj"]
        upload_files_for_order(self, order_id, comparables_url)
        data = fetch_upload_data(self, order_id)
        if not data:
            logging.warning(f"No upload data found for order {order_id}")
            return

        comparables_folder = data.get("comparables_folder")
        if isinstance(comparables_folder, str) and comparables_folder.strip():
            photos_url = page_urls["Photos"]
            upload_photos_to_order(self, comparables_folder.strip(), photos_url)
        else:
            logging.warning(f"Comparables folder is missing or invalid for order {order_id_url}: {comparables_folder!r}")

    except Exception as e:
        logging.exception(f"Error during photo upload steps: {e}")
        return


