from selenium.webdriver.support.ui import Select
import time
import logging

from utils.helper import clearing, data_filling_text, data_filling_text_QC, javascript_excecuter_datefilling, radio_btn_click, select_field

class RedBellFormFiller:
    def __init__(self, driver):
        self.driver = driver
        #merged_json=
    # def fill_form(self, merged_json, order_details, form_config):
    #     subject_data = merged_json.get("subject_data", {})
    #     for page in form_config.get("page", []):
    #         for section in page.get("Subject_info", []):
    #             field_type = section.get("filedtype")
    #             for item in section.get("values", []):
    #                 if isinstance(item, dict):  # save_data, nextpage
    #                     continue

    #                 key, xpath, mode = item
    #                 value = subject_data.get(key)
    #                 if value in [None, ""]:
    #                     continue

    #                 try:
    #                     elem = self.driver.find_element("xpath", xpath)
    #                     if field_type == "Textbox":
    #                         elem.clear()
    #                         elem.send_keys(str(value))
    #                     elif field_type == "Textbox_default":
    #                         elem.clear()
    #                         elem.send_keys(str(key))  # key has actual value like "0"
    #                     elif field_type == "select_data":
    #                         Select(elem).select_by_visible_text(str(value))
    #                     elif field_type == "select_default":
    #                         Select(elem).select_by_visible_text(str(key))  # key has default like "Yes"
    #                     elif field_type == "date_fill_javascript":
    #                         self.driver.execute_script(f"document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value = '{value}'")
    #                     else:
    #                         logging.warning(f"Unknown field type: {field_type}")
    #                     time.sleep(0.5)
    #                 except Exception as e:
    #                     logging.error(f"Error filling field {key} at {xpath}: {e}")

    #         # handle navigation if needed
    #         for item in page.get("Subject_info", []):
    #             if item.get("filedtype") == "save_data":
    #                 next_page = item["values"][0].get("nextpage")
    #                 logging.info(f"Navigating to next page: {next_page}")
    #                 # Click save or navigate if applicable
    #                 break


    def fill_form(self, merged_json, order_details, form_config):
        subject_data = merged_json.get("subject_data", {})

        subject_data = merged_json.get("subject_data", {})

        for page in form_config.get("page", []):
            for section in page.get("Subject_info", []):
                field_type = section.get("filedtype")
                for item in section.get("values", []):
                    if isinstance(item, dict):
                        continue  # Skip nextpage or save_data

                    if len(item) != 3:
                        logging.warning(f"Invalid field item format: {item}")
                        continue

                    key, xpath, mode = item
                    value = subject_data.get(key, key)  # fallback to key for default fields

                    if value in [None, ""] and "default" not in field_type:
                        logging.info(f"Skipping {field_type} with empty value for key: {key}")
                        continue

                    try:
                        # Use helper methods for clarity
                        if field_type == "Textbox":
                            data_filling_text(self.driver, value, xpath, mode)

                        elif field_type == "Textbox_default":
                            data_filling_text(self.driver, key, xpath, mode)

                        elif field_type == "select_data":
                            select_field(self.driver, value, xpath, mode)

                        elif field_type == "select_default":
                            select_field(self.driver, key, xpath, mode)

                        elif field_type == "radiobutton_data":
                            radio_btn_click(self.driver, value, xpath, mode)

                        elif field_type == "radiobutton_default":
                            radio_btn_click(self.driver, key, xpath, mode)

                        elif field_type == "date_fill_javascript":
                            javascript_excecuter_datefilling(self.driver, value, xpath, mode)

                        elif field_type == "clearing":
                            clearing(self.driver, xpath, mode)

                        elif field_type == "Textbox_QC":
                            data_filling_text_QC(self.driver, value, xpath, mode)

                        elif field_type == "Textbox_default_QC":
                            data_filling_text_QC(self.driver, key, xpath, mode)

                        # elif field_type == "save_data":
                        #     for cookie in self.driver.get_cookies():
                        #         session.cookies.set(cookie['name'], cookie['value'])
                        #     save_form(self.driver, order_id)
                        #     logging.info("Form saved. Navigating to Neighborhood info...")
                        #     time.sleep(10)
                        #     self.driver.get(Neighborhood_url["Neighborhood"])

                        else:
                            logging.warning(f"Unknown field type: {field_type}")

                        #time.sleep(0.5)

                    except Exception as e:
                        logging.error(f"Error processing {field_type} - Key: {key}, XPath: {xpath}, Error: {e}")


            # # Handle page navigation if any
            # for section in sections:
            #     if section.get("filedtype") == "save_data":
            #         next_item = section.get("values", [{}])[0]
            #         next_page = next_item.get("nextpage")
            #         logging.info(f"Navigating to next page: {next_page}")
            #         # You can click a "Next" or "Save" button here if you know its xpath
            #         break
