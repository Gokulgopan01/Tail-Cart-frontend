import os
import re
import time
import random
import logging
from config import env
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from utils.glogger import GLogger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import (update_portal_login_confirmation_status, get_order_address_from_assigned_order, 
handle_login_status, params_check, setup_driver,update_order_status,load_form_config_and_data, get_nested, radio_btn_click,
data_filling_text,javascript_excecuter_filling,checkbox_tick_field, fetch_upload_data, set_datepicker_date,click_element,update_pic_status)


# Load variables from .env file
load_dotenv()
logger = GLogger()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
process_type, hybrid_orderid,hybrid_token = params_check()                        


class InspectionPort:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.inspection_date = None
        self.order_id = None
        self.portal_key = portal_key
        logging.basicConfig(level=logging.INFO)


    def login_to_portal(self):
        '''Fcuntion to login to portal'''

        try:
            # Setup driver
            setup_driver(self)

            # Navigate to the portal URL
            self.driver.get(self.portal_url)
            print(f"Opened portal URL: {self.portal_url}")
            wait = WebDriverWait(self.driver, 20)

            # Enter Username
            wait.until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(self.username)
            
            # Enter Password
            wait.until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(self.password)

            # Click login button
            wait.until(EC.element_to_be_clickable((By.ID, "logOnBtn"))).click()

            # # Wait for URL to change after login
            wait.until(lambda driver: driver.current_url != self.portal_url)
            current_url = self.driver.current_url
            print(f"URL after login: {current_url}")

            # Check if login was successful
            login_check_keywords = ["Dashboard", "Profile"]
        
            if process_type == "SmartEntry":
                
                login_success = any(k in current_url for k in login_check_keywords)
                if login_success:
                    orders = self.fetch_data()
                    self.inspectionport_formopen( orders=orders, session=None,  merged_json=None,  order_details=self.order_details, order_id=self.order_id )
                else:
                    handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)
                    return self.driver
            else:   
                update_portal_login_confirmation_status(hybrid_orderid)
                handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)
                return self.driver

        except Exception as e:
            self.login_status = f"Login failed: {e}"
            print("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Login exception"], self.portal_name)
            return "Login error", self.driver


    def fetch_data(self):
        '''Fetch orders from portal'''

        try:
            self.driver.execute_script("window.location.hash = '#Orders';")
            self.wait_for_element( By.CSS_SELECTOR, 'div.order-accepted.order-details')
            soup = BeautifulSoup(self.driver.page_source , 'html.parser')
            order_divs = soup.select('div.order-accepted.order-details')
            portal_order_list = []

            for div in order_divs:  
                address_tag = div.select_one('li.address')
                report_btn = div.select_one("div.btn-fake[id^='submitReportLabel_']")
                report_type_tag = div.select_one("strong[data-bind*='service().serviceFullName']")

                if not address_tag or not report_btn: continue
                address_text = address_tag.get_text(strip=True)
                address_text = re.sub(r'(\d{5})(?:[-\s]?\d{4})\b', r'\1', address_text)
                portal_order_id = report_btn.get("id").split('_')[-1]
                report_type = report_type_tag.get_text(strip=True) if report_type_tag else None

                if address_text and portal_order_id: portal_order_list.append ({'portal_order_id': portal_order_id, 'address': address_text, 'order_type':report_type})

            print(f"{len(portal_order_list)} orders in portal : {portal_order_list}")
            logger.log( module="inspectionport-fetch_data", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"{len(portal_order_list)} orders in portal : {portal_order_list}", severity="INFO" )

            if not portal_order_list :  return []
            
            return portal_order_list

        except Exception as error:
            logger.log( module="inspectionport-fetch_data", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception fetching data: {error}", severity="INFO" )
            return []
        

    def inspectionport_formopen(self, orders, session, merged_json, order_details, order_id):
        """LSI Form check , address check and open form"""

        try:
            #checking order found from hybrid
            orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid) 
            if not orders_from_api: 
                logger.log( module="Inspectionport-inspectionport_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No orders from hybrid found {orders_from_api}.", severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            #checking order available from portal
            if not orders:
                logger.log( module="Inspectionport-inspectionport_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No orders in portal: {orders}", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            for order_from_api in orders_from_api:
                order_id=order_from_api.get("order_id","")

            target_orderid, tfs_orderid, is_qc, master_order_id = get_order_address_from_assigned_order(order_id, hybrid_token)
            form_types = ['Property Condition Report']

            #check for order ids from hybrid
            if not target_orderid and not tfs_orderid:
                logger.log( module="Inspectionport-inspectionport_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Order ids not found from hybrid: target id:{target_orderid}, tfs id {tfs_orderid}",severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            print(f"Target order id to check: {target_orderid}")
            logger.log( module="Inspectionport-inspectionport_fomopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"target order id from assigned orders found: {target_orderid}",severity="INFO")
            matched, portal_order, status = self.find_matching_order(orders, target_orderid, form_types)

            #matching order found
            if matched and (status == 'matched'):

                #check hold order
                is_hold = self.check_hold()
                if is_hold :
                    logger.log( module="Inspectionport-inspectionport_formopen",order_id=hybrid_orderid, action_type="HOLD", remarks=f"Order is in hold status on portal", severity="INFO" )
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                    return
                
                #Form  opening
                is_opened, err_msg = self.lauch_browser(portal_order)
                if not is_opened:
                    logger.log( module="Inspectionport-inspectionport_formopen",order_id=hybrid_orderid, action_type="Form_Not_Opened", remarks=f"Form not opened properly,err msg {err_msg}.", severity="INFO" )
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                    return

                self.inspectionport_formopen_fill(portal_order, session, merged_json, order_details, order_id, tfs_orderid)

            else :
                logger.log( module="Inspectionport-inspectionport_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No exact address match found, message: {status}", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
        except Exception as err:
            print("Error occured on form opening and filling")
            logger.log( module="Inspectionport-inspectionport_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Exception on form open function: error: {err}.", severity="INFO" )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return
        

    def find_matching_order(self, orders, target_orderid, form_types):
        '''Match address by portal order id'''

        try:
            address_found = False  
            for order in orders:
                portal_ID = order.get("portal_order_id")
                
                #Validating Order ID
                if portal_ID == target_orderid:
                    address_found = True
                    print(f"Address Found: {order['address']} || Poral ID: {portal_ID}")
                    logger.log( module="Inspectionport-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Found: {order['address']} || Poral ID: {portal_ID}", severity="INFO"  )

                    #Validating Form Types
                    if order.get("order_type") in form_types:
                        print(f"Form matched: {order.get("order_type")} || Poral ID: {portal_ID}")
                        logger.log( module="Inspectionport-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Form matched: {order.get("order_type")} || Poral ID: {portal_ID}", severity="INFO" )
                        return True, order, "matched"
                    
                    else:
                        print(f"New from type found: {order.get("order_type")}")
                        logger.log( module="Inspectionport-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"New from type found: {order.get("order_type")}", severity="INFO" )
                        return False, None, "form_not_matched"

                else:
                    print(f"orderID {portal_ID} not matched")
                    pass
            
            if not address_found:
                logger.log( module="Inspectionport-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Not Found: {order}", severity="INFO" )
                return False, None, "address_not_found"
            
        except Exception as error:
            print("Error occured while trying to find address")
            logger.log( module="Inspectionport-find_matching_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured: {error}", severity="INFO" )
            return False, None, "address_not_found"


    def lauch_browser(self, orders):
        '''Lauch inspection port form'''

        try:
            order_id = orders.get('portal_order_id')
            order_url = f'https://www.inspectionport.com/OrderDetail/EngagementLetter?orderId={order_id}'
            self.driver.get(order_url)
            time.sleep(3)

            link = self.wait_for_clickable(self.driver, By.XPATH,'/html/body/table/tbody/tr[13]/td/table/tbody/tr/td/a')
            if not link: 
                logger.log( module="Inspectionport-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Order Click link not found", severity="INFO" )
                return False, 'Not loaded'
            
            link.click()
            time.sleep(2)
            is_loaded = WebDriverWait(self.driver, 120).until( EC.visibility_of_element_located((By.TAG_NAME, "iframe")) )

            if is_loaded.is_displayed(): return True, None
            else:
                logger.log( module="Inspectionport-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Form is not loaded and opened", severity="INFO" )
                return False, 'Hold Order'

        except Exception as er: 
            logger.log( module="Inspectionport-lauch_browser", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured on opening form in new tab: {er}", severity="INFO" )
            print(f"Error on opening form"); return False, er
        

    
    def check_hold(self):
        '''Function to check if order is in hold status'''

        try:
            star_icon = self.driver.find_element(By.CSS_SELECTOR, "li.icon span.glyphicons")
            if star_icon.is_displayed(): return False
            else:
                logger.log( module="Inspectionport-check_hold", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Order is in hold status", severity="INFO" )
                return True
        except Exception as error: 
            logger.log( module="Inspectionport-check_hold", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Exception Occured on checking hold: {error}", severity="INFO" )
            return True 
        

    def inspectionport_formopen_fill(self, order, session, merged_json, order_details, order_id, tfs_orderid):
        '''Inspection port form processing controller'''

        try:
            #load datas from apis
            is_from_filled = False 
            is_pic_uploaded = False
            researchpad_data_retrival_url = env.RESEARCHPAD_DATA_URL
            config_path = 'json/inspectionportjson/pcr_inspectionport.json'
            form_config, merged_json = load_form_config_and_data(order_id, config_path, researchpad_data_retrival_url, session, merged_json, hybrid_token)

            if not form_config or not merged_json:
                logger.log( module="Inspectionport-inspectionport_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"Empty Form config: {form_config}, Empty merged_json: {merged_json}", severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                print("No details to fill ,quiting process")
                return  
            
            #genearte any special conditions
            condition_data = self.generate_condition(merged_json)
            if "entry_data" in merged_json and merged_json["entry_data"]:
                merged_json["entry_data"][0]["condition_data"] = condition_data

            logger.log( module="Inspectionport-inspectionport_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"merged_json: {merged_json}", severity="INFO" )

            #Form filling
            form_fill, error = self.fill_form_multi( merged_json, form_config)
            if not form_fill:
                logger.log( module="Inspectionport-inspectionport_formopen_fill",order_id=hybrid_orderid,action_type="ERROR",remarks=f"Error while filling the form: {error}",severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return 
            
            time.sleep(2)
            is_from_filled = True
            logger.log( module="Inspectionport-inspectionport_formopen_fill",order_id=hybrid_orderid,action_type="Completed",remarks=f"Completed entry form filling",severity="INFO" )

            #Upload photos 
            uploaded, error_msg = self.upload_pic_and_sig()
            if not uploaded:
                logger.log( module="Inspectionport-inspectionport_formopen_fill",order_id=hybrid_orderid,action_type="ERROR",remarks=f"Error while Uploading pics : {error_msg}",severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return
            
            time.sleep(2)
            is_pic_uploaded = True
            logger.log( module="Inspectionport-inspectionport_formopen_fill",order_id=hybrid_orderid,action_type="Completed",remarks=f"Completed Picture Uploading",severity="INFO" )

            #All process completed
            if is_from_filled and is_pic_uploaded:
                print("Order Completed Successfully")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
                update_pic_status(hybrid_orderid,"Uploaded",hybrid_token)
                return
            
            #Only Entry Completed
            elif is_from_filled :
                print("Entry Completed Successfully")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
                return
            
            #Issue in process
            else:
                print("Isue in uploading")
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                return

        except Exception as error:
            logger.log( module="Inspectionport-inspectionport_formopen_fill",order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception in form filling main: {error}",severity="INFO" )
            return
        

    def generate_condition(self, data_to_fill):
        try:


            # Iterate through each entry in entry_data
            for entry in data_to_fill.get("entry_data", []):
                sub_data = entry.get("sub_data", {})
                
                # Ensure 'sub_data' exists
                if not sub_data:
                    continue  # Skip this entry if no sub_data

                # Extract the external factors list from sub_data
                external_factors_list = sub_data.get("externalFactorsDetail", [])

                # If there are any external factors, we update the "externalFactors" field
                if external_factors_list:
                    sub_data["externalFactors"] = "Yes"
                else:
                    sub_data["externalFactors"] = "No"

                # After processing, store the updated sub_data back to the entry
                entry["sub_data"] = sub_data

            # Return the updated data_to_fill with modified sub_data
            return data_to_fill

        except Exception as error:
            # Log any error encountered
            logger.log(
                module="Inspectionport-generate_condition",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Exception in generating special functions: {error}",
                severity="INFO"
            )
            return data_to_fill



    def fill_form_multi(self, merged_json, form_config):
        '''LSI form filling section'''

        # switching to iframe
        WebDriverWait(self.driver, 120).until(  EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))  )
        print("switched to iframe")

        #wait form to load fully
        load_xpath = '/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[3]/div[2]/div/div/div/div/div/div[1]/input'
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, load_xpath)) )
        logger.log( module="Inspectionport-fill_form_multi", order_id=hybrid_orderid, action_type="SUCCESS",remarks=f"Form Loaded and Swicthed to iframe",severity="INFO" )
        
        key_expr_cache = {}
        value_cache = {}

        def get_keys_cached(key_expr):
            if key_expr not in key_expr_cache:
                key_expr_cache[key_expr] = re.findall(r"\['(.*?)'\]", key_expr)
            return key_expr_cache[key_expr]

        def extract_value_from_expr(expr):
            if expr in value_cache: return value_cache[expr]

            data_sources = { "sub_data": sub_data  }

            for prefix, data_source in data_sources.items():
                if expr.startswith(prefix):
                    suffix = expr[len(prefix):]
                    keys = get_keys_cached(suffix) if prefix == "entry_data[0]" else get_keys_cached(expr)
                    value = get_nested(data_source, keys, "")
                    value_cache[expr] = value
                    return value

            value_cache[expr] = expr
            return expr

        field_actions = {
            "input_field": data_filling_text,
            "js_execute": javascript_excecuter_filling,
            "radiobutton_data":radio_btn_click,
        }

        entry_data = merged_json.get('entry_data', [])
        entry = entry_data[0]
        sub_data = entry.get('sub_data', None) 
        self.inspection_date = sub_data.get('InspectionDate')

        for page in form_config.get("page", []):
            controls = page.get("Controls", [])

            if not isinstance(controls, (list, tuple)):
                print(f"Expected 'Controls' to be list but got {type(controls)}")
                continue

            for control in controls:
                if not isinstance(control, dict):
                    print(f"Control is not dict: {control}")
                    continue

                field_type = control.get("FieldType")
                values = control.get("values", [])

                for field in values:
                    if not (isinstance(field, list) and (len(field) == 3 or len(field) == 4)):
                        print(f"Invalid field format: {field}")
                        continue

                    if field_type == 'checkbox':
                        time.sleep(0.3)
                        field_name, expected_value, locator, locator_type = field
                        actual_value = sub_data.get(field_name, "").lower()
                        expected_value_lower = expected_value.lower()
                        if actual_value == expected_value_lower:
                            checkbox_tick_field(self.driver, locator, locator_type)
                            continue
                        else:continue

                    if field_type == 'simple_click':
                        field_name, locator, locator_type = field
                        click_element(self.driver, locator, locator_type)
                        break

                    key_expr, xpath, mode = field

                    try:
                        value = extract_value_from_expr(key_expr)

                        if value in [None, ""]: continue
                        action_func = field_actions.get(field_type)

                        if action_func: action_func(self.driver, value, xpath, mode)
                        else: 
                            logger.log(module="Inspectionport-fill_form_multi",order_id=hybrid_orderid,  action_type="Check_condition",remarks=f"Unknown field type: {field_type}", severity="INFO" )
                            print(f"Unknown field type: {field_type}")

                    except Exception as e: 
                        logger.log(module="Inspectionport-fill_form_multi",order_id=hybrid_orderid,  action_type="EXCEPTION",remarks=f"Exception in filling field {key_expr}: Exception {e}", severity="INFO" )
                        print(f"Exception filling field {key_expr}: {e}")

        return True,None

    
    def upload_pic_and_sig(self):
        '''Upload pic controller'''
        
        #Fetch from API
        data = fetch_upload_data(self, hybrid_orderid)
        if not data:
            logger.log( module="Inspectionport-upload_pic_and_sig", order_id=hybrid_orderid,action_type="Pic_Upload",remarks=f"No upload data found for order {self.order_id}",severity="INFO")
            return False, "Upload Data is None"
        
        # photos_url = data.get("photo_flder")
        photos_url = r'Z:\BPO\soft\PropVision_Photos\Keystone Holding\1602008\Verified' # need to update

        if isinstance(photos_url, str) and photos_url.strip():
            upload_result, error = self.upload_photos_to_order( photos_url)
            if not upload_result: return False, error

            time.sleep(1)
            upload_sig = self.Upload_sig()

            if upload_sig:  return True, "Completed"
            else: return False, "Issue in signature Upload"

        else:
            logger.log(module="Inspectionport-upload_pic_and_sig",order_id=hybrid_orderid,  action_type="Pic_Upload",remarks=f"Signature path is invalid or None {self.order_id}: {photos_url}", severity="INFO" )
            return False, "upload paths not in desired format"

        
    def upload_photos_to_order(self, photos_url):
        """Upload / re-upload photos in portal"""

        try:
            uploaded = 1
            photo_infos = self.build_photo_infos(photos_url)
            image_slots = self.driver.find_elements(By.CSS_SELECTOR, ".imageCell")

            #Delete photos if avialble
            if len(image_slots) > 0:
                try:
                    total_slots = len(image_slots)
                    logger.log( module="Inspectionport-upload_photos_to_order", order_id=hybrid_orderid, action_type="Condition_Check",remarks=f"{total_slots} Image already exists",severity="INFO" )

                    for slot_index in range(total_slots, 0, -1):
                        old_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".imageCell"))
                        delete_xpath = f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[7]/div/div[2]/div[2]/div[{slot_index}]/div[2]/div[5]/div[1]/label/span"
                        yes_xpath = f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[7]/div/div[2]/div[2]/div[{slot_index}]/div[2]/div[5]/div[2]/button[1]"

                        delete_btn = WebDriverWait(self.driver, 10).until( EC.element_to_be_clickable((By.XPATH, delete_xpath)) )
                        self.driver.execute_script("arguments[0].click();", delete_btn)
                        yes_btn = WebDriverWait(self.driver, 10).until( EC.element_to_be_clickable((By.XPATH, yes_xpath)) )
                        self.driver.execute_script("arguments[0].click();", yes_btn)

                        WebDriverWait(self.driver, 10).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".imageCell")) < old_count)

                except Exception as err:
                    logger.log( module="Inspectionport-upload_photos_to_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception during deleting existing photos: {err}", severity="INFO" )
                    return False, err

            #Upload photos
            for photo_info in photo_infos:
                image_path = photo_info["path"]
                description = photo_info["name"].lower()

                #Upload to fileinput
                file_input = self.driver.find_element(By.CSS_SELECTOR, 'input.upload-file[type="file"]')
                self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                self.driver.execute_script("arguments[0].value = '';", file_input)
                file_input.send_keys(image_path)
                logger.log( module="Inspectionport-upload_photos_to_order", order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Uploading image: {image_path}", severity="INFO")

                WebDriverWait(self.driver, 60).until_not(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.uploading-message'), 'Uploading...'))

                #Enter Description
                desc_to_enter = self.parse_jpg(description)
                time.sleep(0.5)
                data_filling_text( self.driver, desc_to_enter, f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[7]/div/div[2]/div[2]/div[{uploaded}]/div[2]/div[2]/div/textarea", "xpath" )

                #Date
                date_xpath = f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[7]/div/div[2]/div[2]/div[{uploaded}]/div[2]/div[3]/div/div/div/input"
                date_element = self.wait_for_clickable(self.driver, By.XPATH, date_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", date_element)
                self.driver.execute_script("arguments[0].value = '';", date_element)
                set_datepicker_date( self.driver, date_element, self.inspection_date )

                # Select image Role
                image_role = self.get_image_role(description)
                dropdown = Select( WebDriverWait(self.driver, 20).until( EC.presence_of_element_located(( By.XPATH,
                            f"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/" f"div[7]/div/div[2]/div[2]/div[{uploaded}]/div[2]/div[4]/div/div[1]/div/select" ))))
                try:
                    time.sleep(0.5)
                    dropdown.select_by_visible_text(image_role)
                except:
                    dropdown.select_by_visible_text("Additional Photo")

                uploaded += 1
                time.sleep(0.3)

            return True, "Completed"

        except Exception as error:
            logger.log( module="Inspectionport-upload_photos_to_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception during uploading photos: {error}", severity="INFO" )
            return False, error
        
        
    def Upload_sig(self):
        '''Function to upload siganture'''

        try:
            signature_array = ["/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[8]/div/div[1]/div[2]/div[1]/button",
                               "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[8]/div/div[1]/div[2]/div[2]/button",
                               "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[8]/div/div[1]/div[2]/div[3]/button",
                               "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[8]/div/div[1]/div[2]/div[4]/button"]
            
            sig_xpath = random.choice(signature_array)
            sig_element = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, sig_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sig_element)
            self.driver.execute_script("arguments[0].click();", sig_element)
            is_signed = self.sign_form()

            if is_signed :return True
            else: return False

        except Exception as error:
            logger.log( module="Inspectionport-Upload_sig", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception during selecting signature: {error}", severity="INFO" )
            return False, error


    def sign_form(self):
        '''function to enter password and sign form'''

        try:
            click_element(self.driver,"/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[8]/div/div[2]/div[2]/div[2]/button",By.XPATH)
            self.driver.switch_to.default_content()
            time.sleep(1)

            if self.is_element_visible(self.driver, By.XPATH, "//div[contains(@class, 'send-auth') and contains(@class, 'modal')]//h3[contains(text(), 'Login to Appraisal Port')]", 10):
                file_input = self.driver.find_element(By.XPATH, '//*[@id="password"]')
                file_input.send_keys(self.password)
                click_element(self.driver,"/html/body/div[6]/div[3]/a[1]",By.XPATH)
                logger.log( module="Inspectionport-sign_form", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Signed with password", severity="INFO" )
                return True
            
            logger.log( module="Inspectionport-sign_form", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Signed the form", severity="INFO" )
            return True

        except Exception as err: 
            logger.log( module="Inspectionport-sign_form", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception occured on clicking sign and password {err}", severity="INFO" )
            return False

    
    def parse_jpg(self,description):
        '''Function to remove the .jpg'''

        try:
            cleaned_desc = re.sub(r'\.(jpg|jpeg|png|bmp|gif|webp|tiff|svg)$', '', description.strip(), flags=re.IGNORECASE)
            return cleaned_desc.strip()
        except Exception as error : 
            logger.log( module="Inspectionport-parse_jpg", order_id=hybrid_orderid, action_type="Exception", remarks=f"exception in removing jpg {description}", severity="INFO" )


    def build_photo_infos(self,folder_path):
        '''Build paths for each photo'''

        photo_infos = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                photo_infos.append({  "name": os.path.splitext(file)[0],"path": os.path.join(folder_path, file)  })
        return photo_infos
    

    def get_image_role(self, desc):
        '''Function to get image role'''
        
        try:
            filename = os.path.splitext(desc)[0].strip().lower() 
            mappings = {"subject front view":"Subject Front View", "subject street view":"Subject Street View", "address verification":"Address Verification"}


            for key , text in mappings.items():
                if key == filename:
                    return text
                
            return "Additional Photo"

        except Exception as error:
            logger.log( module="Inspectionport-get_image_role", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception occured on getting image role {error}", severity="INFO" )
            return "Additional Photo"
    

    #Supporting UTIL METHOD
    def wait_for_element(self, by, value, timeout=30):
        return WebDriverWait(self.driver, timeout).until(  EC.presence_of_element_located((by, value)) )
    
    def wait_for_clickable(self, driver, by, value, timeout=30):
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    
    def is_element_visible(self, driver, by, value, timeout):
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException: return False

