from selenium.webdriver.support.ui import WebDriverWait

from devm_versions import update_log

def register_of_transactions(WEBLOAD_TIMEOUT, docs, devm, driver, pdf):
    try:
        # Get PDF URL and download
        url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda driver: driver.find_element("xpath", "//*[@id='transaction']/div[2]/table/tbody/tr[2]/td[1]/div/span/a")
        ).get_attribute('href')

        filename = f"{url.split('/')[-1][:-4]}.PDF"
        
        # collate pdf names and url 
        pdf[filename] = url

        # Get text content
        div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda driver: driver.find_elements("xpath", "//*[@id='transaction']/div[2]/div")
        )
        devm['rt_text'] = "\n".join([devm.get('rt_text', "")] + [elem.text for elem in div_elements if elem.text])
    except Exception:
        update_log(docs, "RT N/A\n")