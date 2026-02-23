import importlib
import logging
from utils.glogger import GLogger
import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse

from screens.loaded_screen import LoadedScreen
from utils.helper import get_order_address_from_assigned_order, params_check, update_order_status
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading
from integrations import hybrid_bpo_api
from screens import portal_login_screen
process_type, hybrid_orderid, hybrid_token = params_check()
logger = GLogger()
class EntryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = hybrid_bpo_api.HybridBPOApi()

        # Initialize Frame Container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.stop_event = threading.Event()  # Event to stop processing thread
        # Create LoadedScreen Instance
        title_text = "Starting Hybrid Entry..."
        status_text = "Entry started"
        # self.loaded_screen = LoadedScreen(self.container, self, title_text, status_text)
        # self.loaded_screen.pack(fill="both", expand=True)

        self.loaded_screen = LoadedScreen(
            self.container,
            self,
            title_text,
            status_text,
            on_exit_callback=self.exit_entry_screen  # Pass callback
        )
        self.loaded_screen.pack(fill="both", expand=True)

        # Determine which process to run based on parameters
        #process_type, hybrid_orderid = params_check()
        #process_type="SmartEntry"
        #process_type="PortalLogin"
        #process_type="AutoLogin"
        self.handle_argument(process_type, hybrid_orderid, hybrid_token)


    def handle_argument(self, process_type, hybrid_orderid, hybrid_token):
        process_type = process_type or ""
        hybrid_orderid = hybrid_orderid or ""
        hybrid_token = hybrid_token or ""
        if 'SmartEntry' in process_type:
            # Run the process in a thread to keep GUI responsive
            threading.Thread(target=self.run_smart_entry_process, args=(hybrid_orderid,), daemon=True).start()
        else:
            self.loaded_screen.update_status(
                title="Orders not found",
                status="No SmartEntry tag detected."
            )

    def run_smart_entry_process(self, hybrid_orderid):
        try:
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Initiated", hybrid_token)
            self.loaded_screen.update_status(
                title="Parsing Order Data...",
                status="Fetching required details..."
            )

            self.check_if_any_argument_passed(hybrid_orderid)

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
            import traceback
            logger.log(
                module="EntryScreen-run_smart_entry_process",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"SmartEntry process failed: {traceback.format_exc()}",
                severity="ERROR"
            )

    def check_if_any_argument_passed(self, order_id):
        try:
            if not vpn_checking():
                self.loaded_screen.update_status(
                    title="VPN Error",
                    status="VPN Not Connected... Please connect and retry"
                )
                return

            # Retrieve order details
            orders = hybrid_bpo_api.HybridBPOApi.get_entry_order(hybrid_orderid)
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
                account_id=None
                portal_key=order.get("portal_key", None)
                #order_details = get_order_address_from_assigned_order(order_id,arg3)

                if not portal_name:
                    logger.log(
                        module="EntryScreen-check_if_any_argument_passed",
                        order_id=hybrid_orderid,
                        action_type="Warning",
                        remarks="Portal name missing in order data.",
                        severity="WARNING"
                    )
                    continue

                logger.log(
                    module="EntryScreen-check_if_any_argument_passed",
                    order_id=hybrid_orderid,
                    action_type="Info",
                    remarks=f"Logging into portal: {portal_name}",
                    severity="INFO"
                )
                print("Entry")
                portal_login_screen.PortalLoginScreen.login_to_portals(
                    self, username, password, portal_url,
                    portal_name, proxy, session,account_id,portal_key
                )

        except Exception as e:
            import traceback
            logger.log(
                module="EntryScreen-check_if_any_argument_passed",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Error in check_if_any_argument_passed: {traceback.format_exc()}",
                severity="ERROR"
            )
            self.loaded_screen.update_status(
                title="Error",
                status=f"Order processing failed: {str(e)}"
            )


    def exit_entry_screen(self):
        self.stop_event.set()
        self.destroy()
        try:
            self.controller.quit()
            self.controller.destroy()
        except Exception as e:
            logger.log(
                module="EntryScreen-exit_entry_screen",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Error closing application: {e}",
                severity="ERROR"
            )
        sys.exit(0)