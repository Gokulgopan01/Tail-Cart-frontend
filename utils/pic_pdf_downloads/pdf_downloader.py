from selenium.webdriver.common.print_page_options import PrintOptions
from base64 import b64decode
import os

def pdf_downloader(driver,comp_name,path):
        
        try:
            print_options = PrintOptions()
            print_options.page_height = 8.5
            print_options.page_width = 11
            print_options.scale = 0.3
            driver.print_page(print_options)
            pdfBase64 = driver.print_page()
            if pdfBase64:  # Check if the result is valid
                pdf_bytes = b64decode(pdfBase64, validate=True)
                if not os.path.exists(path):
                    os.makedirs(path)
                filepath = os.path.join(path, f"{comp_name}.pdf")
                with open(filepath, "wb") as f:
                    f.write(pdf_bytes)  # Save PDF
                    
            return True      
        except Exception as e:
            print("exception in pdf_downloader: ", e)
            return False