import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse
from check_and_form_open.redbell_check_and_form_open import formopen_fill
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

        # if(arg1=='mlsdownloader'):
        if('SmartEntry' in arg1):
            threading.Thread(target=self.check_if_any_argument_passed, args=(arg2,), daemon=True).start()
            self.after(2000, lambda: self.loaded_screen.update_status(title="Parsing Order Data...", status="Fetching required details..."))
        else:
             print("Orders not found") 
             self.after(2000, lambda: self.loaded_screen.update_status(title="Orders not found", status="Fetching required details..."))
    
        self.after(4000, lambda: self.loaded_screen.update_status(title="Validating Data...", status="Checking order integrity..."))
        self.after(6000, lambda: self.loaded_screen.update_status(title="Completed", status="Hybrid Entry Processing Finished."))





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
                                orders, session = RedBellEntry(self,username, password, portal_url, portal_name, proxy, session)
                               
                                formopen_fill(orders, session, merged_json=None, order_details=order_details,order_id=order_id)
                            else:     
                                print(f"Logging into portal: {portal_name}")
                                portal_login_screen.PortalLoginScreen.login_to_portal(self,username, password, portal_url, portal_name, proxy)
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