"""
Scraping Module
Provides browser setup, web interaction, file download, and property processing utilities
"""

from .browser import headless_chrome_options, launch_web
from .web_interaction import agree_terms, safe_driver_get
from .file_download import download_pdf, get_download_directories
from .property_processing import (
    extract_property_data,
    navigate_and_extract_pdfs,
    clean_property_data,
    build_lookup_index,
    check_property_in_database,
    process_property_pdfs,
    restart_browser,
    process_single_property,
)

__all__ = [
    # Browser setup
    "headless_chrome_options",
    "launch_web",
    # Web interaction
    "agree_terms",
    "safe_driver_get",
    # File download
    "download_pdf",
    "get_download_directories",
    # Property processing
    "extract_property_data",
    "navigate_and_extract_pdfs",
    "clean_property_data",
    "build_lookup_index",
    "check_property_in_database",
    "process_property_pdfs",
    "restart_browser",
    "process_single_property",
]
