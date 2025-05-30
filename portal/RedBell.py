
import os
import re
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
from utils.helper import clean_address, clearing, data_filling_text, data_filling_text_QC, fetch_upload_data, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_datefilling, params_check, radio_btn_click, save_form, select_field, setup_driver
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



def get_nested(data, path_list, default=""):
    """Safely get nested dictionary data with a list of keys."""
    for key in path_list:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data






def fill_form_multi(self, driver, merged_json, order_id, form_config, session, subject_url):
    import json
    import re
    import time
    import logging

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
        "clearing": clearing
    }

    try:
        # Validate and extract merged_json structure
        entry_data = merged_json.get('entry_data')
        if not isinstance(entry_data, list) or len(entry_data) == 0:
            logging.error("merged_json['entry_data'] is missing or not a list.")
            return

        entry = entry_data[0]
        if not isinstance(entry, dict):
            logging.error("entry_data[0] is not a dictionary.")
            return

        sub_data = entry.get('sub_data')
        comp_data = entry.get('comp_data', {}).get('List 1')

        if not isinstance(sub_data, dict):
            logging.warning("sub_data is missing or not a dictionary. Defaulting to empty.")
            sub_data = {}

        if not isinstance(comp_data, dict):
            logging.warning("comp_data['List 1'] is missing or not a dictionary. Defaulting to empty.")
            comp_data = {}

        # Proceed with form filling
        for page in form_config.get("page", []):
            for section_key, controls in page.items():
                for control in controls:
                    field_type = control.get("filedtype")

                    # Save data action
                    if field_type == "save_data":
                        for cookie in driver.get_cookies():
                            c = {cookie['name']: cookie['value']}
                            session.cookies.update(c)
                        save_form(driver)
                        time.sleep(10)

                    for field in control.get("values", []):
                        if isinstance(field, dict):
                            continue

                        if len(field) != 3:
                            logging.warning(f"Invalid field format: {field}")
                            continue

                        key_expr, xpath, mode = field

                        try:
                            if key_expr.startswith("sub_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(sub_data, keys, "")
                            elif key_expr.startswith("comp_data"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr)
                                value = get_nested(comp_data, keys, "")
                            elif key_expr.startswith("entry_data[0]"):
                                keys = re.findall(r"\['(.*?)'\]", key_expr[len("entry_data[0]"):])
                                value = get_nested(entry, keys, "")
                            else:
                                value = key_expr  # Possibly a literal default

                            if value in [None, ""]:
                                logging.info(f"Skipping empty value for {field_type} - Expression: {key_expr}")
                                continue

                            action_func = field_actions.get(field_type)
                            if action_func:
                                action_func(driver, value, xpath, mode)
                                logging.info(f"{field_type}: {key_expr} = {value} at {xpath}")
                            else:
                                logging.warning(f"Unknown field type: {field_type}")

                        except Exception as e:
                            logging.error(f"Error processing field {key_expr}: {e}")
    except Exception as e:
        logging.error(f"Fatal error in fill_form_multi: {e}")


# def upload_files_for_order(self, order_id: int, upload_page_url: str):
#         COMP_UPLOAD_URL = f'{env.PIC_PDF_UPLOAD_URL}{order_id}'

#         try:
#             response = requests.get(COMP_UPLOAD_URL)
#             response.raise_for_status()
#             json_data = response.json()
#         except Exception as e:
#             print(f" Failed to fetch data from API: {e}")
#             return

#         documents = json_data.get("content", {}).get("data", {}).get("documents", [])
#         comparables_folder = json_data.get("content", {}).get("data", {}).get("comparables", "")

#         file_paths = {}

#         #  Extract subject documents
#         for doc in documents:
#             doc_type = doc.get("type")
#             doc_path = doc.get("path")
#             if doc_type == "MLS":
#                 file_paths["MLSPdfIdSubject"] = doc_path
#             elif doc_type == "Tax":
#                 file_paths["TaxPdfIdSubject"] = doc_path

#         #  Extract S1–S3 (sold) and L1–L3 (listed) PDF files
#         if os.path.exists(comparables_folder):
#             for fname in os.listdir(comparables_folder):
#                 fname_lower = fname.lower()
#                 full_path = os.path.join(comparables_folder, fname)

#                 if not fname_lower.endswith(".pdf"):
#                     continue

#                 sold_match = re.match(r"s(\d)\.pdf", fname_lower)
#                 listed_match = re.match(r"a(\d)\.pdf", fname_lower)

#                 if sold_match:
#                     idx = int(sold_match.group(1))
#                     if 1 <= idx <= 3:
#                         file_paths[f"MLSPdfIdSoldComp{idx}"] = full_path
#                         continue

#                 if listed_match:
#                     idx = int(listed_match.group(1))
#                     if 1 <= idx <= 3:
#                         file_paths[f"MLSPdfIdListedComp{idx}"] = full_path
#         else:
#             print(" Comparables folder not found!")

#         #  Navigate to the upload page
#         self.driver.get(upload_page_url)
#         time.sleep(3)

#         #  Upload documents
#         for input_id, file_path in file_paths.items():
#             if not os.path.exists(file_path):
#                 print(f" File not found: {file_path}")
#                 continue
#             try:
#                 file_input = self.driver.find_element(By.ID, input_id)
#                 file_input.send_keys(file_path)
#                 print(f" Uploaded {file_path} to {input_id}")
#                 time.sleep(0.5)
#             except Exception as e:
#                 print(f" Failed to upload {file_path} to {input_id}: {e}")

def upload_files_for_order(self, order_id: int, upload_page_url: str):
    data = fetch_upload_data(order_id)
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

def upload_photos_to_order(self, comparables_folder: str,photos_url: str) -> dict:
    
    self.driver.get(photos_url)
    time.sleep(3)  # wait for page load
    
    if not os.path.exists(comparables_folder):
        print("Comparables folder not found!")
        return {}

    def count_non_subject_photos():
        """
        Count photos excluding subject photos.
        Assumes photos have alt or aria-label or nearby text that says 'Subject' for subject photos.
        Adjust selector and conditions as per actual page.
        """
        photo_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'photo-thumbnail')]//img")
        count = 0
        for img in photo_elements:
            alt_text = img.get_attribute("alt") or ""
            aria_label = img.get_attribute("aria-label") or ""
            # Check if this photo is labeled 'Subject', exclude it
            if "subject" in alt_text.lower() or "subject" in aria_label.lower():
                continue
            count += 1
        return count

    photos_before = count_non_subject_photos()
    print(f"Non-subject photos before upload: {photos_before}")

    # Prepare label to file path map
    label_to_file_map = {}
    for fname in os.listdir(comparables_folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        match = re.match(r'([asl])([1-3])\.(jpg|jpeg|png)', fname.lower())
        if match:
            prefix, idx, _ = match.groups()
            label = None
            if prefix == 'a':
                label = f"Active Comp {idx}"
            elif prefix == 's':
                label = f"Sold Comp {idx}"
            elif prefix == 'l':
                label = f"Leased Comp {idx}"
            if label:
                label_to_file_map[label] = os.path.join(comparables_folder, fname)

    print(f"Photos to upload: {len(label_to_file_map)}")

    upload_results = {}
    photo_blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'photo-upload-block')]")

    for block in photo_blocks:
        try:
            label_input = block.find_element(By.XPATH, ".//input[@type='text']")
            label = label_input.get_attribute("value").strip()

            if not label or label.lower().startswith("subject"):
                continue

            file_path = label_to_file_map.get(label)
            if not file_path:
                print(f"No photo file for label '{label}'")
                upload_results[label] = {"success": False, "url": None}
                continue

            file_input = block.find_element(By.XPATH, ".//input[@type='file']")
            upload_button = block.find_element(By.XPATH, ".//button[contains(text(),'Upload Photo')]")

            file_input.send_keys(file_path)
            upload_button.click()

            # Wait for upload and thumbnail appearance
            thumbnail_img = WebDriverWait(block, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//img[contains(@src,'blob:') or contains(@src,'http')]"))
            )
            photo_url = thumbnail_img.get_attribute("src")

            print(f"Uploaded '{label}' => {photo_url}")
            upload_results[label] = {"success": True, "url": photo_url}

            time.sleep(1)
        except Exception as e:
            print(f"Upload error for '{label}': {e}")
            upload_results[label] = {"success": False, "url": None}

    photos_after = count_non_subject_photos()
    print(f"Non-subject photos after upload: {photos_after}")

    expected_new_photos = sum(1 for r in upload_results.values() if r["success"])
    actual_new_photos = photos_after - photos_before
    upload_valid = actual_new_photos == expected_new_photos

    print(f"Expected new photos: {expected_new_photos}")
    print(f"Actual new photos: {actual_new_photos}")
    print(f"Upload validation result: {'PASS' if upload_valid else 'FAIL'}")

    return {
        "photos_before": photos_before,
        "photos_after": photos_after,
        "photos_uploaded_count": actual_new_photos,
        "upload_results": upload_results,
        "upload_valid": upload_valid,
    }


