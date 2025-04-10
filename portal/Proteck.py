from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from tkinter import messagebox
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from utility.helper import log_login_status,initialize_driver
from selenium.webdriver.chrome.service import Service

from exact_address_check.proteck_check_exact_address import find_matching_order
from utils.helper import handle_login_status
class Proteck:
    def __init__(self, username, password, portal_url, portal_name, proxy,session):
        #self.client_data = client_data
        self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)

    def initialize_driver(self):
        """Initialize Selenium WebDriver without version dependency."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")  #Maximize window
            chrome_options.add_argument("--disable-notifications")  #Disable pop-ups

            self.driver = webdriver.Chrome(options=chrome_options)  #Auto-detect ChromeDriver
            return self.driver
        except Exception as e:
            logging.error(f"Error initializing WebDriver: {e}")
            return None

    def login_to_portal(self,username, password, portal_url, portal_name,proxy,session):
        """Login to a generic portal (extendable)."""
        try:
            self.driver = self.initialize_driver()
            if not self.driver:
                raise Exception("WebDriver initialization failed.")

            self.driver.get(portal_url)
            logging.info(f"Navigating to {portal_url}...")
        # Wait for the username field to be visible
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='UserNameOrEmail']"))
            )

            # Enter the username and password
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").clear()
            self.driver.find_element(By.XPATH, "//*[@id='UserNameOrEmail']").send_keys(username)
            self.driver.find_element(By.XPATH, "//*[@id='Password']").send_keys(password)

            # Submit the login form
            self.driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[2]/form/input[3]").click()
            logging.info(f"Clicked login button for {username}")

            # Wait for login success by checking page title
            WebDriverWait(self.driver, 60).until(EC.title_contains("Partner Portal"))

            title = self.driver.title
            login_check_keyword=["Partner Portal"]

            handle_login_status(title, username, login_check_keyword,portal_name)

            # # Maximize the window and set position
            # self.driver.set_window_position(0, 0)
            # self.driver.maximize_window()
            return self.driver
        except Exception as e:
            if self.driver:
                #self.log_login_status(username, portal_name, "Login Failed", None, str(e))
                logging.error(f"Error during login to {portal_name}: {e}")
                messagebox.showerror("Error", f"Login failed: {e}")

        # finally:
        #     pass
        #     # if self.driver:
        #     #     self.driver.quit()
