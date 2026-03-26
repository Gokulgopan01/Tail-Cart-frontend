
# import tkinter as tk
# import threading
# import logging
# from integrations.hybrid_bpo_api import HybridBPOApi
# from utils.helper import get_order_address_from_assigned_order, params_check
# from utils.vpn_connection import vpn_checking
# from screens import portal_login_screen

# arg1, arg2,arg3 = params_check()

# class PortalInstructionScreen(tk.Frame):
#     def __init__(self, parent, controller):
#         super().__init__(parent)
#         self.controller = controller
#         self.hybridIntegration = HybridBPOApi()
#         #arg1="SmartEntry"
#         #arg1="PortalLogin"
#         #arg1="auto"
#         if "PortalLogin" in arg1:
#             # Title label - centered
#             self.title_label = tk.Label(
#                 self,
#                 font=("Arial", 16, "bold"),
#                 anchor='center',
#                 justify='center'
#             )
#             self.title_label.pack(fill='x', padx=20, pady=(20, 5))

#             # Message label - centered, wrapped
#             self.message_label = tk.Label(
#                 self,
#                 font=("Arial", 14),
#                 anchor='center',
#                 justify='center',
#                 wraplength=600
#             )
#             self.message_label.pack(fill='x', padx=20, pady=(0, 20))

#             # Start background thread after UI renders
#             self.after(100, self.start_background_thread)

#     def start_background_thread(self):
#         threading.Thread(target=self.check_if_any_argument_passed, daemon=True).start()

#     def update_status(self, title, message):
#         """Thread-safe update of UI labels."""
#         def _update():
#             self.title_label.config(text=title)
#             self.message_label.config(text=message)
#             logging.info(f"{title} - {message}")
#         self.after(0, _update)

#     def check_if_any_argument_passed(self):
#         """Main processing function: VPN check, fetch order, portal login."""
#         try:
#             self.update_status("VPN Check", "Validating VPN connection...")
#             if not vpn_checking():
#                 self.update_status("VPN Error", "VPN Not Connected... Please connect and retry.")
#                 return

#             self.update_status("Order Check", "Fetching order details...")
#             #arg2 = 110  # (Optional: test override)
#             #arg2=110
#             orders = HybridBPOApi.get_entry_order(arg2)

#             if not orders:
#                 self.update_status("No Orders", "No orders found to process.")
#                 return

#             # Process only the first order to prevent duplicate logins
#             order = orders[0]
#             portal_name = order.get("portal_name", "")
#             username = order.get("username", "")
#             password = order.get("password", "")
#             portal_url = order.get("portal_url", "")
#             proxy = order.get("proxy", None)
#             session = order.get("session", None)
#             order_id = order.get("order_id", "")

#             self.update_status("Fetching Order Address", f"Order ID: {order_id}")
#             if not portal_name:
#                 logging.warning("Portal name missing in order data.")
#                 return

#             logging.info(f"Logging into portal: {portal_name}")
#             self.update_status("Logging In", f"Portal: {portal_name} for user {username}")
#             portal_login_screen.PortalLoginScreen.login_to_portal(
#                 self, username, password, portal_url, portal_name, proxy, session
#             )
#             self.update_status("Success", f"Successfully logged into {portal_name}")

#         except Exception as e:
#             logging.error("Portal login process failed.", exc_info=True)
#             self.update_status("Error", f"Order processing failed: {str(e)}")




# import tkinter as tk
# import threading
# import logging
# import sys

# from integrations.hybrid_bpo_api import HybridBPOApi
# from utils.helper import get_order_address_from_assigned_order, params_check
# from utils.vpn_connection import vpn_checking
# from screens import portal_login_screen

# arg1, arg2, arg3 = params_check()

# class PortalInstructionScreen(tk.Frame):
#     def __init__(self, parent, controller):
#         super().__init__(parent)
#         self.controller = controller
#         self.hybridIntegration = HybridBPOApi()

#         if "PortalLogin" in arg1:
#             self.title_label = tk.Label(
#                 self, font=("Arial", 16, "bold"),
#                 anchor='center', justify='center'
#             )
#             self.title_label.pack(fill='x', padx=20, pady=(20, 5))

#             self.message_label = tk.Label(
#                 self, font=("Arial", 14),
#                 anchor='center', justify='center', wraplength=600
#             )
#             self.message_label.pack(fill='x', padx=20, pady=(0, 10))

#             # Exit button
#             self.exit_button = tk.Button(
#                 self, text="Exit", font=("Arial", 12),
#                 command=self.exit_application, bg='red', fg='white'
#             )
#             self.exit_button.pack(pady=(10, 20))

#             self.after(100, self.start_background_thread)

#     def exit_application(self):
#         """Exit the app cleanly."""
#         logging.info("Exit requested. Closing application.")
#         self.controller.destroy()
#         sys.exit(0)  # ensure Python process also exits if frozen

#     def start_background_thread(self):
#         threading.Thread(target=self.check_if_any_argument_passed, daemon=True).start()

#     def update_status(self, title, message):
#         def _update():
#             self.title_label.config(text=title)
#             self.message_label.config(text=message)
#             logging.info(f"{title} - {message}")
#         self.after(0, _update)