def redbell_formopen_fill(self, order, session, merged_json, order_details, order_id):
    ProductDesc = order.get('ProductDesc', '').strip()
    photos_url = f"https://valuationops.homegenius.com/VendorBpoForm?{order['ItemId']}&OrderId={order['OrderId']}&ActivePage=Photos"
    if 'Rental' in ProductDesc:
        subject_url = f"https://valuationops.homegenius.com/VendorBpoForm?ItemId={order['ItemId']}&OrderId={order['OrderId']}&ActivePage=SubjectHistoryAdj"
        self.driver.get(subject_url)
        self.driver.implicitly_wait(10)

        with open('json/redbelljson/Redbell_Enhanced.json') as f:
            form_config = json.load(f)

        # Create a session if None
        if session is None:
            import requests
            session = requests.Session()

        url = f"http://192.168.2.70:8001/api/v1/entry-data/?order_id={order_id}"
        response = requests.get(url)
        if response.status_code == 200:
            merged_json = response.json()
            fill_form_multi(self, self.driver, merged_json, order_id, form_config, session, subject_url)
            RNT_PIC_PDF_UPLOAD_PAGE_URL=f"https://valuationops.homegenius.com/VendorBpoForm?ItemId={order['ItemId']}&OrderId={order['OrderId']}&ActivePage=ComparablesAdj"                    
            upload_page_url=f"{RNT_PIC_PDF_UPLOAD_PAGE_URL}"
            print(upload_page_url)                 
            upload_files_for_order(self,order_id, upload_page_url)
            
        else:
            logging.error(f"Failed to fetch merged_json, status code: {response.status_code}")