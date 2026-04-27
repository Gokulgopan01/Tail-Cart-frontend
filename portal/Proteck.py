import re
import os
import time
import logging
import requests
from config import env
from dotenv import load_dotenv
from utils.glogger import GLogger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from integrations.hybrid_bpo_api import HybridBPOApi
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (StaleElementReferenceException, TimeoutException)


from utils.helper import (load_form_config_and_data, handle_login_status, setup_driver, update_portal_login_confirmation_status,
data_filling_text,javascript_excecuter_filling,scrape_and_fill,params_check,update_order_status,get_order_address_from_assigned_order, 
fetch_upload_data, get_nested, click_element, select_field,select_checkboxes_list,radio_btn_click, fill_repairs_list,update_pic_status) 


# Load environment variables from the .env file
load_dotenv()
logger = GLogger()

ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
process_type, hybrid_orderid,hybrid_token = params_check()                        


class Proteck:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):

        logging.basicConfig(level=logging.INFO)
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.login_status = None
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None
        self.portal_key = portal_key
        self.order_details = None
        self.session = None
        self.portal_order_id = None
        self.is_inspection = False
     
    def login_to_portal(self):
        """Login to a portal"""

        try:
            setup_driver(self)
            self.driver.get(self.portal_url)
            WebDriverWait(self.driver, 20).until(  EC.visibility_of_element_located((By.XPATH, "//*[@id='UserNameOrEmail']")))

            # Enter the username and password
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").clear()
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").send_keys(self.username)
            self.driver.find_element(By.XPATH, "//*[@id='Password']").send_keys(self.password)

            # Submit the login form
            self.driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[2]/form/input[3]").click()

            # Wait for login success by checking page title
            WebDriverWait(self.driver, 60).until(EC.title_contains("Partner Portal"))
            title = self.driver.title
            login_check_keyword=["Partner Portal"]

            if process_type == "SmartEntry":
                login_success = any(k in title for k in login_check_keyword)

                if login_success:
                    orders = self.fetch_data()
                    self.proteck_formopen( orders=orders, session=None,  merged_json=None,  order_details=self.order_details, order_id=self.portal_order_id )
                    return self.driver
                else:
                    handle_login_status(title, self.username, login_check_keyword, self.portal_name)
                    return self.driver
            else:
                update_portal_login_confirmation_status(hybrid_orderid)
                handle_login_status(title, self.username, login_check_keyword, self.portal_name)
                return self.driver
        
        except Exception as e:
            logger.log( module="Proteck-fetch_data", order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Error during login to {self.portal_name}: {e}", severity="INFO" )
            self.login_status = f"Exception occurred: {e}"
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            return "Login error", self.driver


    def fetch_data(self):
        '''Fetch orders from portal'''

        try:
            dash_url ='https://partners.protk.com/workqueue/Open/PendingCompletion'
            self.driver.get(dash_url)
            time.sleep(4)

            self.session = requests.Session()
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])

            api_url = "https://partners.protk.com/v1/case?type=Open"
            response = self.session.get(api_url)
            open_data_json = response.json()
            ordersinprogress = len(open_data_json)

            if not ordersinprogress:
                logger.log( module="Proteck-fetch_data", order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"No order available in portal", severity="INFO" )
                return []
            
            portal_order_list = []
            for order in open_data_json:

                addres = order['address']
                parts = [
                    addres.get('address1', ''), addres.get('address2', ''),
                    addres.get('suite', ''), addres.get('city', ''),
                    addres.get('state', ''), addres.get('zip', '')]
                
                address = " ".join([p.strip() for p in parts if p and p.strip()])
                link = order['dataEntryFormUrl']
                status = order['caseDisplayStatus']
                portal_ordID = order['caseNumber']
                form = (order['servicesRequested'])
                form_type = form[0]

                portal_order_list.append({'link': link, 'address': address, 'order_status': status, 'form_type': form_type, 'portal_ordID':portal_ordID})

            return portal_order_list

        except Exception as error:
            logger.log( module="Proteck-fetch_data", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception fetching data: {error}", severity="INFO" )
            return []
        
    
    def proteck_formopen(self, orders, session, merged_json, order_details, order_id):
        '''Form open function main'''

        try:
            #checking order found from hybrid
            orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid) 
            if not orders_from_api: 
                logger.log( module="Proteck-proteck_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No order from hybrid matched: Hybrid_id: {hybrid_orderid}, {orders_from_api}.", severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            #checking order available from portal
            if not orders:
                logger.log( module="Proteck-proteck_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No orders in portal: {orders}", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            for order_from_api in orders_from_api:
                order_id=order_from_api.get("order_id","")

            target_orderid, tfs_orderid, is_qc, master_order_id = get_order_address_from_assigned_order(order_id, hybrid_token)

            #Form Types
            INP_form_types = ["PCR eValuation Exterior With Checklist","Property Condition Report Standalone","Property Condition Report","AVM and PCR"]
            Entry_form_types = ['IBPO with MIT', 'Homesteps', 'Homesteps BPO Interior', 'New Chase Exterior BPO on Apollo',
            'Exterior valuation with 3 sales comps and 3 listing comps', 'Exterior BPO', 'Fannie BPO', 'Evaluation' ]

            #check for order ids from hybrid
            if not target_orderid and not tfs_orderid:
                logger.log( module="Proteck-proteck_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Order ids not found from hybrid: target id: {target_orderid}, tfs_id: {tfs_orderid}",severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            print(f"Target order id to check: {target_orderid}")
            logger.log( module="Proteck-proteck_formopen", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Target order id from assigned orders found: {target_orderid}",severity="INFO")

            matched, portal_order, status = self.find_matching_order(orders, target_orderid, INP_form_types, Entry_form_types)
            
            if matched and (status == 'matched'):

                #open the form
                self.portal_order_id = portal_order.get('portal_ordID')
                is_opened, err_msg = self.lauch_browser(portal_order)
                if not is_opened:
                    logger.log( module="Proteck-proteck_formopen",order_id=hybrid_orderid, action_type="Form_Not_Opened", remarks=f"Form not opened properly,err msg {err_msg}.", severity="INFO" )
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                    return
                
                self.proteck_formopen_fill(portal_order, session, merged_json, order_details, order_id, tfs_orderid, master_order_id)
                return

            else :
                logger.log( module="Proteck-proteck_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"No addreses matched from portal, message: {status}", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
        except Exception as err:
            print("Error occured on form opening and filling")
            logger.log( module="Proteck-proteck_formopen",order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Exception on form open function: error: {err}.", severity="INFO" )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return


    def find_matching_order(self, orders, target_orderid, INP_form_types, Entry_form_types):
        '''Function to find address and Form type'''

        try:
            address_found = False  
            for order in orders:
                portal_ID = str(order.get("portal_ordID") )

                #Validating Order ID
                if portal_ID == target_orderid:
                    address_found = True
                    print(f"Address Found: {order['address']} || Poral ID: {portal_ID}")
                    logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Found: {order['address']} || Poral ID: {portal_ID}", severity="INFO"  )

                    #Validating inp Form Types
                    if order.get("form_type") in INP_form_types:
                        print(f"Form matched: {order.get("form_type")} || Poral ID: {portal_ID}")
                        self.is_inspection = True
                        logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Form matched: {order.get("form_type")} || Poral ID: {portal_ID}", severity="INFO" )
                        return True, order, "matched"
                    
                    #Validating entry Form Types
                    elif order.get("form_type") in Entry_form_types:
                        print(f"Form matched: {order.get("form_type")} || Poral ID: {portal_ID}")
                        logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Form matched: {order.get("form_type")} || Poral ID: {portal_ID}", severity="INFO" )
                        return True, order, "matched"
                    
                    #New form type
                    else:
                        print(f"New from type found: {order.get("form_type")}")
                        logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"New from type found: {order.get("form_type")}", severity="INFO" )
                        return False, None, "form_not_matched"
                
                else:
                    print(f"orderID {portal_ID} not matched")
                    pass
            
            if not address_found:
                logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Condition_check", remarks=f"Address Not Found from orders: {orders}", severity="INFO" )
                return False, None, "address_not_found"

        except Exception as error:
            print("Error occured while trying to find address")
            logger.log( module="Proteck-find_matching_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured: {error}", severity="INFO" )
            return False, None, "address_not_found"
        

    def lauch_browser(self,portal_order):
        '''Open the form for proteck'''

        try:
            order_link = portal_order.get('link')
            self.driver.get(order_link)
            self.driver.implicitly_wait(20)
            WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located((By.ID, "WaitIndicator")))
            view = WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1 span.product-type")))

            if view :
                return True, "Opened Form"
            else:
                logger.log( module="Proteck-lauch_browser", order_id=hybrid_orderid, action_type="Condtion_Check", remarks=f"Issue in opening form in new tab , not loaded within 40 seconds", severity="INFO" )
                return False, "Error in opening"
            
        except Exception as er: 
            logger.log( module="Proteck-lauch_browser", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception Occured on opening form in new tab: {er}", severity="INFO" )
            return False, er


    def proteck_formopen_fill(self, portal_order, session, merged_json, order_details, order_id, tfs_orderid, master_order_id):
        '''Proteck form processing controller'''

        try:
            researchpad_data_retrival_url = env.RESEARCHPAD_DATA_URL
            config_path = self.get_config(portal_order)

            #no config paths found
            if config_path is None:
                logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"No matching config path found: {config_path}", severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                return

            #get data and json file
            form_config, merged_json = load_form_config_and_data( order_id=order_id,config_path=config_path, researchpad_data_retrival_url=researchpad_data_retrival_url, session=session, merged_json=merged_json,token=hybrid_token )
            if not form_config or not merged_json:
                logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"Empty Form config: {form_config}, Empty merged_json: {merged_json}", severity="INFO" )
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                print("No details to fill ,quiting process")
                return  
            
            #Get conditions
            if self.is_inspection:
                condition_data = self.generate_inp_condition(merged_json)
            else:
                pass

            if "entry_data" in merged_json and merged_json["entry_data"]:
                merged_json["entry_data"][0]["condition_data"] = condition_data
            logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"merged_json: {merged_json}", severity="INFO" )

            #Form filling
            form_fill, error = self.fill_form_multi( merged_json, form_config)
            
            #fetch uploading  document, photo
            uplaod_data = fetch_upload_data(self, order_id)
            if not uplaod_data:
                logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid, action_type="Condition-check",  remarks=f"No upload data found for order {order_id}", severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            comparables_folder = uplaod_data.get("comparables_folder")
            tax_record = uplaod_data.get("documents")
            mls_record = uplaod_data.get("documents")
            documents = uplaod_data.get("documents", [])
            image_path = uplaod_data.get("image_path")
            
            #checking tax and mls
            if documents:
                upload_documents, err = self.upload_tax_mls(merged_json,documents)

            #checking photos
            if not image_path or not isinstance(image_path, str) or not image_path.strip():
                logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid,action_type="Condition-check", remarks=f"Subject photo folder is missing or invalid for order {order_id}: {comparables_folder!r}",severity="INFO" )

                if form_fill:
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
                else:
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            #upload photos
            upload_photos, err = self.upload_photos_to_order(image_path)
            
            #If form is filled and upload completed
            if form_fill and upload_photos:
                logger.log(  module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid, action_type="Condition-check", remarks="All form filling and upload functions completed successfully.", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
                update_pic_status(master_order_id,"Uploaded",hybrid_token)
                return
            
            #if Upload completed , mark status
            elif form_fill and not upload_photos:
                logger.log(  module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid, action_type="Condition-check", remarks="only form filling completed successfully.", severity="INFO" )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
                return
            
            #if Upload completed , mark status
            elif upload_photos and not form_fill:
                logger.log(  module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid, action_type="Condition-check", remarks="only pic uploading is completed.", severity="INFO" )
                update_pic_status(master_order_id,"Uploaded",hybrid_token)
                update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
            else:
                logger.log( module="Proteck-proteck_formopen_fill", order_id=hybrid_orderid, action_type="Condition-check", remarks=f"One or more functions failed: form_fill={form_fill}, upload_photos={upload_photos}, upload_documents={upload_documents}", severity="INFO")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                return
            
        except Exception as error:
            logger.log( module="Proteck-proteck_formopen_fill",order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception in form filling main: {error}",severity="INFO" )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return
        

    def get_config(self, portal_order):
        '''Get config paths'''

        try:
            form_type = portal_order.get('form_type')
            
            if self.is_inspection:

                #checking if bank is provider
                is_bank = self.check_bank()

                if form_type == 'PCR eValuation Exterior With Checklist' :
                    config_path = 'json/proteckjson/pcr_evaluation_exterior_with_checklist.json'
                elif form_type == 'Property Condition Report Standalone' :
                    if is_bank: config_path = "json/proteckjson/pcr_standalone.json"
                    else: config_path = "json/proteckjson/pcr_standalone_without_PUD.json"
                elif form_type == 'Property Condition Report' :
                    if is_bank: config_path = "json/proteckjson/pcr_standalone.json"
                    else: config_path = "json/proteckjson/pcr_proteck_without_PUD.json" 
                elif form_type == 'AVM and PCR' :
                   config_path = "json/proteckjson/avm_and_pcr.json"
                else:
                    logger.log( module="Proteck-get_config", order_id=hybrid_orderid, action_type="Condition-check", remarks=f"Config path not found for form {form_type}", severity="INFO")
                    config_path = None
            else:
                print("Normal entry orders")
                pass

            return config_path

        except Exception as err:
            logger.log( module="Proteck-get_config",order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception in getting config path: {err}",severity="INFO" )
            return None


    def check_bank(self):
        '''Checking if bank is client, If bank some fields are not available in form'''

        try:
            order_detail_URL = f"https://partners.protk.com/v1/case/{self.portal_order_id}"
            response = self.session.get(order_detail_URL)
            details = response.json()
            client = details['clientName']
            if client == 'TD Bank Consumer Mortgage':
                logger.log( module="Proteck-check_bank",order_id=hybrid_orderid,action_type="Condition_Check",remarks=f"service client is bank",severity="INFO" )
                return True
            else:
                logger.log( module="Proteck-check_bank",order_id=hybrid_orderid,action_type="Condition_Check",remarks=f"service client is not bank",severity="INFO" )
                return False
            
        except Exception as err: 
            logger.log( module="Proteck-check_bank",order_id=hybrid_orderid,action_type="Exception",remarks=f"Exception in checking if bank is client for inspection order: {err}",severity="INFO" )
            return False

    def generate_inp_condition(self, merged_json):
        pass


    def fill_form_multi(self, merged_json, form_config):
        '''Function to fill the form'''

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
            "select_data": select_field,
            "Textbox": data_filling_text,
            "js_execute": javascript_excecuter_filling,
            "scrape_fill":scrape_and_fill,
            "radiobutton_data":radio_btn_click,
            "checkbox_list":select_checkboxes_list,
            "repairs":fill_repairs_list
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

                    if field_type == 'click':
                        field_name, locator, locator_type = field
                        click_element(self.driver, locator, locator_type)
                        continue

                    key_expr, xpath, mode = field

                    try:
                        value = extract_value_from_expr(key_expr)

                        if value in [None, ""]: continue

                        action_func = field_actions.get(field_type)

                        if action_func: action_func(self.driver, value, xpath, mode)
                        else: print(f"Unknown field type: {field_type}")

                    except Exception as e: 
                        logger.log(module="Proteck-fill_form_multi",order_id=hybrid_orderid,  action_type="EXCEPTION",remarks=f"Exception in filling field {key_expr}: Exception :{e}", severity="INFO" )
                        print(f"Exception filling field {key_expr}: {e}")

        return True,None
        

    def upload_photos_to_order(self, subject_photos):
        '''Upload photos'''

        try:
            click_element(self.driver, "//*[@id='PhotoAndFileLink']/a", By.XPATH)
            photo_infos = self.build_photo_infos(subject_photos)
            self.clear_all_photo_slots()
            uploaded = 0   

            for photo_info in photo_infos:
                time.sleep(0.5)

                panels_before = self.driver.find_elements(By.CSS_SELECTOR, ".photoPanel")
                panel_states = []
                for panel in panels_before:
                    text = panel.text.strip()
                    panel_states.append(text)

                count_before = len(panels_before)

                base_name, _ = os.path.splitext(photo_info['name'])
                image_name = base_name
                image_path = photo_info['path']

                #Clear the slot
                drop_zone = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.photoPanel')))
                js_drop_file = """
                    var dropZone = arguments[0];
                    var fileInput = document.createElement('input');
                    fileInput.type = 'file';
                    fileInput.style.display = 'none';
                    document.body.appendChild(fileInput);

                    fileInput.onchange = function () {
                        var event = new Event('drop', { bubbles: true });
                        var dataTransfer = new DataTransfer();
                        dataTransfer.items.add(fileInput.files[0]);
                        event.dataTransfer = dataTransfer;
                        dropZone.dispatchEvent(event);
                    };

                    fileInput.click();
                """
                
                self.driver.execute_script(js_drop_file, drop_zone)

                # Upload the file
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(image_path)

                # Clear file input to avoid duplicate issues
                js_clear_file_input = """
                    var fileInput = document.querySelector('input[type="file"]');
                    if (fileInput) {
                        fileInput.value = '';
                        fileInput.remove();}"""
                self.driver.execute_script(js_clear_file_input)

                try:
                    #wait for photo panel to appear
                    WebDriverWait(self.driver, 20).until( lambda d: len(d.find_elements(By.CSS_SELECTOR, ".photoPanel")) > count_before)

                    #get latest panel
                    panels_now = self.driver.find_elements(By.CSS_SELECTOR, ".photoPanel")
                    for i, panel in enumerate(panels_now):
                        if panel.text.strip() != panel_states[i]: break
                    latest_panel = panel

                    #wait for photo to uploaded
                    WebDriverWait(latest_panel, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))

                    # Wait for dropdown near the uploaded photo
                    dropdown = latest_panel.find_element(By.TAG_NAME, "select")
                    select = Select(dropdown)
                    image_role = self.get_image_role(image_name)

                    try:
                        select.select_by_visible_text(image_role)
                        logger.log( module="Proteck-upload_photos_to_order", order_id=hybrid_orderid, action_type="Condition_Check", remarks = f"Selected description '{image_role}' for {image_name}", severity="INFO" )
                    except:
                        select.select_by_visible_text("Additional Exterior Subject Photo")
                        logger.log( module="Proteck-upload_photos_to_order", order_id=hybrid_orderid, action_type="Condition_Check", remarks = f"Option '{image_role}' disabled or missing , selected Additional Exterior Subject Photo", severity="INFO" )
                    
                    uploaded+=1

                except Exception as e: 
                    logger.log( module="Proteck-upload_photos_to_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"No dropdown found for {image_name} or could not select description: {e}", severity="INFO" )
            

            self.driver.execute_script("document.querySelector('a.save-and-close').click();")
            if uploaded>=6:
                return True, None
            else:
                return False,'not uploaded'

        except Exception as err:
            logger.log( module="Proteck-upload_photos_to_order", order_id=hybrid_orderid, action_type="Exception", remarks=f"Exception during uploading photos: {err}", severity="INFO" )
            return False, err


    def upload_tax_mls(self,merged_json,documents):
        '''Upload tax and mls if available'''
        
        try:
            tax_document = None
            mls_document = None

            for doc in documents:
                doc_type = doc.get("type", "").strip().upper()

                if doc_type == "TAX": tax_document = doc.get("path")
                elif doc_type == "MLS": mls_document = doc.get("path")

            if not tax_document and not mls_document:
                logger.log(module="Proteck-upload_tax_mls", order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Tax and mls docuement not provided: {tax_document}", severity="INFO")
                return True,None  

            entry_data = merged_json.get('entry_data', [])
            entry = entry_data[0]
            sub_data = entry.get('sub_data', None) 
            
            click_element(self.driver, "//a[@class='case-talk']", By.XPATH)

            #switch to new tab
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
            parent = self.driver.current_window_handle
            child = [h for h in self.driver.window_handles if h != parent][0]
            self.driver.switch_to.window(child)
            WebDriverWait(self.driver,15).until(EC.url_contains("CaseMessage"))
            logger.log( module="Proteck-upload_tax_mls",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Switched to new tab for uplaoding tax", severity="INFO" )

            #Addd new entry
            add_new_file = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='view']/div/p/a")))
            add_new_file.click()
            self.driver.implicitly_wait(10)

            #Main page inputs
            subject_line = self.driver.find_element(By.XPATH,"//*[@id='_addMessage__form__subjectLine']")
            Note = self.driver.find_element(By.XPATH, "//*[@id='_addMessage__form__note']")
            subject_line.send_keys(sub_data.get("subjectLine"))
            Note.send_keys(sub_data.get("note"))

            #click notify and action
            click_element(self.driver, "/html/body/form/div[3]/div/table/tbody/tr/td/fieldset/div[1]/p/input", By.XPATH)
            click_element(self.driver, "/html/body/form/div[3]/div/table/tbody/tr/td/fieldset/div[2]/p/input", By.XPATH)
            click_element(self.driver, "/html/body/form/div[3]/div/table/tbody/tr/td/div/fieldset/p/input[2]", By.XPATH)

            description = self.driver.find_element(By.XPATH,"//*[@id='_title_1']")
            description.send_keys(sub_data.get("description1"))
            attach_file = self.upload_file(tax_document,"//*[@id='_file_1']")
            logger.log( module="Proteck-upload_tax_mls",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Uploaded Tax Successfully", severity="INFO" )

            if mls_document:
                logger.log( module="Proteck-upload_tax_mls",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"MLS Found in attachment", severity="INFO" )
                click_element(self.driver, "/html/body/form/div[3]/div/table/tbody/tr/td/div/fieldset/p/input[2]", By.XPATH)
                description2 = self.driver.find_element(By.XPATH,"//*[@id='_title_2']")
                description2.send_keys(sub_data.get("description2"))
                attach_file2 = self.upload_file(mls_document,"//*[@id='_file_2']")
            
            # save_btn = WebDriverWait(self.driver, 20).until( EC.presence_of_element_located((By.XPATH, '//*[@id="_addMessage__form__insert"]')))
            # self.driver.execute_script("arguments[0].click();", save_btn)
            self.driver.switch_to.window(parent)
            
            logger.log( module="Proteck-upload_tax_mls",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Uploaded files Successfully", severity="INFO" )

            if attach_file:
                return True, None
            else:
                return False, "tax upload issue"

        except Exception as e:
            logger.log(module="Proteck-upload_tax_mls", order_id=hybrid_orderid, action_type="Exception", remarks=f"Could not Upload documents: {e}", severity="INFO")
            return False, e


    def upload_file(self, path_of_file, elementlocator, retries=2):
        '''Upload tax'''

        try:
            file_name = os.path.basename(path_of_file)
            for attempt in range(retries):

                # Wait for the element to be clickable
                element = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, elementlocator)))                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                
                # Upload the file
                element.send_keys(path_of_file)

                # Recheck upload
                uploaded_file = element.get_attribute("value")
                if uploaded_file and file_name in uploaded_file:
                    logger.log( module="Proteck-clear_all_photo_slots",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Successfully uploaded the file: {uploaded_file}", severity="INFO" )
                    return True
                else:
                    logging.warning(f"Recheck failed for file upload, retrying... ({attempt + 1}/{retries})")
            logger.log( module="Proteck-clear_all_photo_slots",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"File upload failed after {retries} retries", severity="INFO" )
            return False

        except Exception as error:
            logger.log( module="Proteck-clear_all_photo_slots",order_id=hybrid_orderid, action_type="Condition_Check", remarks=f"Exception on file Upload section in controller: {error}", severity="INFO" )
            return False


    def clear_all_photo_slots(self):
        '''Clear all photos'''

        try:
            wait = WebDriverWait(self.driver, 5)

            while True:
                try:
                    delete_icons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.deletePhoto.iconRow')))

                    if not delete_icons:
                        break

                    delete_icons[0].click()
                    alert = wait.until(EC.alert_is_present())
                    alert.accept()

                    # Wait until the DOM updates (icon disappears)
                    wait.until(EC.staleness_of(delete_icons[0]))
                    logger.log( module="Proteck-clear_all_photo_slots",order_id=hybrid_orderid, action_type="Condition_Check", remarks="Deleted one photo slot", severity="INFO" )

                except TimeoutException:
                    break

                except StaleElementReferenceException:
                    continue

            logger.log( module="Proteck-clear_all_photo_slots",order_id=hybrid_orderid, action_type="Condition_Check",remarks="Cleared all existing photos before uploading new ones",severity="INFO" )

        except Exception as e:
            logger.log( module="Proteck-clear_all_photo_slots", order_id=hybrid_orderid, action_type="Exception", remarks=f"Could not clear existing photos: {e}",severity="ERROR" )


    def build_photo_infos(self,folder_path):
        '''Build paths for each photo'''

        photo_infos = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                photo_infos.append({  "name": os.path.splitext(file)[0],"path": os.path.join(folder_path, file)  })
        return photo_infos
    

    def get_image_role(self, image_name):
        '''Function to get image role'''

        try:
            base_name = image_name.split('.')[0].lower().replace("_", " ")
            mappings = {"subject street scene facing other direction": "Subject Street Scene Facing Other Direction","subject photo of front": "Subject Photo of Front", "subject street scene": "Subject Street Scene","subject photo of side": "Subject Photo of Side", "subject address verification photo": "Subject Address Verification Photo","left side":"Subject Photo of Side","right side":"Subject Photo of Side"}

            # Match against keys
            for key, dropdown_text in mappings.items():
                if key in base_name: return dropdown_text
            return "Additional Exterior Subject Photo"

        except Exception as error:
            logger.log( module="Proteck-get_image_role", order_id=hybrid_orderid, action_type="Exception", remarks= f"Exception occured on geting image role {error}", severity="INFO" )
            return "Additional Exterior Subject Photo"


