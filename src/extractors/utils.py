"""
Utility functions for development info extraction
"""
from selenium.webdriver.support.ui import WebDriverWait


def extract_pdf_url_from_xpath(driver, WEBLOAD_TIMEOUT, xpath):
    """
    Extract PDF URL from an XPath element.

    Returns:
        URL string if successful, None if element not found
    """
    try:
        url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda d: d.find_element("xpath", xpath)
        ).get_attribute("href")
        return url
    except Exception:
        return None
