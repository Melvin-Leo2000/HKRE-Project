from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time, datetime
import pandas as pd
import os, re
from datetime import datetime 

# Newly implemented stealth mode
from selenium_stealth import stealth

# Functions for getting devm information
from development_info.sales_brochure import sales_brochure
from development_info.register_of_transactions import register_of_transactions
from development_info.price_orders import price_orders

# Get the data from the devm spreadsheet
from devm_versions import google_auth, insert_new_data, get_devm, update_log, upload_file_to_gdrive, create_drive_folder, get_drive_service

# Authenticate with Google
spreadsheet, docs = google_auth()

WEBLOAD_TIMEOUT = 5

chrome_exe_path = "/usr/bin/google-chrome"
# chrome_exe_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe" # Path of chrome.exe in my computer


# Construct the path to the "HKR New Files" directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# for t18m
sales_brochure_files_dir = os.path.join(script_dir, "t18m", "sales brochure")
register_of_transactions_files_dir = os.path.join(script_dir, "t18m", "register of transactions")
price_lists_files_dir = os.path.join(script_dir, "t18m", "price lists")

parent_folder_id = '1hixECvWsddWgy94PT0y2OQ_-kysAkvya'

# Getting the Database 
# csv_path = os.path.join(script_dir, "HKRE Database.csv")

# df = pd.read_csv(csv_path)
# file_names = df["File Name"].tolist()


