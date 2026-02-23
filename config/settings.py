"""
Configuration settings for HKRE App
All configuration constants are defined here.
"""
import os
import platform
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# ============================================================================
# Web Scraping Configuration
# ============================================================================

WEBLOAD_TIMEOUT = 5

# Chrome executable path (auto-detect based on OS, or use environment variable)
def _get_default_chrome_path():
    """Get default Chrome path based on operating system"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return chrome_path
    elif system == "Linux":
        chrome_path = "/usr/bin/google-chrome"
        if os.path.exists(chrome_path):
            return chrome_path
    elif system == "Windows":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            return chrome_path
    
    # Fallback: let Selenium find it automatically
    return None

CHROME_EXE_PATH = os.getenv("CHROME_EXE_PATH") or _get_default_chrome_path()

# ============================================================================
# Google Services Configuration
# ============================================================================

# Google Drive parent folder ID
PARENT_FOLDER_ID = os.getenv(
    "PARENT_FOLDER_ID",
    "1hixECvWsddWgy94PT0y2OQ_-kysAkvya"
)

# ============================================================================
# Target URLs
# ============================================================================

T18M_URL = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential_t18m.htm"
NON_T18M_URL = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential.htm"

# ============================================================================
# Directory Paths
# ============================================================================

# Data directories for downloads
DATA_DIR = BASE_DIR / "data"
T18M_DIR = DATA_DIR / "t18m"
NON_T18M_DIR = DATA_DIR / "non-t18m"

# Credentials file path
CREDENTIALS_FILE = BASE_DIR / "config" / "credentials.json"

