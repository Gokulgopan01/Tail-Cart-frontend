# import tkinter as tk
# import threading
# import logging
# from integrations.hybrid_bpo_api import HybridBPOApi
# from utils.helper import get_order_address_from_assigned_order, params_check
# from utils.pic_pdf_downloads.vpn_connection import vpn_checking
# from screens import portal_login_screen

# arg1, arg2 = params_check()

# class PortalInstructionScreen(tk.Frame):
#     def __init__(self, parent, controller):
#         super().__init__(parent)
#         self.controller = controller
#         self.hybridIntegration = HybridBPOApi()

#         # Title label - bold and larger font, left aligned
#         self.title_label = tk.Label(self, font=("Arial", 16, "bold"), anchor='w')
#         self.title_label.pack(fill='x', padx=20, pady=(20, 5))

#         # Message label - normal font, multiline, wrap text, left aligned
#         self.message_label = tk.Label(self, font=("Arial", 14), anchor='w', justify='left', wraplength=600)
#         self.message_label.pack(fill='x', padx=20, pady=(0, 20))

#         # Start background thread for the main processing so UI remains responsive
#         threading.Thread(target=self.check_if_any_argument_passed, daemon=True).start()

#     def update_status(self, title, message):
#         """Thread-safe update of UI labels."""
#         def _update():
#             self.title_label.config(text=title)
#             self.message_label.config(text=message)
#             logging.info(f"{title} - {message}")

#         # Schedule the UI update on the main thread
#         self.after(0, _update)

#     def login_portal_thread(self, username, password, portal_url, portal_name, proxy, session):
#         """Perform portal login and update UI status accordingly."""
#         try:
#             self.update_status("Logging In", f"Portal: {portal_name} for user {username}")
#             # Call the portal login method (assumed blocking call)
#             portal_login_screen.PortalLoginScreen.login_to_portal(
#                 self, username, password, portal_url, portal_name, proxy, session
#             )
#             self.update_status("Success", f"Successfully logged into {portal_name}")
#         except Exception as e:
#             logging.error(f"Login failed for {portal_name}: {e}", exc_info=True)
#             self.update_status("Login Failed", f"Failed to login to {portal_name}: {str(e)}")

#     def check_if_any_argument_passed(self):
#         """Main processing function, validates VPN, fetches orders, and initiates portal logins."""
#         try:
#             self.update_status("VPN Check", "Validating VPN connection...")
#             if not vpn_checking():
#                 self.update_status("VPN Error", "VPN Not Connected... Please connect and retry")
#                 return

#             self.update_status("Order Check", "Fetching order details...")
#             arg2=109
#             orders = HybridBPOApi.get_entry_order(arg2)

#             if not orders:
#                 self.update_status("No Orders", "No orders found to process.")
#                 return

#             # Process each order: login portals concurrently
#             for order in orders:
#                 portal_name = order.get("portal_name", "")
#                 username = order.get("username", "")
#                 password = order.get("password", "")
#                 portal_url = order.get("portal_url", "")
#                 proxy = order.get("proxy", None)
#                 session = order.get("session", None)
#                 order_id = order.get("order_id", "")

#                 self.update_status("Fetching Order Address", f"Order ID: {order_id}")
#                 if not portal_name:
#                     logging.warning("Portal name missing in order data.")
#                     continue

#                 logging.info(f"Logging into portal: {portal_name}")
#                 portal_login_screen.PortalLoginScreen.login_to_portal(
#                     self, username, password, portal_url,
#                     portal_name, proxy, session
#                 )


#         except Exception as e:
#             logging.error("Portal login process failed.", exc_info=True)
#             self.update_status("Error", f"Order processing failed: {str(e)}")

##############################################################################
import tkinter as tk
import threading
import logging
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import get_order_address_from_assigned_order, params_check
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
from screens import portal_login_screen

arg1, arg2 = params_check()

class PortalInstructionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()
        #arg1="SmartEntry"
        #arg1="PortalLogin"
        if "PortalLogin" in arg1:
            # Title label - centered
            self.title_label = tk.Label(
                self,
                font=("Arial", 16, "bold"),
                anchor='center',
                justify='center'
            )
            self.title_label.pack(fill='x', padx=20, pady=(20, 5))

            # Message label - centered, wrapped
            self.message_label = tk.Label(
                self,
                font=("Arial", 14),
                anchor='center',
                justify='center',
                wraplength=600
            )
            self.message_label.pack(fill='x', padx=20, pady=(0, 20))

            # Start background thread after UI renders
            self.after(100, self.start_background_thread)

    def start_background_thread(self):
        threading.Thread(target=self.check_if_any_argument_passed, daemon=True).start()

    def update_status(self, title, message):
        """Thread-safe update of UI labels."""
        def _update():
            self.title_label.config(text=title)
            self.message_label.config(text=message)
            logging.info(f"{title} - {message}")
        self.after(0, _update)

    def check_if_any_argument_passed(self):
        """Main processing function: VPN check, fetch order, portal login."""
        try:
            self.update_status("VPN Check", "Validating VPN connection...")
            if not vpn_checking():
                self.update_status("VPN Error", "VPN Not Connected... Please connect and retry.")
                return

            self.update_status("Order Check", "Fetching order details...")
            #arg2 = 110  # (Optional: test override)
            #arg2=110
            orders = HybridBPOApi.get_entry_order(arg2)

            if not orders:
                self.update_status("No Orders", "No orders found to process.")
                return

            # Process only the first order to prevent duplicate logins
            order = orders[0]
            portal_name = order.get("portal_name", "")
            username = order.get("username", "")
            password = order.get("password", "")
            portal_url = order.get("portal_url", "")
            proxy = order.get("proxy", None)
            session = order.get("session", None)
            order_id = order.get("order_id", "")

            self.update_status("Fetching Order Address", f"Order ID: {order_id}")
            if not portal_name:
                logging.warning("Portal name missing in order data.")
                return

            logging.info(f"Logging into portal: {portal_name}")
            self.update_status("Logging In", f"Portal: {portal_name} for user {username}")
            portal_login_screen.PortalLoginScreen.login_to_portal(
                self, username, password, portal_url, portal_name, proxy, session
            )
            self.update_status("Success", f"Successfully logged into {portal_name}")

        except Exception as e:
            logging.error("Portal login process failed.", exc_info=True)
            self.update_status("Error", f"Order processing failed: {str(e)}")
