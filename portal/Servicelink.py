
import os
import re
import time
import pytz
import logging
import datetime
import tempfile
from PIL import Image
from io import BytesIO
from config import env
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin
from utils.glogger import GLogger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import (get_order_address_from_assigned_order, handle_login_status, lsi_next_click,checkbox_tick_field_lsi,
params_check, setup_driver, update_order_status, get_nested, data_filling_text, javascript_excecuter_filling, input_dropdown_field,
scrape_and_fill,fetch_upload_data, update_portal_login_confirmation_status, load_form_config_and_data,tfs_statuschange)

# Load variables from .env file
load_dotenv()
logger = GLogger()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
process_type, hybrid_orderid,hybrid_token = params_check()                      


class Servicelink:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.order_id = None
        self.portal_key = portal_key
        logging.basicConfig(level=logging.INFO)

    def login_to_portal(self):
        """Login to the portal with username/password and check based on URL keyword."""
        
        try:
            setup_driver(self)
            self.driver.get(self.portal_url)
            print("Opening portal login ...")

            #Enter Username
            WebDriverWait(self.driver, 20).until( EC.visibility_of_element_located((By.ID, "userName")) )
            self.driver.find_element(By.ID, "userName").clear()
            self.driver.find_element(By.ID, "userName").send_keys(self.username)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            #Enter Password
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "password")))
            self.driver.find_element(By.ID, "password").clear()
            self.driver.find_element(By.ID, "password").send_keys(self.password)

            next_button = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "next")))
            WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, "temp-overlay")))

            # Then click the button
            next_button = WebDriverWait(self.driver, 20).until( EC.element_to_be_clickable((By.ID, "next")))
            next_button.click()

            sign_in = WebDriverWait(self.driver, 20).until( EC.element_to_be_clickable((By.ID, 'verifyCode')))
            sign_in.click()

            if "Enter your verification code below" in self.driver.page_source:
                print("verification page detected. Waiting for user to input the code...")

                try:
                    # Inject a non-blocking notification into the browser
                    js_notification = """
                    var div = document.createElement('div');
                    div.id = 'otp-notification';
                    div.style.position = 'fixed';
                    div.style.top = '20px';
                    div.style.right = '20px';
                    div.style.backgroundColor = '#ff9800';
                    div.style.color = 'white';
                    div.style.padding = '20px';
                    div.style.zIndex = '99999';
                    div.style.borderRadius = '5px';
                    div.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
                    div.style.fontSize = '16px';
                    div.style.fontFamily = 'Arial, sans-serif';
                    div.innerHTML = '<strong>Action Required:</strong><br>Please enter the OTP in the verification field.<br><small>The script is waiting for your input...</small>';
                    document.body.appendChild(div);
                    """
                    self.driver.execute_script(js_notification)
                    print("Browser notification shown.")
                except Exception as e:
                    print(f"Error showing browser notification: {e}")

                if not self.wait_for_user_input():
                    self.login_status = f"Code input error occurred: {e}"
                    handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
                    return "Login error", self.driver


                time.sleep(10)  # Wait for final redirect
                current_url = self.driver.current_url.lower()
                print(f"Final URL after login: {current_url}")

                SUCCESS_KEYWORDS = ["providerportal","dashboard"]
                login_check_keywords = ["CombinedSigninAndSignup","providerportal"]
                login_success = any(k in current_url for k in SUCCESS_KEYWORDS)

                if process_type == "SmartEntry":
                    if login_success:
                        orders = self.fetch_data()
                        self.lsi_formopen( orders=orders, session=None,  merged_json=None,  order_details=self.order_details, order_id=self.order_id )
                    else:
                        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                        handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

                else:
                    update_portal_login_confirmation_status(hybrid_orderid)
                    handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)
                    return self.driver
            else:    
                self.login_status = f"Code input error occurred: {e}"
                handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
                return "Login error", self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logger.log(module="LSI-login_to_portal", order_id=hybrid_orderid, action_type="Login_Check", remarks=f"Exception in login fucntion: {e}", severity="INFO" )
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            return "Login error", self.driver
        

    def wait_for_user_input(self,timeout=30, retries=3):
        '''Fucntion that check url change happened , if so user entered the code'''

        try:
            # Wait for the verification code input field to become visible
            code_input_locator = (By.ID, 'verificationCode')
            code_input = WebDriverWait(self.driver, timeout).until( EC.visibility_of_element_located(code_input_locator) )
            WebDriverWait(self.driver, 70).until(EC.url_changes(self.driver.current_url))
            logger.log(module="LSI-wait_for_user_input", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"verification code received from user", severity="INFO" )
            print(" User entered the verification code.")
            return True 
        
        except TimeoutException as e:
            logger.log(module="LSI-wait_for_user_input", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Timeout waiting for user input or page redirect: {e}", severity="INFO" )
            print(f"Timeout waiting for user input or page redirect: {e}")
            return False

        except Exception as e:
            logger.log(module="LSI-wait_for_user_input", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Error waiting for user input: {e}", severity="INFO" )
            print(f"Error waiting for user input: {e}")
            return False
        

    def fetch_data(self):
        '''Fetching order from portal'''

        try:
            logger.log(  module="LSI-fetch_data", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Starting Smart Entry Proccessing", severity="INFO" )
            self.wait_for_element(By.CSS_SELECTOR, '.provider-row-expandable')
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            soup = BeautifulSoup(self.driver.page_source , 'html.parser')
            order_containers = soup.select('.provider-dashboard-grid .provider-grid-body .provider-row-expandable') 

            portal_order_list = []

            for order in order_containers:
                link_tag = order.select_one('.provider-col-order a.blue-text')
                href = link_tag['href'] if link_tag and link_tag.has_attr('href') else None

                portal_ID = link_tag.text.strip() if link_tag else None

                address_tag = order.select_one('.provider-col-address')
                address = address_tag.text.strip() if address_tag else None

                product_tag = order.select_one('.provider-col-product span')
                product = product_tag.text.strip() if product_tag else None

                if href and portal_ID: portal_order_list.append({'link': href, 'address': address, 'product': product, 'portal_ID':portal_ID})

            if not portal_order_list:
                logger.log(  module="LSI-fetch_data", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Failed to fetch orders. Server returned empty.", severity="INFO" )
                return []
            
            count = len(portal_order_list)
            logger.log(module="LSI-fetch_data", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"{count} Orders in portal, Orders List: {portal_order_list}", severity="INFO" )
            print(f"{count} order in portal")
            return portal_order_list

        except Exception as error:
            logger.log( module="LSI-fetch_data", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception fetching data: {error}", severity="INFO" )
            return []
        

    def lsi_formopen(self, orders, session, merged_json, order_details, order_id):
        """LSI Form check , address check and open form"""

        try:
            #order details from hybrid frontend
            orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid) 
            form_types = ["BofA PCR - Exterior", "Exterior Property Condition Report", "PCR Plus - Exterior","Equity - Exterior Property Condition Report"]

            #checking order found from hybrid
            if not orders_from_api: 
                logger.log( module="LSI-lsi_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No orders from hybrid found {orders_from_api}.", severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            #checking order available from portal
            if not orders:
                logger.log( module="LSI-lsi_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No orders in portal", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            for order_from_api in orders_from_api:
                order_id=order_from_api.get("order_id","")

            target_orderid, tfs_orderid = get_order_address_from_assigned_order(order_id, hybrid_token)

            #check for order ids from hybrid
            if not target_orderid or not tfs_orderid:
                logger.log( module="LSI-lsi_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Order ids not found from hybrid: target id:{target_orderid}, tfs id {tfs_orderid}",severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return

            print(f"Target order id to check: {target_orderid}")
            logger.log( module="LSI-lsi_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"target order id from assigned orders found: {target_orderid}",severity="INFO")
            matched, portal_order, status = self.find_matching_order(orders, target_orderid, form_types)

            if matched and (status == 'matched'):
                order_url = portal_order.get('link')
                is_opened, err_msg = self.lauch_browser(order_url)

                if not is_opened:
                    logger.log( module="LSI-lsi_formopen",order_id=hybrid_orderid, action_type="Form_Not_Opened", remarks=f"Form not opened properly,err msg {err_msg}.", severity="INFO" )
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                    return

                self.lsi_formopen_fill(portal_order, session, merged_json, order_details, order_id, tfs_orderid)

            else :
                logger.log( module="LSI-lsi_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No exact address match found, message: {status}", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return

        except Exception as err:
            print("Error occured on form opening and filling")
            logger.log( module="LSI-lsi_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Exception on form open function: error: {err}.", severity="INFO" )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return


    def find_matching_order(self,orders, target_orderid, form_types):
        '''Match address by portal order id'''

        try:
            address_found = False  
            for order in orders:
                portal_ID = order.get("portal_ID")
                
                #Validating Order ID
                if portal_ID == target_orderid:
                    address_found = True
                    print(f"Address Found: {order['address']} || Poral ID: {order['portal_ID']}")
                    logger.log( module="LSI-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Found: {order['address']} || Poral ID: {order['portal_ID']}", severity="INFO"  )

                    #Validating Form Types
                    if order.get("product") in form_types:
                        self.form_type = order.get("product")
                        print(f"Form matched: {self.form_type} || Poral ID: {portal_ID}")
                        logger.log( module="LSI-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Form matched: {order.get("product")} || Poral ID: {portal_ID}", severity="INFO" )
                        return True, order, "matched"
                    
                    else:
                        print(f"New from type found: {order.get("product")}")
                        logger.log( module="LSI-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"New from type found: {order.get("product")}", severity="INFO" )
                        return False, None, "form_not_matched"

                else:
                    print(f"orderID {portal_ID} not matched")
                    pass
            
            if not address_found:
                logger.log( module="LSI-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Not Found: {order}", severity="INFO" )
                return False, None, "address_not_found"
            
        except Exception as error:
            print("Error occured while trying to find address")
            logger.log( module="LSI-find_matching_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured: {error}", severity="INFO" )
            return False, None, "address_not_found"

    
    def lauch_browser(self,order_url):
        '''Open the form in new tab'''

        try:
            full_url = urljoin("https://ui.exostechnology.com", order_url)
            logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Opening order url: {full_url}", severity="INFO" )

            self.driver.get(full_url)
            time.sleep(5)
            click_order = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/span/div')

            #if the click the menu for open portal
            if not click_order:
                logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Click order button not loaded after 30 seconds", severity="INFO" )
                print("Order Click not found")
                return False, 'Click order button not loaded after 30 seconds'
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", click_order)
            time.sleep(0.5)

            try:
                click_order.click()
            except Exception as e:
                print(f" Failed to click order retry again: {e}")
                click_order = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/span/div')
                self.driver.execute_script("arguments[0].scrollIntoView(true);", click_order)
                time.sleep(0.5)
                click_order.click()
            
            #form open button
            upload_button = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/div/span[2]/div')
            if not upload_button:
                logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Upload order button not loaded after 30 seconds", severity="INFO" )
                print("Order Click not found")
                return False, 'Upload form button loaded after 30 seconds'

            main_window = self.driver.current_window_handle
            upload_button.click()
            time.sleep(5)

            if self.is_element_visible(self.driver, By.XPATH, "/html/body/app-root/orders/order-ordercontent/order-orderstatus/upload-report/div[3]/div/form/div",10):
                is_alert_handled = self.handle_alert()

                if not is_alert_handled : 
                    logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Alert cant be processed properly", severity="INFO" )
                    return False,'Issue in handling alert'
                
                upload_button = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/div/span[2]/div')

                if not upload_button: 
                    print("Upload report option not available")
                    click_order = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/span/div')
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", click_order)
                    time.sleep(0.5)
                    click_order.click()
                        
                main_window = self.driver.current_window_handle
                upload_button.click()
                time.sleep(5)
            
            WebDriverWait(self.driver, 20).until(lambda d: len(d.window_handles) > 1)

            for handle  in self.driver.window_handles:
                if handle != main_window:
                    self.driver.switch_to.window(handle)
            
            confirm_switch = self.is_element_visible(self.driver, By.XPATH,"/html/body/div[72]/div/div[3]/div[1]/form/article/div", timeout=20)
            logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Successfully switched to new tab", severity="INFO" )
            print(f"Switched to new tab: {self.driver.current_url}")

            return True, None
        
        except Exception as er: 
            logger.log( module="LSI-lauch_browser", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured on opening form in new tab: {er}", severity="INFO" )
            print(f"Error on opening form"); return False, er


    def handle_alert(self):
        '''handle the extra box to open form'''

        try:
            logger.log( module="LSI-handle_alert",order_id=hybrid_orderid, action_type="Alert", remarks=f"Processing the alert.", severity="INFO" )
            #Update in est time
            india_tz = pytz.timezone('Asia/Kolkata')
            us_eastern_tz = pytz.timezone('US/Eastern')
            now_ist = datetime.datetime.now(india_tz)
            now_us = now_ist.astimezone(us_eastern_tz)

            formatted_datetime = now_us.strftime("%Y-%m-%dT%H:%M")
            print(formatted_datetime) 

            input_elem = self.driver.find_element(By.NAME, "providerPortalDueDate")
            if not input_elem : print("Date input not interacting")

            #Append dates in each tab space on date field
            self.driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, input_elem, formatted_datetime)
            time.sleep(1)


            #Appennd reason and description
            select_element = self.wait_for_element(By.XPATH,"/html/body/app-root/orders/order-ordercontent/order-orderstatus/upload-report/div[3]/div/form/div/div[2]/div[2]/select")

            if not select_element : print("Issue in finding reason from dropdown,alert handling")
            select = Select(select_element)
            select.select_by_visible_text("POC Reschedule - Vacation")
            description = self.send_keys_with_wait(self.driver,By.XPATH, "/html/body/app-root/orders/order-ordercontent/order-orderstatus/upload-report/div[3]/div/form/div/div[2]/div[3]/textarea", "Vacation holidays")
            submit = self.wait_for_clickable(self.driver, By.XPATH,'/html/body/app-root/orders/order-ordercontent/order-orderstatus/upload-report/div[3]/div/form/div/div[3]/button[2]')

            if submit: 
                submit.click()
                try:
                    WebDriverWait(self.driver, 20).until_not(  EC.presence_of_element_located((By.CSS_SELECTOR, ".loading-mask")) )
                except:
                    print("Loading mask still present… continuing anyway")

                self.driver.refresh()
                time.sleep(2)
                click_order = self.wait_for_clickable(self.driver, By.XPATH,'//*[@id="Order Details - Top"]/div[1]/div/div[2]/span/div')

                if not click_order:print("Order Click not found"); return False
                self.driver.execute_script("arguments[0].scrollIntoView(true);", click_order)
                time.sleep(0.5)

                for _ in range(5):
                    try:
                        click_order.click()
                        logger.log( module="LSI-handle_alert",order_id=hybrid_orderid, action_type="Alert", remarks=f"Alert processes succesfully.", severity="INFO" )
                        return True
                    except Exception as e:
                        print(f"Retry clicking order (blocked): {e}")
                        time.sleep(1)

                logger.log( module="LSI-handle_alert",order_id=hybrid_orderid, action_type="Alert", remarks=f"Failed to click order button after multiple retries", severity="INFO" )
                print("Failed to click order button after multiple retries"); return False
            
            else: 
                logger.log( module="LSI-handle_alert",order_id=hybrid_orderid, action_type="Alert", remarks=f"issue in submit button not found in form alert box", severity="INFO" )
                print("issue in submit button not found in form alert box"); return False

        except Exception as er: 
            logger.log( module="LSI-handle_alert",order_id=hybrid_orderid, action_type="Alert", remarks=f"Exception on handling alert box to open form : {er}", severity="INFO" )
            print(f"Exception on handling alert box to open form : {er}"); return False


    def lsi_formopen_fill(self, order, session, merged_json, order_details, order_id, tfs_orderid):
        '''LSI form processing main'''

        try:
            #loading configs and data to fill
            is_from_filled = False
            is_pic_uploaded = False
            researchpad_data_retrival_url = env.RESEARCHPAD_DATA_URL
            
            if self.form_type == 'BofA PCR - Exterior': config_path = 'json/servicelinkjson/Bofa_insp.json'
            else: config_path = 'json/servicelinkjson/Exterior_condition_report.json'

            form_config, merged_json = load_form_config_and_data(order_id, config_path, researchpad_data_retrival_url, session, merged_json, hybrid_token)
            if not form_config or not merged_json:
                print("No json or rpad data , Quiting process")
                return
            
            #generate any special conditions
            condition_data = self.generate_condition(merged_json)
            if "entry_data" in merged_json and merged_json["entry_data"]:
                merged_json["entry_data"][0]["condition_data"] = condition_data

            logger.log( module="LSI-lsi_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"merged_json: {merged_json}", severity="INFO" )

            #Form filling
            form_fill, error = self.fill_form_multi( merged_json, form_config)
            if not form_fill:
                logger.log( module="LSI-lsi_formopen_fill",order_id=hybrid_orderid,action_type="ERROR",remarks=f"Error while filling the form: {error}",severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return

            time.sleep(0.5)
            is_from_filled = True
            logger.log( module="LSI-lsi_formopen_fill",order_id=hybrid_orderid,action_type="Completed",remarks=f"Completed entry form filling",severity="INFO" )

            #Upload signature and photos 
            uploaded, error_msg = self.upload_pic_and_sig()
            if not uploaded:
                logger.log( module="LSI-lsi_formopen_fill",order_id=hybrid_orderid,action_type="ERROR",remarks=f"Error while Uploading pics : {error_msg}",severity="INFO" )
                return
            
            time.sleep(0.5)
            is_pic_uploaded = True
            logger.log( module="LSI-lsi_formopen_fill",order_id=hybrid_orderid,action_type="Completed",remarks=f"Completed Picture Uploading",severity="INFO" )

            #Upload map 
            is_uploaded, error_ms = self.upload_map()

            if is_uploaded and is_from_filled and is_pic_uploaded:
                print("Order Completed Successfully")
                tfs_statuschange(tfs_orderid, "26", "3", "14")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Completed",hybrid_token)
                return
            
            elif is_from_filled:
                print("Form filling only completed")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Completed",hybrid_token)
                return
            
            else:
                print("Isue in uploading")
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                return
        
        except Exception as error:
            logger.log( module="LSI-lsi_formopen_fill",order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception in form filling main: {error}",severity="INFO" )
            return


    def upload_pic_and_sig(self):
        '''Fetch and Upload main'''

        #get phot and signature url from api
        data = fetch_upload_data(self, hybrid_orderid)
        if not data:
            logger.log( module="LSI-upload_pic_and_sig", order_id=hybrid_orderid,action_type="Pic_Upload",remarks=f"No upload data found for order {self.order_id}",severity="INFO")
            return False, "Upload Data is None"
        
        # signature_path = data.get("siganture_folder")
        # photos_url = data.get("photo_flder")

        signature_path = r'Z:\BPO\NGL Employees Documents\Propinspect\Final\keystone\KSH_ Patrick McEneely.JPG'
        photos_url = r'Z:\BPO\soft\PropVision_Photos\Keystone Holding\1628927\Verified' # need to update
        
        if not isinstance(signature_path, str) or not signature_path.strip():
            logger.log(module="LSI-upload_pic_and_sig", order_id=hybrid_orderid, action_type="Pic_Upload", remarks=f"Invalid or missing signature path : {signature_path}", severity="ERROR")
            # return False, "Invalid signature path"

        if not isinstance(photos_url, str) or not photos_url.strip():
            logger.log(module="LSI-upload_pic_and_sig", order_id=hybrid_orderid, action_type="Pic_Upload", remarks=f"Invalid or missing photo URL : {photos_url}", severity="ERROR")
            return False, "Invalid photo URL"

        #upload photos 

        upload_result, error = self.upload_photos_to_order(signature_path, photos_url)
        if upload_result:
            return True, error
        else:
            return False, error
        

    def upload_photos_to_order(self,signature_path, photo_path):
        '''Uploading photos from folder to portal slots'''

        try:
            uploaded = 0

            def upload_to_slot(photo_descriptions, pic_infos):
                '''Inner fucntion to upload to slot'''

                nonlocal uploaded
                photo_slots = self.driver.find_elements(By.CSS_SELECTOR, 'div.image-slot')

                for photo_info in pic_infos:
                    image_path = photo_info['path']
                    folder_image_name = photo_info['name'].lower()

                    for image_name, description_text in photo_descriptions.items():
                        if self.clean(image_name) == self.clean(folder_image_name.split('.')[0]):
                            for slot in photo_slots:
                                portal_description = slot.get_attribute('data-description').lower()

                                if description_text.lower() in portal_description:
                                    try:
                                        input_element = slot.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                                        self.driver.execute_script("arguments[0].classList.remove('hidden')", input_element)
                                        self.driver.execute_script("arguments[0].style.display = 'block';", input_element)
                                        time.sleep(0.5)
                                        input_element.send_keys(image_path)
                                        logger.log( module="upload_photos_to_order", order_id=hybrid_orderid,action_type="SUCCESS",remarks=f"Uploaded {image_name} to {portal_description}",severity="INFO")
                                        self.wait_for_loading_spinner_to_disappear(keyword="Loading Report")
                                        is_uploaded = self.recheck_upload (slot)
                                        if is_uploaded :uploaded += 1
                                        else: pass
                                    except Exception as e: 
                                        logger.log( module="upload_photos_to_order", order_id=hybrid_orderid,action_type="FAILED",remarks=f"Failed to upload {image_name} to {portal_description}: {e}",severity="INFO")
                    
            SIGNATURE_DESC = { "signature": "agent preparer signature"}
            PAGE1_DESC = {"SUBJECT(FRONT VIEW)": "subject (front view) photo", "SUBJECT(ANGLED)": "Subject (Angled) Photo", "ADDRESS VERIFICATION": "address verification photo"}
            PAGE2_DESC = {"STREET VIEW(LEFT)": "Street View (Left) Photo", "STREET VIEW(RIGHT)": "Street View (Right) Photo", "STREET VIEW(ACROSS STREET)": "Street View (Across Street) Photo"}
            signature_infos = [{ "name": "signature", "path": signature_path}]
            photo_infos = self.build_photo_infos(photo_path)

            upload_to_slot(SIGNATURE_DESC, signature_infos)
            lsi_next_click(self.driver)
            upload_to_slot(PAGE1_DESC, photo_infos)
            lsi_next_click(self.driver)
            upload_to_slot(PAGE2_DESC, photo_infos)

            if uploaded >= 6:
                print("Success Completion of Pic Uploading")
                logger.log( module="upload_photos_to_order", order_id=hybrid_orderid,action_type="SUCCESS",remarks=f"Success Completion of Pic Upload",severity="INFO")
                return True, "completed"
            
            else:
                print(f"Couldnt Upload all photos")
                logger.log( module="upload_photos_to_order", order_id=hybrid_orderid,action_type="ERROR",remarks=f"Cant Upload all phtos , count: {uploaded}",severity="INFO")
                return False, 'All photos not uploaded'
            
        except Exception as error:
            logger.log( module="upload_photos_to_order", order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception during uploading photos: {error}",severity="INFO")
            return False, error
      

    def generate_condition(self, merged_json):
        '''to generate special conditions'''
        for entry in merged_json.get("entry_data", []):
            sub_data = entry.get("sub_data", {})
            sub_data['agent_financial_interest'] = "No"
        return merged_json
    

    def clean(self, name):
        '''Clean the photo urls to remove slashes'''
        return name.lower().replace('-', '').replace('_', '').replace(' ', '').strip()
    

    def build_photo_infos(self,folder_path):
        '''Build paths for each photo'''
        photo_infos = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                photo_infos.append({  "name": os.path.splitext(file)[0],"path": os.path.join(folder_path, file)  })
        return photo_infos
    

    def recheck_upload(self,slot, timeout=20):
        '''Function to recheck if upload completed'''

        try:
            WebDriverWait(self.driver, timeout).until(lambda d: len(slot.find_elements(By.TAG_NAME, "img")) > 0)
            uploaded_image = slot.find_element(By.CSS_SELECTOR, 'img')
            field_name = slot.get_attribute('data-description')
                
            if uploaded_image.get_attribute('src'): 
                logger.log( module="recheck_upload", order_id=hybrid_orderid,action_type="Condition_Check",remarks=f"Photo Upload recheck Success for slot {field_name}",severity="INFO")
                print(f"Recheck successful: Image has been uploaded: {field_name}")
                return True
            else: 
                logger.log( module="recheck_upload", order_id=hybrid_orderid,action_type="Condition_Check",remarks=f"Photo Upload recheck failed for slot {field_name}",severity="INFO")
                print("Recheck failed: No image found after upload.")
                return False
                    
        except Exception as e:
            logger.log( module="recheck_upload", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on rechecking photo Upload for {field_name}, error: {e}",severity="INFO")
            return False
    

    def wait_for_loading_spinner_to_disappear(self, keyword):
        '''Function to check load spinner to end'''

        try:
            wait = WebDriverWait(self.driver, timeout=40)

            def condition(d):
                spinners = d.find_elements(By.XPATH, f"//h4[contains(text(),'{keyword}')]")
                still_visible = []
                for s in spinners:
                    try:
                        style = d.execute_script("""
                            const el = arguments[0].closest('div.loading-wrapper') || arguments[0];
                            const cs = window.getComputedStyle(el);
                            return {display: cs.display, visibility: cs.visibility, opacity: cs.opacity, text: arguments[0].innerText
                            };
                        """, s)
                        if style["display"] != "none" and style["visibility"] != "hidden" and float(style["opacity"]) > 0: still_visible.append(style)
                    except Exception: continue

                if still_visible:
                    for st in still_visible: print(f"   text={st['text']!r}, display={st['display']}, "f"visibility={st['visibility']}, opacity={st['opacity']}")
                    logger.log( module="wait_for_loading_spinner_to_disappear", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Loading spinner not closed in given time",severity="INFO")
                    return False

                print("Loading Completed")
                return True

            wait.until(condition)
        except Exception as error:
            logger.log( module="wait_for_loading_spinner_to_disappear", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on laoding spiiner waiting for {keyword} , error: {error}",severity="INFO")
            return False


    def fill_form_multi(self, merged_json, form_config):
        '''LSI form filling section'''

        key_expr_cache = {}
        value_cache = {}
        self.wait_for_form_opned()

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
            "input_dropdown": input_dropdown_field,
            "button_click": lsi_next_click,
            "date_input": javascript_excecuter_filling,
        }

        entry_data = merged_json.get('entry_data', [])
        entry = entry_data[0]
        sub_data = entry.get('sub_data', None) 

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
                        field_name, expected_value, locator, locator_type = field
                        actual_value = sub_data.get(field_name, "").lower()
                        expected_value_lower = expected_value.lower()
                        if actual_value == expected_value_lower:
                            checkbox_tick_field_lsi(self.driver, locator, locator_type)
                            continue
                        else:continue

                    key_expr, xpath, mode = field

                    try:
                        if field_type == 'button_click':
                            lsi_next_click(self.driver)
                            continue

                        if field_type == 'scrape_fill':
                            scrape_and_fill(self.driver, xpath, key_expr, mode)
                            continue

                        value = extract_value_from_expr(key_expr)

                        if value in [None, ""]: continue

                        action_func = field_actions.get(field_type)

                        if action_func: action_func(self.driver, value, xpath, mode)
                        else: print(f"Unknown field type: {field_type}")

                    except Exception as e:
                        logger.log( module="LSI-fill_form_multi", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exception filling field {key_expr}: Exception : {e}",severity="INFO")
                        print(f"Exception filling field {key_expr}: {e}")

        return True,None
    

    def wait_for_form_opned(self):
        '''check whether form opned in croped format'''

        try:
            confirm = WebDriverWait(self.driver, 20).until( EC.element_to_be_clickable( (By.XPATH, "/html/body/div[72]/div/div[3]/div[1]/form/article/div/input[17]") ))
            return True
        except Exception as error:
            next = WebDriverWait(self.driver, 20).until( EC.element_to_be_clickable( (By.XPATH, "//*[@id='navbar']/ul/li[3]/span/button[3]") )).click()
            previous = WebDriverWait(self.driver, 20).until( EC.element_to_be_clickable( (By.XPATH, "//*[@id='navbar']/ul/li[3]/span/button[1]") )).click()
            return True


    def upload_map(self):
        '''Select map and Upload map'''

        if self.form_type == "BofA PCR - Exterior": return self.bofa_map()
        else: return self.inspection_map()


    def inspection_map(self):
        '''Upload inspection orders map'''

        try:   #Selecting Location Map
            logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Proceeding with location map uploading",severity="INFO")
            lsi_next_click(self.driver)
            lsi_next_click(self.driver)
            time.sleep(2)

            #Click map on nav
            map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/button")
            if not map:
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map upload button not in navbar",severity="INFO")
                return False , "No map Button"
            
            #select location map from dropdown
            map.click()
            location = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/div/a[1]")
            if not location: 
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Location map button not in dropdown",severity="INFO")
                return False , "No location map Button"
            
            location.click()
            print("Opening location map in 15 sec")
            time.sleep(15)

            #wait for map to load
            confirm_map =  self.wait_for_clickable(self.driver, By.XPATH, "//*[@id='maps-accept']")
            if not confirm_map:
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map1 confirm selection button not available",severity="INFO")
                return False , "No confirm map Button"
            
            confirm_map.click()
            self.wait_for_loading_spinner_to_disappear(keyword="Loading Map")
            print("Map loaded")
            time.sleep(1)

            #check for alert 
            if self.is_element_visible(self.driver, By.XPATH, "/html/body/div[60]/div/div/div[1]/h4",timeout=5):
                try:
                    Location_map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[60]/div/div/div[2]/div[2]/div/ul/li[1]") 
                    Location_map.click()
                    time.sleep(1)
                    importt = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[60]/div/div/div[3]/button[2]") 
                    importt.click()
                    logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Proceeding with map uploading",severity="INFO")
                    time.sleep(3)
                except Exception as error:
                    logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exception on handling alert for location: {error}",severity="INFO")
                    return False , " Alert Handling Issue"

            logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Location map successfully selected",severity="INFO")
            print("Location map selected successfully")
            time.sleep(2)

        except Exception as error :
            logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on inspection order first location map selection {error}",severity="INFO")
            return False , error
        
        
        try:   #Ariel Map Selection
            logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Proceeding with Ariel map uploading",severity="INFO")
            lsi_next_click(self.driver)
            time.sleep(1)

            #select Map
            map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/button")
            if not map:
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map upload button not in navbar",severity="INFO")
                return False , "No map Button"
            
            #select aerial map from dropdown
            map.click()
            aerial = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/div/a[2]")
            if not aerial: 
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"aerial map button not in dropdown",severity="INFO")
                return False , "No aerial map Button"
            
            aerial.click()
            print("Opening location map in 15 sec")
            time.sleep(10)

            #Select map 
            confirm_map =  self.wait_for_clickable(self.driver, By.XPATH, "//*[@id='SaveAerialMap']")
            time.sleep(4)
            if not confirm_map:
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map2 confirm selection button not available",severity="INFO")
                return False , "No confirm map Button"
            
            confirm_map.click()
            self.wait_for_loading_spinner_to_disappear(keyword="Loading Map")
            print("Map loaded")
            time.sleep(1)

            if self.is_element_visible(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[1]/h4",5):
                aerial_map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[2]/div[2]/div/ul/li[2]") 
                aerial_map.click()
                time.sleep(1)
                importt = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[3]/button[2]") 
                importt.click()
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Aeriel map selected",severity="INFO")
                try:
                    WebDriverWait(self.driver, 15).until_not(  EC.visibility_of_element_located((By.ID, "aerial-selection-modal")) )
                    logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Aerial map modal closed",severity="INFO")
                except:
                    logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Modal still open, forcing close",severity="INFO")

            #Saving Order In portal
            time.sleep(2)
            is_save = self.lsi_order_save()
            if is_save: 
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Aeriel map successfully selected",severity="INFO")
                print("Location map selected successfully")
                return True, "Success"
            else: 
                logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="ERROR",remarks=f"Aeriel map not successfully selected , Order Save Issue",severity="INFO")
                return False, "Order save Error"

        except Exception as error :
            logger.log( module="inspection_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on inspection order second ariel map selection {error}",severity="INFO")
            return False , error
        
    
    def bofa_map(self):
        '''Fucntion to select bofa map and Upload'''

        try:   #Aerieal Close up (1/4 miles)
            logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Proceeding with AERIAL bofa map uploading",severity="INFO")
            lsi_next_click(self.driver)
            time.sleep(2)

            #Click map from nav
            map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/button")
            if not map:
                logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map upload button not in navbar",severity="INFO")
                return False , "No map Button"
            
            #Choose aerial from dropdown
            map.click()
            aerial = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/div/a[2]")
            if not aerial:
                logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Error",remarks=f"aerial map button not in dropdown",severity="INFO")
                return False , "No aerial map Button"
            
            aerial.click()
            print("Opening aerial map in 15 sec")
            time.sleep(10)
            
            #Select map 
            confirm_map =  self.wait_for_clickable(self.driver, By.XPATH, "//*[@id='SaveAerialMap']")
            if not confirm_map:
                logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map1 confirm selection button not available",severity="INFO")
                return False , "No confirm map Button"
            
            confirm_map.click()
            self.wait_for_loading_spinner_to_disappear(keyword="Loading Map")
            print("Map uploaded successfully")
            time.sleep(2)

            #check for alert 
            if self.is_element_visible(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[1]/h4",5):
                try:
                    aerial_map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[2]/div[2]/div/ul/li[1]") 
                    aerial_map.click()
                    time.sleep(1)
                    importt =self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[3]/button[2] ") 
                    importt.click()
                    time.sleep(3)

                except Exception as error:
                    logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exception on handling alert for 1/4 aerial: {error}",severity="INFO")
                    return False , " Alert Handling Issue"

            logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"1/4 aerial map successfully selected",severity="INFO")
            print("Aerial close up 1/4 selected")

        except Exception as err:
            logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on bofa_map order frst AERIAL map selection {err}",severity="INFO")
            return False , err
        
        try:   #AERIAL  BIRDS  EYE

            map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/button")
            if not map:
                logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Error",remarks=f"Map upload button not in navbar",severity="INFO")
                return False , "No map Button"
            
            #Choose aerial from dropdown
            map.click()
            aerial = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/div/a[2]")
            if not aerial:
                logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Error",remarks=f"aerial map button not in dropdown",severity="INFO")
                return False , "No aerial map Button"
            
            aerial.click()
            print("Opening aerial map in 15 sec")
            time.sleep(10)

            #wait to load completely
            close_btn = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/div[95]/div[1]/div/span[2]/a[1]")

            #Zoom out 6 times to get birds eye view
            for x in range(6):
                zoom_out = self.wait_for_clickable(self.driver, By.XPATH , "/html/body/div[95]/nav/div/div[2]/ul/li[2]/button")
                zoom_out.click()
                time.sleep(1)

            time.sleep(4)

            #Take screenshot in map canvas
            canvas_container = self.wait_for_clickable(self.driver, By.CLASS_NAME, 'canvas-container')
            location = self.driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {x: rect.left, y: rect.top, width: rect.width, height: rect.height};
            """, canvas_container)

            screenshot_bytes = self.driver.get_screenshot_as_png()
            screenshot = Image.open(BytesIO(screenshot_bytes))
            width, height = screenshot.size
            crop_width=600
            crop_height=400
            center_x, center_y = width // 2, height // 2

            # Compute crop box
            left = center_x - crop_width // 2
            top = center_y - crop_height // 2
            right = center_x + crop_width // 2
            bottom = center_y + crop_height // 2

            # Crop and return
            cropped = screenshot.crop((left, top, right, bottom))
            time.sleep(1)

            # 4. Close popup
            close_btn.click()
            print("Screenshot Taken")
            map = self.wait_for_clickable(self.driver, By.XPATH, "/html/body/nav/div/ul/ul/li[5]/div/button")

            if self.is_element_visible(self.driver, By.XPATH, "/html/body/div[61]/div/div/div[1]/h4",5):
                cancel = self.wait_for_clickable(self.driver, By.XPATH,"//*[@id='aerial-selection-modal']/div/div/div[3]/button[1]")
                cancel.click()
                time.sleep(1)
            
            #Upload with folder name
            upload_dir = "./temp_uploads"
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                time.sleep(0.5)
                cropped.save(tmpfile.name)
                tmpfile.flush()
                self.wait_for_element(By.CSS_SELECTOR, 'div.map-slot')
                slot = self.driver.find_element(By.CSS_SELECTOR, 'div.map-slot')
                time.sleep(1)
                input_elem = slot.find_element(By.XPATH, '/html/body/div[72]/div/div[3]/div[1]/form/article/div/div[3]/input')
                self.driver.execute_script("arguments[0].style.display = 'block';", input_elem)
                time.sleep(2)
                input_elem.send_keys(tmpfile.name)

                try:  #recheck for image uploaded
                    self.wait_for_element( By.XPATH, "/html/body/div[72]/div/div[3]/div[1]/form/article/div/div[3]/img")
                    is_save = self.lsi_order_save()

                    if is_save: 
                        logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="Conditon_Check",remarks=f"Aeriel birds eye map successfully selected",severity="INFO")
                        print("Aeriel birds eye map selected successfully")
                        return True, "Success"
                    else: 
                        logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="ERROR",remarks=f"Aeriel birds eye map not successfully selected , Order Save Issue",severity="INFO")
                        return False, "Order save Error"
                    
                except Exception as err :
                    logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Aeriel birds eye map recheck order failed: {tmpfile}",severity="INFO"); return False

        except Exception as err:
            logger.log( module="bofa_map", order_id=hybrid_orderid,action_type="EXCEPTION",remarks=f"Exeption on bofa_map second brids eye AERIAL map selection {err}",severity="INFO")
            return False , err


    def lsi_order_save(self, retries=2):
        '''Function to save order'''

        for attempt in range(retries):
            try:
                time.sleep(1)
                order_save = self.wait_for_clickable(self.driver,By.XPATH, "/html/body/nav/div/ul/ul/li[1]/button")
                order_save.click()
                logger.log( module="lsi_order_save", order_id=hybrid_orderid,action_type="SUCCESS",remarks=f"Order Saved Successfully",severity="INFO")
                print("Order Saved Successfully")
                return True
            except Exception as error: time.sleep(1.5); print(f"retrying order saving {error},  ({attempt+1}/{retries})")
        
        logger.log( module="lsi_order_save", order_id=hybrid_orderid,action_type="ERROR",remarks=f"ould not save the order",severity="INFO")
        return False
    
    
    #Supporting UTIL METHOD
    def wait_for_element(self, by, value, timeout=30):
        return WebDriverWait(self.driver, timeout).until(  EC.presence_of_element_located((by, value)) )
    
    def wait_for_clickable(self,driver, by, value, timeout=30):
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    
    def is_element_visible(self,driver, by, value, timeout):
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException: return False

    def send_keys_with_wait(self,driver, by, value, keys, timeout=15):
        elem = self.wait_for_element(by, value)
        elem.clear()
        elem.send_keys(keys)
        return elem
            
