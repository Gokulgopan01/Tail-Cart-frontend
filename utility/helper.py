import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.webdriver.chrome.service import Service

def initialize_driver(self):
        """Initialize Selenium WebDriver."""
        try:
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")  # ✅ Maximize window
                chrome_options.add_argument("--disable-notifications")  # ✅ Disable pop-ups

                service = Service("chromedriver.exe")  # ✅ Ensure you have ChromeDriver installed
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                return self.driver
        except Exception as e:
                logging.error(f"Error initializing WebDriver: {e}")
                return None
# def __init__(self, client_data, order_details):
#         self.client_data = client_data  # Contains username and password
#         self.order_details = order_details  # Contains order details
#         self.session = None  # Will store session after successful login
#         self.driver = None  # Will store the driver instance
#         logging.basicConfig(level=logging.INFO)
# def log_login_status(self, username, portal_name, status, session=None, error_message=None):
#         """Log the login status."""
#         logging.info(f"{username} logged into {portal_name}: {status} - {error_message if error_message else ''}")


def log_login_status(self, username, portal_name, status, additional_info=None, error_message=None):
        """Log login status (can be extended to store in DB or send email alerts)."""
        logging.info(f"Login Status: {status} | User: {username} | Portal: {portal_name}")
        if error_message:
            logging.error(f"Error Details: {error_message}")

def handle_exception(self, e):
        """Handle exceptions and log the error."""
        stack_trace = traceback.format_exc()
        if stack_trace:
            e = stack_trace
        self.update_report_data(None, str(e), 'UNABLE TO LOGIN')        