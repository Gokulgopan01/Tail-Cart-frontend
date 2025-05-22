import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading
from urllib.parse import urlparse, parse_qs


class MlsScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()

        label = ttk.Label(self, text="Downloading Comparable PIC and PDF....", font=("Arial", 17))
        label.pack(pady=20)

        progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")
        progress.pack(pady=10)
        progress.start()
         # Get command line arguments 

        if len(sys.argv) < 2:
            print("Insufficient arguments provided.")
            return
        url = sys.argv[1]  # Example: 'myapp://?arg1=mlsdownloader&arg2=order123'
        parsed_url = urlparse(url)
        args = parse_qs(parsed_url.query)
        arg1 = args.get('arg1', [None])[0]  # Get 'arg1' or None if not present
        arg2 = args.get('arg2', [None])[0]  # Get 'arg2' or None if not present  

        # if(arg1=='mlsdownloader'):
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
                        init.process_mls_actions(order_data)
                        for widget in self.winfo_children():
                            widget.destroy() 
                        label = ttk.Label(self, text="Downloading Comparable PIC and PDF Completed", font=("Arial", 18))
                        label.pack(pady=20) 
                             
                    else:
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



