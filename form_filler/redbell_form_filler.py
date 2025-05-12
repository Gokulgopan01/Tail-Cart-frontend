from selenium.webdriver.support.ui import Select
import time
import logging

class RedBellFormFiller:
    def __init__(self, driver):
        self.driver = driver
        #merged_json=
    def fill_form(self, merged_json, order_details, form_config):
        subject_data = merged_json.get("subject_data", {})
        for page in form_config.get("page", []):
            for section in page.get("Subject_info", []):
                field_type = section.get("filedtype")
                for item in section.get("values", []):
                    if isinstance(item, dict):  # save_data, nextpage
                        continue

                    key, xpath, mode = item
                    value = subject_data.get(key)
                    if value in [None, ""]:
                        continue

                    try:
                        elem = self.driver.find_element("xpath", xpath)
                        if field_type == "Textbox":
                            elem.clear()
                            elem.send_keys(str(value))
                        elif field_type == "Textbox_default":
                            elem.clear()
                            elem.send_keys(str(key))  # key has actual value like "0"
                        elif field_type == "select_data":
                            Select(elem).select_by_visible_text(str(value))
                        elif field_type == "select_default":
                            Select(elem).select_by_visible_text(str(key))  # key has default like "Yes"
                        elif field_type == "date_fill_javascript":
                            self.driver.execute_script(f"document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value = '{value}'")
                        else:
                            logging.warning(f"Unknown field type: {field_type}")
                        time.sleep(0.5)
                    except Exception as e:
                        logging.error(f"Error filling field {key} at {xpath}: {e}")

            # handle navigation if needed
            for item in page.get("Subject_info", []):
                if item.get("filedtype") == "save_data":
                    next_page = item["values"][0].get("nextpage")
                    logging.info(f"Navigating to next page: {next_page}")
                    # Click save or navigate if applicable
                    break
