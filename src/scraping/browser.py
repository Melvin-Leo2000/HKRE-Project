"""
Browser Setup Module
Handles Chrome WebDriver configuration and initialization
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

# Note: These constants should be passed as parameters or imported from config
# Default values provided for backward compatibility


def headless_chrome_options(chrome_exe_path=None) -> Options:
    """
    Configures headless Chrome WebDriver options for stealth and automated browsing.
    
    Args:
        chrome_exe_path: Path to Chrome executable (optional, will auto-detect if None)
    
    Returns:
        Configured ChromeOptions object
    """
    options = webdriver.ChromeOptions()

    # Enable Headless Mode
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    # User-Agent for blending automation traffic with normal user traffic
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36")

    # Disable automation infobar and extension
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Disable automation-related features
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Set Chrome binary location (only if path is provided and exists)
    if chrome_exe_path and os.path.exists(chrome_exe_path):
        options.binary_location = chrome_exe_path

    # Configure download preferences
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    return options


def launch_web(target_web, webload_timeout=5, chrome_exe_path=None):
    """
    Launch and configure a headless Chrome browser with stealth settings.
    
    Args:
        target_web: URL to navigate to
        webload_timeout: Timeout for web element loading (default: 5)
    
    Returns:
        Configured WebDriver instance
    """
    from .web_interaction import agree_terms
    
    service = Service()
    options = headless_chrome_options(chrome_exe_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Apply stealth settings to avoid detection
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # Hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Navigate to target webpage
    driver.get(target_web)

    # Agree to terms and conditions
    agree_terms(driver, webload_timeout)

    return driver

