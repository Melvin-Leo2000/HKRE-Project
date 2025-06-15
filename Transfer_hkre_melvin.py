# Jan 10, 2023. Based on selenium-4.7.2

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time, datetime
import pandas as pd
import os

# Newly implemented stealth mode
from selenium_stealth import stealth

WEBLOAD_TIMEOUT = 10 # Maximum seconds to fully load a web page
date = datetime.datetime.now().strftime("%Y%m%d")

current_directory =  os.path.dirname(os.path.abspath(__file__)) # Current Existing Directory
hkre_download_dir = os.path.join(current_directory, 'HKR New Files') # HKRE New Downloaded FIle Folder

csv_file_path = os.path.join(current_directory, 'HKRE Database.csv') # Path to the CSV file
target_web = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential_t18m.htm" # Target webpage

# To be changed 

# working_dir = r'C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213' # Path of working directory
# log_path = rf"C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213\{date}_log.txt" # Path of log file
# index_csv_path = rf'C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213\{date}_devm_index_t18m.csv' # Path of index csv

# dl_pdf_path = rf"C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213\{date}_pdfs_t18m" # Path of downloading pdf

# adding a new product to our database (Csv file)
def append_to_csv(csv_file_path, new_filename):
    new_row = pd.DataFrame({'File Name': [new_filename]})
    new_row.to_csv(csv_file_path, mode='a', header=False, index=False)


# awaiting for pdf to finish downloading
def wait_for_pdf_downloading(driver, url, filename):

    df = pd.read_csv(csv_file_path) # Reload the CSV file and get the 'File Name' column into a set for each check
    file_names_in_csv = set(df['File Name'])
    
    # Check if the file name exists in the 'File Name' column of the CSV
    if filename in file_names_in_csv:
        print(f"{filename} already exists in the CSV, skipping download.")
        return

    # If the file is not found in the CSV, check if it exists in the download folder
    file_path = os.path.join(hkre_download_dir, filename)
    
    if os.path.exists(file_path):
        print(f"{filename} already exists in the download directory, skipping download.")
        return
    
    time.sleep(5)

    # If the file is not found in the CSV or folder, download it
    driver.get(url)

    # Checking if the file has finished downloading
    while True:
        if os.path.exists(file_path):
            print(f'Download complete: {file_path}.')
            # Optionally append the new file name to the CSV
            append_to_csv(csv_file_path, filename)
            return
        time.sleep(2)



def headless_chrome_options() -> Options:
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # with this option, no Chrome window will be popped

    # Following steps will add increased security and stealth to the browsng 
    # Tells websites information about the browser type, operating system, and version among other details, help automated sessions blend in with regular traffic
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36") 

    # Disabling the "Chrome is being controlled by automated test software" infobar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Disabling the use of the automation extension, we tell Chrome not to load the automation extension, which can also be a sign of browser automation.
    options.add_experimental_option("useAutomationExtension", False)

    # Targets and disables the internal flags or features that make navigator.webdriver or similar properties reveal the presence of automation
    options.add_argument("--disable-blink-features=AutomationControlled") 


    prefs = {"download.default_directory" : hkre_download_dir, # necessary in --headless mode
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
            } 
    options.add_experimental_option("prefs", prefs)
    return options


# checks if the scv path exists, then creates a new one if it doesn't.  convert data into a dataframe and save it to a csv file
# if csv exists, it will go straight to read the file into dataframe, apped data and update it 
# def append_to_csv(csv_path, data):
#         if not os.path.isfile(csv_path): # Create a new csv
#                 df = pd.DataFrame(data)
#                 df.to_csv(csv_path, encoding='utf-8-sig', index=False)
#         else: # Append to the original csv
#                 df = pd.read_csv(csv_path)
#                 df = df.append(data, ignore_index=True)
#                 df.to_csv(csv_path, encoding='utf-8-sig', index=False)


# Write a new entry into the log file to update the current date and time, while adding on a new data

# def update_log(data):
#         with open(log_path,'a+', encoding='utf-8-sig') as f:
#                 f.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+':'+data+'\n')

