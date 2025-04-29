import logging
import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse
from check_and_form_open.redbell_check_and_form_open import  redbell_formopen_fill
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from portal.RedBell_Entry import RedBellEntry
from screens.loaded_screen import LoadedScreen
from utils.helper import get_order_address_from_assigned_order, params_check
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading
from integrations import hybrid_bpo_api
from screens import portal_login_screen
from check_and_form_open.proteck_check_and_form_open import proteck_formopen_fill

class EntryScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()
        # Initialize Frame Container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        title_text="Starting Hybrid Entry..."
        status_text="Entry started"
        # Create LoadedScreen Instance
        self.loaded_screen = LoadedScreen(self.container, self, title_text, status_text)
        self.loaded_screen.pack(fill="both", expand=True)
        

        # Simulating Updates from Another Script
        # login screen  
        arg1,arg2= params_check()    
        arg1="SmartEntry"
        self.handle_argument(arg1, arg2)
        # # if(arg1=='mlsdownloader'):
        # if('SmartEntry' in arg1):
        #     threading.Thread(target=self.check_if_any_argument_passed, args=(arg2,), daemon=True).start()
        #     self.after(2000, lambda: self.loaded_screen.update_status(title="Parsing Order Data...", status="Fetching required details..."))
        # else:
        #      print("Orders not found") 
        #      self.after(2000, lambda: self.loaded_screen.update_status(title="Orders not found", status="Fetching required details..."))
    
        # self.after(4000, lambda: self.loaded_screen.update_status(title="Validating Data...", status="Checking order integrity..."))
        # self.after(6000, lambda: self.loaded_screen.update_status(title="Completed", status="Hybrid Entry Processing Finished."))

    def run_smart_entry_process(self, arg2):
        def process():
            try:
                # Step 1: Update UI - Start Parsing
                self.loaded_screen.update_status(
                    title="Parsing Order Data...",
                    status="Fetching required details..."
                )

                # Step 2: Parse & fetch required data
                self.check_if_any_argument_passed(arg2)

                # Step 3: Update UI - Validating
                self.loaded_screen.update_status(
                    title="Validating Data...",
                    status="Checking order integrity..."
                )

                # Optional: If you have validation logic, call it here
                # self.validate_data()

                # Step 4: Update UI - Completed
                self.loaded_screen.update_status(
                    title="Completed",
                    status="Hybrid Entry Processing Finished."
                )

            except Exception as e:
                self.loaded_screen.update_status(
                    title="Error",
                    status=f"Something went wrong: {str(e)}"
                )
                logging.error(f"SmartEntry process failed: {e}")

    #     # Run in background thread to avoid freezing GUI
    #     threading.Thread(target=process, daemon=True).start()


    def handle_argument(self, arg1, arg2):
        if 'SmartEntry' in arg1:
            self.run_smart_entry_process(arg2)
        else:
            self.loaded_screen.update_status(
                title="Orders not found",
                status="No SmartEntry tag detected."
            )


    def check_if_any_argument_passed(self, orderId):
            
            try:
                is_vpn_connected = vpn_checking()
                if is_vpn_connected:
                     # Retrieve order details
                    orders = HybridBPOApi.get_entry_order() 
                    if not orders:  # Check if the order list is empty
                        print("No orders found.")
                        return
                    
                    # Process each order
                    for order in orders:
                        portal_name = order.get("portal_name", "")
                        username = order.get("username", "")
                        password = order.get("password", "")
                        portal_url = order.get("portal_url", "")
                        proxy = order.get("proxy", None)  # Optional proxy
                        session=order.get("session",None)
                        order_id=order.get("order_id","")
                        order_details=get_order_address_from_assigned_order(order_id)
                        if portal_name:
                            if portal_name=="RedBell":
                                print(f"Logging into portal: {portal_name}")
                               # Create an instance of RedBellEntry
                                orders, session,driver = RedBellEntry(self,username, password, portal_url, portal_name, proxy, session)
                               
                                redbell_formopen_fill(orders, driver,session, merged_json=None, order_details=order_details,order_id=order_id)
                            else:     
                                print(f"Logging into portal: {portal_name}")
                                orders,session,driver=portal_login_screen.PortalLoginScreen.login_to_portal(self,username, password, portal_url, portal_name, proxy,session)  
                                # # Dynamically call the corresponding form open function
                                form_open_func_name = f"{portal_name.lower()}_formopen_fill"
                                print(form_open_func_name)
                                form_open_func = globals().get(form_open_func_name)

                                if callable(form_open_func):
                                    form_open_func(orders, driver,session, merged_json=None, order_details=order_details,order_id=order_id)
                                else:
                                    logging.error(f"No function defined for portal: {form_open_func_name}")
                        else:
                            print("Portal name missing in order data.")
                                

                else:
                    print('VPN not connected')
                    for widget in self.winfo_children():
                            widget.destroy() 
                    label = ttk.Label(self, text="VPN Not Connected... Please connect and retry", font=("Arial", 18))
                    label.pack(pady=20)
            except Exception as e:
                print(f"Error in the program: {e}")