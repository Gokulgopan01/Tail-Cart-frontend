import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys


class MlsScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()
        args = sys.argv[1:]  # Get command line arguments
        if len(args) < 1:
            print("Insufficient arguments provided.")
            return
        args1 = sys.argv[1] 
        arg2 = sys.argv[2] 
        print(f"Arguments passed: {args}")
        print(f"Second argument passed: {arg2}")   

        if(args1=='mlsdownloader'):
            self.check_if_any_argument_passed(arg2)
        else:
             print("Orders not found")    


        # ttk.Button(self, text="MLS_Process_Start",command=lambda:self.check_if_any_argument_passed(1010)).pack(pady=10)
        ttk.Label(self, text="MLS Automation", style="Title.TLabel")

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
                        # init=GaMls()

                        init=mls_data[mls_type]()
                        init.process_mls_actions(order_data)              
                    else:
                        print("No order data found for the given orderId.")
                        # Handle the case where no order data is found
                else:
                    print('VPN not connected')
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



