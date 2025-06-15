from selenium.webdriver.support.ui import WebDriverWait
from devm_versions import update_log

def price_orders(WEBLOAD_TIMEOUT, docs, devm, driver, pdf):
    try:
        el_pos = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda driver: driver.find_elements("xpath", "//*[@id='price']/div[2]/table/tbody/tr")
        )
    except Exception:
        el_pos = []

    if el_pos:
        for r, element in enumerate(el_pos, start=1):
            # Get row text
            devm[f'po{r}_text'] = element.text

            # Get PDF URL and download
            try:
                url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                    lambda driver: driver.find_element("xpath", f"//*[@id='price']/div[2]/table/tbody/tr[{r}]/td[1]/div/span/a")
                ).get_attribute('href')
                filename = f"{url.split('/')[-1][:-4]}.PDF"

                # collate pdf names and url 
                pdf[filename] = url
                
            except Exception:
                update_log(docs, f"Failed to download Price Order PDF for row {r}\n")

        # Get text content
        try:
            div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda driver: driver.find_elements("xpath", "//*[@id='price']/div[2]/div")
            )
            devm['po_note'] = "\n".join([devm.get('po_note', "")] + [elem.text for elem in div_elements if elem.text])
        except Exception:
            update_log(docs, "po_note N/A\n")
    else:
        update_log(docs, "Price Order N/A\n")
        try:
            devm['po_note'] = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda driver: driver.find_element("xpath", "//*[@id='price']/div[2]")
            ).text
        except Exception:
            update_log(docs, "po_note N/A\n")