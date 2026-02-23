"""
Web Interaction Module
Handles page interactions and navigation with retry logic
"""

import time
from selenium.webdriver.support.ui import WebDriverWait


def agree_terms(driver, webload_timeout=5):
    """
    Interact with the disclaimer page to accept terms and continue.
    
    Args:
        driver: WebDriver instance
        webload_timeout: Timeout for waiting for elements (default: 5)
    """
    # Click the disclaimer checkbox
    el_disclaim = WebDriverWait(driver, webload_timeout).until(
        lambda driver: driver.find_element("xpath", "//*[@id='content']/div[1]/div[3]/div[1]/input")
    )
    el_disclaim.click()

    # Click the continue button
    el_cont = WebDriverWait(driver, webload_timeout).until(
        lambda driver: driver.find_element("xpath", "//*[@id='continueBtn']")
    )
    el_cont.click()


def safe_driver_get(driver, url, retries=2):
    """
    Safely navigate to a URL with retry logic for network errors.
    
    Args:
        driver: WebDriver instance
        url: URL to navigate to
        retries: Number of retry attempts (default: 2)
    
    Returns:
        True if successful, False if failed after all retries
    """
    for attempt in range(retries):
        try:
            driver.get(url)
            return True  # Success
        except Exception as e:
            if "EOF occurred in violation of protocol" in str(e):
                # Network error - wait with exponential backoff
                time.sleep(2 ** attempt)
            else:
                # Other errors should be raised immediately
                raise e
    return False  # Failed after all retries

