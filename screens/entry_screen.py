import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from screens.loaded_screen import LoadedScreen
from utils.helper import params_check
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading


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

                    # mls_data={'GAMLS':Gamls,'FMLS':Fmls}
                    # order_data=self.hybridIntegration.get_order(orderId)
                    # print(order_data["MLS"])
                    # mls_type = order_data["MLS"]
                    # if mls_type in mls_data:
                    #     # If order data is found, proceed with the login
                    #     init=mls_data[mls_type]()
                    #     init.process_mls_actions(order_data)
                    #     for widget in self.winfo_children():
                    #         widget.destroy() 
                    #     label = ttk.Label(self, text="Downloading Comparable PIC and PDF Completed", font=("Arial", 18))
                    #     label.pack(pady=20) 
                             
                    # else:
                        print("No order data found for the given orderId.")
                        # Handle the case where no order data is found

                else:
                    print('VPN not connected')
                    for widget in self.winfo_children():
                            widget.destroy() 
                    label = ttk.Label(self, text="VPN Not Connected... Please connect and retry", font=("Arial", 18))
                    label.pack(pady=20)
            except Exception as e:
                print(f"Error in the program: {e}")