import importlib
import logging
import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse
from integrations.hybrid_bpo_api import HybridBPOApi
from screens.loaded_screen import LoadedScreen
from utils.helper import get_order_address_from_assigned_order, params_check
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading
from integrations import hybrid_bpo_api
from screens import portal_login_screen
arg1, arg2 = params_check()
class EntryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()

        # Initialize Frame Container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Create LoadedScreen Instance
        title_text = "Starting Hybrid Entry..."
        status_text = "Entry started"
        self.loaded_screen = LoadedScreen(self.container, self, title_text, status_text)
        self.loaded_screen.pack(fill="both", expand=True)

        # Determine which process to run based on parameters
        #arg1, arg2 = params_check()
        #arg1="SmartEntry"
        #arg1="PortalLogin"
        #arg1="login"
        self.handle_argument(arg1, arg2)

    def handle_argument(self, arg1, arg2):
        arg1 = arg1 or ""
        arg2 = arg2 or ""
        if 'SmartEntry' in arg1:
            # Run the process in a thread to keep GUI responsive
            threading.Thread(target=self.run_smart_entry_process, args=(arg2,), daemon=True).start()
        else:
            self.loaded_screen.update_status(
                title="Orders not found",
                status="No SmartEntry tag detected."
            )

    def run_smart_entry_process(self, arg2):
        try:
            self.loaded_screen.update_status(
                title="Parsing Order Data...",
                status="Fetching required details..."
            )

            self.check_if_any_argument_passed(arg2)

            self.loaded_screen.update_status(
                title="Validating Data...",
                status="Checking order integrity..."
            )

            # Optional: Add validation logic here if needed
            # self.validate_data()

            self.loaded_screen.update_status(
                title="Completed",
                status="Hybrid Entry Processing Finished."
            )

        except Exception as e:
            self.loaded_screen.update_status(
                title="Error",
                status=f"Something went wrong: {str(e)}"
            )
            logging.error("SmartEntry process failed", exc_info=True)

    def check_if_any_argument_passed(self, order_id):
        try:
            if not vpn_checking():
                self.loaded_screen.update_status(
                    title="VPN Error",
                    status="VPN Not Connected... Please connect and retry"
                )
                return

            # Retrieve order details
            orders = HybridBPOApi.get_entry_order(arg2)
            if not orders:
                self.loaded_screen.update_status(
                    title="No Orders",
                    status="No orders found to process."
                )
                return
            


            # Process each order
            for order in orders:
                portal_name = order.get("portal_name", "")
                username = order.get("username", "")
                password = order.get("password", "")
                portal_url = order.get("portal_url", "")
                proxy = order.get("proxy", None)
                session = order.get("session", None)
                order_id = order.get("order_id", "")
                order_details = get_order_address_from_assigned_order(order_id)

                if not portal_name:
                    logging.warning("Portal name missing in order data.")
                    continue

                logging.info(f"Logging into portal: {portal_name}")
                portal_login_screen.PortalLoginScreen.login_to_portal(
                    self, username, password, portal_url,
                    portal_name, proxy, session
                )

        except Exception as e:
            logging.error("Error in check_if_any_argument_passed", exc_info=True)
            self.loaded_screen.update_status(
                title="Error",
                status=f"Order processing failed: {str(e)}"
            )