#     def check_if_any_argument_passed(self):
#         try:
#             self.update_status("VPN Check", "Validating VPN connection...")
#             if not vpn_checking():
#                 self.update_status("VPN Error", "VPN Not Connected... Please connect and retry.")
#                 return

#             self.update_status("Order Check", "Fetching order details...")
#             orders = HybridBPOApi.get_entry_order(arg2)

#             if not orders:
#                 self.update_status("No Orders", "No orders found to process.")
#                 return

#             order = orders[0]
#             portal_name = order.get("portal_name", "")
#             username = order.get("username", "")
#             password = order.get("password", "")
#             portal_url = order.get("portal_url", "")
#             proxy = order.get("proxy", None)
#             session = order.get("session", None)
#             order_id = order.get("order_id", "")

#             self.update_status("Fetching Order Address", f"Order ID: {order_id}")
#             if not portal_name:
#                 logging.warning("Portal name missing in order data.")
#                 return

#             logging.info(f"Logging into portal: {portal_name}")
#             self.update_status("Logging In", f"Portal: {portal_name} for user {username}")
#             portal_login_screen.PortalLoginScreen.login_to_portal(
#                 self, username, password, portal_url, portal_name, proxy, session
#             )
#             self.update_status("Success", f"Successfully logged into {portal_name}")

#         except Exception as e:
#             logging.error("Portal login process failed.", exc_info=True)
#             self.update_status("Error", f"Order processing failed: {str(e)}")

import tkinter as tk
import threading
import logging
from utils.glogger import GLogger
import sys

from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import get_order_address_from_assigned_order, params_check, update_order_status
from utils.vpn_connection import vpn_checking
from screens.portal_login_screen import PortalLoginScreen
from screens.loaded_screen import LoadedScreen

process_type, hybrid_orderid, hybrid_token = params_check()
logger = GLogger()

class PortalInstructionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        #process_type="SmartEntry"
        #process_type="PortalLogin"
        #process_type="AutoLogin"
        if "PortalLogin" in process_type:
            # Initialize LoadedScreen immediately
            title_text = "Portal Login In Progress..."
            status_text = "Preparing login instructions."
            self.loaded_screen = LoadedScreen(
                self.container,
                self,
                title_text,
                status_text,
                on_exit_callback=self.exit_portalinstruction_screen
            )
            self.loaded_screen.pack(expand=True, fill="both")

            # Start background processing
            self.after(100, self.start_background_thread)

    def exit_portalinstruction_screen(self):
        """Cleanly exit the entry screen and application."""
        logger.log(
            module="PortalInstructionScreen-exit_portalinstruction_screen",
            order_id=hybrid_orderid,
            action_type="Info",
            remarks="Exit requested from LoadedScreen. Closing application.",
            severity="INFO"
        )
        self.controller.destroy()
        sys.exit(0)

    def start_background_thread(self):
        threading.Thread(target=self.check_and_process_order, daemon=True).start()

    def update_loaded_screen(self, title, message):
        self.loaded_screen.update_status(title, message)
        logger.log(
            module="PortalInstructionScreen-update_loaded_screen",
            order_id=hybrid_orderid,
            action_type="Info",
            remarks=f"{title} - {message}",
            severity="INFO"
        )

    def check_and_process_order(self):
        try:
            #update_order_status(hybrid_orderid, "In Progress", "View Portal Instructions", "Initiated", hybrid_token)
            self.update_loaded_screen("VPN Check", "Validating VPN connection...")
            if not vpn_checking():
                self.update_loaded_screen("VPN Error", "VPN not connected. Please connect and retry.")
                return

            self.update_loaded_screen("Order Check", "Fetching order details...")
            orders = HybridBPOApi.get_entry_order(hybrid_orderid)

            if not orders:
                self.update_loaded_screen("No Orders", "No orders found to process.")
                return

            order = orders[0]
            portal_name = order.get("portal_name", "")
            username = order.get("username", "")
            password = order.get("password", "")
            portal_url = order.get("portal_url", "")
            proxy = order.get("proxy")
            session = order.get("session")
            order_id = order.get("order_id", "")
            account_id=None
            portal_key=order.get("portal_key", None)
            

            self.update_loaded_screen("Order ID", f"Order ID: {order_id}")

            if not portal_name:
                logger.log(
                    module="PortalInstructionScreen-check_and_process_order",
                    order_id=hybrid_orderid,
                    action_type="Warning",
                    remarks="Portal name missing in order data.",
                    severity="WARNING"
                )
                self.update_loaded_screen("Error", "Missing portal name in order.")
                return

            self.update_loaded_screen("Logging In", f"Logging into {portal_name}...")
            PortalLoginScreen.login_to_portals(
                self,
                username,
                password,
                portal_url,
                portal_name,
                proxy,
                session,account_id,portal_key
            )
            self.update_loaded_screen("Success", f"Successfully logged into {portal_name}")

        except Exception as e:
            import traceback
            logger.log(
                module="PortalInstructionScreen-check_and_process_order",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Portal login process failed: {traceback.format_exc()}",
                severity="ERROR"
            )
            self.update_loaded_screen("Error", f"Login failed: {str(e)}")