def main():
        # if not os.path.exists(dl_pdf_path): os.mkdir(dl_pdf_path)

        service = Service()
        options = headless_chrome_options()
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Stealth mode
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        # Changing the property of the navigator value for webdriver to undefined 
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        driver.get(target_web)
        
        el_disclaim = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='content']/div[1]/div[3]/div[1]/input")) # click the input box
        el_disclaim.click()
        el_cont =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='continueBtn']")) # click continue
        el_cont.click()

        # index list
        el_list = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='sort_table']/tbody/tr"))
        begin = 1
        end = len(el_list)
        tl_loop = time.time()

        time.sleep(3)

        for j in range(begin, end+1):
                data = []
                #===========Loop begins=================================================
                tl = time.time()
                devm = {}
                # Index page information

                time.sleep(3)
                el_devm = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[1]/div/a".format(j))
                page = el_devm.get_attribute("href")
                devm['name'] = el_devm.text
                # update_log("==== Development " + str(j) + " " + devm['name'].replace('\n', '') + " begins ====")

                time.sleep(3)
                devm['web'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[1]/div/div/a").get_attribute("href")
                devm['phas'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[2]").text
                devm['phasnm'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[3]").text
                devm['addr'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[4]").text
                devm['area'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[5]").text
                devm['date'] = driver.find_element("xpath", f"//*[@id='sort_table']/tbody/tr[{j}]/td[6]").text
        
                # Development page information
                ## sales brochure

                time.sleep(3)
                driver.get(page)
                try:
                        el_sb = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='brochure']"))
                except:
                        driver.get(page)

                el_sb = []
                try:
                        el_sb = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='brochure']/div[2]/table/tbody/tr"))
                except:
                        pass

                time.sleep(3)

                if len(el_sb) > 2:
                        devm['sb1_date'] = el_sb[0].text[-11:len(el_sb[0].text)]
                        devm['sbe_date'] = el_sb[1].text[-11:len(el_sb[1].text)]

                        for r in range(2, len(el_sb)-1):
                                devm['sb{0}_text'.format(r-1)] = el_sb[r].text
                                # download sb
                                url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", f"//*[@id='brochure']/div[2]/table/tbody/tr[{r+1}]/td[1]/div/span/a")).get_attribute("href")
                                # Wait for the file to be downloaded
                                filename = f"{url.split('/')[-1][:-4]}.PDF"
                                wait_for_pdf_downloading(driver, url, filename)
                        
                        time.sleep(3)
                        devm['sbe_text'] = el_sb[-1].text
                        url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", f"//*[@id='brochure']/div[2]/table/tbody/tr[{len(el_sb)}]/td[1]/div/span/a")).get_attribute("href")

                        filename = f"{url.split('/')[-1][:-4]}.PDF"
                        wait_for_pdf_downloading(driver, url, filename)
                        time.sleep(3)
                        try:
                                div_elements = url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='brochure']/div[2]/div"))
                                for _ in range(0, len(div_elements)):
                                        devm['sb_note'] = devm.get('sb_note', "") + ('' if devm.get('sb_note', "")=="" else '\n') + div_elements[_].text
                        except:
                                print("sb_note N/A")
                                # update_log("sb_note N/A")
                else:
                        print("Sales Brochure N/A")
                        # update_log("Sales Brochure N/A")
                        try:
                                devm['sb_note'] = url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='brochure']/div[2]")).text
                        except:
                                print("sb_note N/A")
                                # update_log("sb_note N/A")
                # break
                ## register of transactions
                try:
                        url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='transaction']/div[2]/table/tbody/tr[2]/td[1]/div/span/a")).get_attribute('href')

                        filename = f"{url.split('/')[-1][:-4]}.PDF"
                        wait_for_pdf_downloading(driver, url, filename)

                        div_elements =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='transaction']/div[2]/div"))
                        for _ in range(0, len(div_elements)):
                                devm['rt_text'] = devm.get('rt_text', "") + ('' if devm.get('rt_text', "")=="" else '\n') + div_elements[_].text
                except:
                        print("RT N/A")
                        # update_log("RT N/A")
                #
                ## price orders
                el_pos = []
                try:
                        el_pos =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='price']/div[2]/table/tbody/tr"))
                except:
                        pass
                if len(el_pos) > 0:
                        for r in range(len(el_pos)):
                                devm[f'po{r+1}_text'] = el_pos[r].text
                                url =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", f"//*[@id='price']/div[2]/table/tbody/tr[{r+1}]/td[1]/div/span/a")).get_attribute('href')
                                
                                filename = f"{url.split('/')[-1][:-4]}.PDF"
                                wait_for_pdf_downloading(driver, url, filename)
                        try:
                                div_elements =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_elements("xpath", "//*[@id='price']/div[2]/div"))
                                for _ in range(len(div_elements)):
                                        devm['po_note'] = devm.get('po_note', "") + ('' if devm.get('po_note', "")=="" else '\n') + div_elements[_].text
                        except:
                                print("po_note N/A")
                                # update_log("po_note N/A")
                else:
                        print("Price Order N/A")
                        # update_log("Price Order N/A")
                        try:
                                devm['po_note'] =  WebDriverWait(driver, WEBLOAD_TIMEOUT).until(lambda driver: driver.find_element("xpath", "//*[@id='price']/div[2]")).text
                        except:
                                print("po_note N/A")
                                # update_log("po_note N/A")
                data.append(devm)
                driver.back()
                # append_to_csv(index_csv_path, data)
                print("finished devm "+str(j) + " in " + str((time.time()-tl)/60) + "min")
                # update_log("finished devm "+str(j) + " in " + str((time.time()-tl)/60) + "min")
                #===========Loop ends=================================================

        print(f'{(time.time()-tl_loop)/60} min') # log the total time for whole loop
        driver.quit()




if __name__ == "__main__":
        main() # For t18m
        print('Finished Data Cleaning')
        # update_log("finished t18m")
        # index_csv_path = rf'C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213\{date}_devm_index.csv' # Path of index csv
        # dl_pdf_path = rf"C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\weekly_dl_20230213\{date}_pdfs" # Path of downloading pdf
        # target_web = "https://www.srpe.gov.hk/opip/disclaimer_index_for_all_residential.htm" # Target web URL
        # main() # For non t18m
        # update_log("finished automation")