def headless_chrome_options() -> Options:
    """
    Configures headless Chrome WebDriver options for stealth and automated browsing.
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

    # Set Chrome binary location
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


def agree_terms(driver):
        # Interact with initial page elements
    el_disclaim = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
        lambda driver: driver.find_element("xpath", "//*[@id='content']/div[1]/div[3]/div[1]/input")
    )
    el_disclaim.click()


    el_cont = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
        lambda driver: driver.find_element("xpath", "//*[@id='continueBtn']")
    )
    el_cont.click()



def safe_driver_get(driver, url, retries=2):
    for attempt in range(retries):
        try:
            driver.get(url)
            return True  # success
        except Exception as e:
            if "EOF occurred in violation of protocol" in str(e):
                time.sleep(2 ** attempt)
            else:
                raise e
    return False  # failed after retries



def download_pdf(driver, pdf, dir, parent_folder_id, drive_service):

    params = {
        "behavior": "allow",
        "downloadPath": dir
    }

    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    timeout_download = False

    for filename, url in pdf.items():
        
        # Ensure that file download is smooth
        if not safe_driver_get(driver, url):
            update_log(docs, f"Failed to load {url} after retries, URL likely don't exist. Skipping {filename}.\n")
            continue

        file_path = os.path.join(dir, filename)
        start_time = time.time()
        prev_size = -1

        while True:

            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size == prev_size:
                    break
                prev_size = size


            if time.time() - start_time > 300:

                # Update that there is a timeout download 
                update_log(docs, f"Timeout downloading: {filename}.\nRestarting Process...\n")
                print(f"Timeout downloading: {filename}")
                timeout_download = True
                break

            time.sleep(2)


        # if there is a timeout download
        if timeout_download:
            break

        # Proceed to upload if file exists
        if os.path.exists(file_path):
            update_log(docs, f"Downloaded: {filename}.\n")

            # Upload with retry and exponential backoff
            for attempt in range(3):
                try:
                    upload_file_to_gdrive(file_path, filename, drive_service, parent_folder_id)
                    break
                except Exception as e:
                    print(f"Upload failed for {filename}, attempt {attempt+1}: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

            os.remove(file_path)

        time.sleep(3)  # Add delay between downloads to reduce API stress

    return timeout_download
        

def launch_web(target_web):
    service = Service()
    options = headless_chrome_options()
    driver = webdriver.Chrome(service=service, options=options)

    stealth(driver,
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

    # agree to terms
    agree_terms(driver)

    return driver



def main(target_web, version, run_folder_id, j):

    # Get the database
    devm_df, sheet = get_devm(spreadsheet, version)
    devm_df = devm_df.apply(lambda col: col.map(lambda x: x.replace('\n', '').strip() if isinstance(x, str) else x))

    drive_service = get_drive_service()

    # Launch the web
    driver = launch_web(target_web)
    time.sleep(2)

    # Fetch the list of items
    el_list = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
        lambda driver: driver.find_elements("xpath", "//*[@id='sort_table']/tbody/tr")
    )

    end = len(el_list)

    tl_loop = time.time()
    
    while j <= end:
        try:
            devm = {}
            tl = time.time()

            # Getting data from the selected developments 
            el_devm = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[1]/div/a")
            devm['name'] = el_devm.text
            devm['web'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[1]/div/div/a").get_attribute("href")
            devm['phas'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[2]").text
            devm['phasnm'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[3]").text
            devm['addr'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[4]").text
            devm['area'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[5]").text
            devm['date'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[6]").text
            
            name_cleaned = devm['name'].replace('\n', '')
            update_log(docs, f"==== Development {j} {name_cleaned} begins ====\n")


            # Navigate to individual development pages
            page = el_devm.get_attribute("href")
            driver.get(page)

            # Extract sales brochure information
            try:
                el_sb = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                    lambda driver: driver.find_element("xpath", "//*[@id='brochure']")
                )
            except:
                driver.get(page)

            el_sb = []

            try:
                el_sb = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                    lambda driver: driver.find_elements("xpath", "//*[@id='brochure']/div[2]/table/tbody/tr")
                )
            except:
                pass

            # Checks if at least three rows are found in the table
            if len(el_sb) > 2:

                # Data from Sales Brochure Table
                sales_brochure_pdf = {}
                sales_brochure(WEBLOAD_TIMEOUT, docs, devm, el_sb, driver, sales_brochure_pdf)
                
                # Register of Transactions
                register_of_transactions_pdf = {}
                register_of_transactions(WEBLOAD_TIMEOUT, docs, devm, driver, register_of_transactions_pdf)

                # Price Orders
                price_orders_pdf = {}
                price_orders(WEBLOAD_TIMEOUT, docs, devm, driver, price_orders_pdf)

            else:
                update_log(docs, f"Data not full available. Skipping this development.\n\n")
                driver.back()
                j += 1
                continue
                

            # Remove the new lines so that it does not interfere in the new changes 
            devm_nolines = {
                key: value.replace('\n', '').strip() if isinstance(value, str) else value
                for key, value in devm.items()
            }

            found = False
            new_file = True

            
            for index, row in devm_df.iterrows():
                if all(value in row.values for value in devm_nolines.values() if value is not None):
                    print(f"{devm_nolines['name']}: No Changes")
                    found = True
                    break

                # Checks whether the property name is found inside the devm sheet
                elif devm_nolines['name'] == row.iloc[0]:
                    new_file = False
                    new_updates = [f"{key}: {value}" for key, value in devm_nolines.items() if value not in row.values]
                            
                
            if not found:
                # Get the name of the new development file
                if new_file: 
                    update_log(docs, f"New File: {devm_nolines['name']}\n")
                
                else:
                    update_log(docs, f"Updates to Existing File: {devm_nolines['name']}\n" + '\n'.join([f'updated {u}' for u in new_updates]))

                
                folder_name = devm_nolines['name']
                property_folder_id = create_drive_folder(folder_name, parent_id=run_folder_id)

                # Download the necessary pdfs into each file and folder 
                timeout_download = download_pdf(driver, sales_brochure_pdf, sales_brochure_files_dir, property_folder_id, drive_service)
                
                # If there is a timeout download, refresh the page and try again
                if timeout_download:
                    driver.quit()
                    time.sleep(2)
                    
                    driver = launch_web(target_web)
                    time.sleep(2)
                    continue

                download_pdf(driver, register_of_transactions_pdf, register_of_transactions_files_dir, property_folder_id, drive_service)
                download_pdf(driver, price_orders_pdf, price_lists_files_dir, property_folder_id, drive_service)
                # if the property name is not found, then we will update the whole row with the new data
                insert_new_data(sheet, devm)
        

            driver.back()
            update_log(docs, f"finished devm {j} in {(time.time() - tl) / 60:.2f} min\n\n")
            j += 1 
        
        except Exception as e:
            update_log(docs, f"Ran into error at row {j} due to memory overload\n Retrying again...\n\n")
            time.sleep(3) 

            # Restarting the whole process again to avoid memory overload
            driver.quit()
            driver = launch_web(target_web)
            time.sleep(3)
            continue

    update_log(docs, f'Total time: {(time.time() - tl_loop) / 60:.2f} min\n\n')
    driver.quit()
    return j


if __name__ == "__main__":
    
    # Start by updating the Date of the Scrape in the logs
    today_date = datetime.now().strftime("%Y-%m-%d")

    # new_folder_name = f"Metric Job - {datetime.today().strftime('%Y-%m-%d')}"
    
    folder_id = '1_1Y3VUgyk3cOWqHOzn22teepKtz7AnNH'

    # create_drive_folder(new_folder_name, parent_id=parent_folder_id)

    j = 71

    # Create a new drive folder for t18ms
    # t18ms = create_drive_folder('t18m files', parent_id=folder_id)



    # Begin Scrape for t18m
    # update_log(docs, f"Date of Scrape: {today_date}\nFor t18m\n\n")
    # target_web = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential_t18m.htm"
    # main(target_web, "t18m", t18ms, j)
    # update_log(docs, f"finished t18m\n\n")

    # Create a new drive folder for non-t18ms
    # non_t18ms = create_drive_folder('non-t18m files', parent_id=folder_id)
    non_t18ms = '1EzMoVfZ-tdub6HcF7BeJC9jQJEeq3xZ7'

    # Begin Scrape for non-t18m
    update_log(docs, f"For non-t18m\n\n")
    target_web = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential.htm" # Target web URL
    main(target_web, "non-t18m", non_t18ms, j)
    update_log(docs, "finished non-t18m and automation")