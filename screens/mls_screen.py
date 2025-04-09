import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading
from urllib.parse import urlparse, parse_qs
from utils.helper import params_check
from screens.loaded_screen import LoadedScreen

class MlsScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        title_text="Starting Hybrid Comp_PIC_PDF Download..."
        status_text="Downloading started"
        # Create LoadedScreen Instance
        self.loaded_screen = LoadedScreen(self.container, self, title_text, status_text)
        self.loaded_screen.pack(fill="both", expand=True)

        if len(sys.argv) < 2:
            print("Insufficient arguments provided.")
            return
        
        arg1,arg2= params_check() # Get 'arg2' or None if not present  
        if('mlsdownloader' in arg1):
            threading.Thread(target=self.check_if_any_argument_passed, args=(arg2,), daemon=True).start()
        else:
             print("Orders not found") 


    def check_if_any_argument_passed(self, orderId):
            
            try:
                is_vpn_connected = vpn_checking()
                if is_vpn_connected:

                    mls_data={'GAMLS':Gamls,'FMLS':Fmls}
                    order_data=self.hybridIntegration.get_order(orderId)
                    print(order_data["MLS"])
                    mls_type = order_data["MLS"]
                    if mls_type in mls_data:
                        # If order data is found, proceed with the login
                        init=mls_data[mls_type]()
                        final_output=init.process_mls_actions(order_data)
                        final_output
                        self.after(2000, lambda: self.loaded_screen.update_status(title="Downloading Comparable PIC and PDF Completed", status=f"{final_output} download failed", loading='Clear'))                    
                    else:
                        print("No order data found for the given orderId.")
                        # Handle the case where no order data is found

                else:
                    print('VPN not connected')
                    self.after(2000, lambda: self.loaded_screen.update_status(title="VPN Not Connected... Please connect and retry", status="Download Failed",loading='Clear'))
            except Exception as e:
                print(f"Error in the program: {e}")


        # check if autologin version is correct
        # ttk.Button(self, text="Login",command=self.check_if_any_argument_passed(1010)).pack(pady=10)


    #     version_check = self.check_if_version()

    #     if not version_check:

    #         self.download_new_version()

    #     else:

    #         self.check_if_already_loggedIn()



    # def check_if_already_loggedIn():

    #     # check if the user is already logged in also, check if the user login expired by date
    #     1

    
    # def check_if_version(self):

    #     try:
    #         self.hybridIntegration.check_application_version() 
    #     except Exception as e:
    #         print("e")
                 

    # def download_new_version(self):
    #     try:
    #         1
    #     except Exception as e:
    #         print("e")



