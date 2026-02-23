from selenium.webdriver.support.ui import WebDriverWait
from src.google_services import update_log
from .utils import extract_pdf_url_from_xpath

def price_orders(WEBLOAD_TIMEOUT, docs, devm, driver, pdf):
    # Get price order table rows
    try:
        price_rows = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda d: d.find_elements("xpath", "//*[@id='price']/div[2]/table/tbody/tr")
        )
    except Exception:
        price_rows = []

    if price_rows:
        # Extract row text and PDF URLs
        for r, element in enumerate(price_rows, start=1):
            devm[f'po{r}_text'] = element.text
            
            xpath = f"//*[@id='price']/div[2]/table/tbody/tr[{r}]/td[1]/div/span/a"
            url = extract_pdf_url_from_xpath(driver, WEBLOAD_TIMEOUT, xpath)
            if url:
                text_key = element.text.replace('\n', '').strip()
                pdf[text_key] = url
            else:
                update_log(docs, f"Failed to extract Price Order PDF URL for row {r}\n")
        
        # Extract notes from div elements
        try:
            div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda d: d.find_elements("xpath", "//*[@id='price']/div[2]/div")
            )
            note_texts = [elem.text for elem in div_elements if elem.text]
            if note_texts:
                devm['po_note'] = "\n".join([devm.get('po_note', "")] + note_texts)
        except Exception:
            update_log(docs, "po_note N/A\n")
    else:
        update_log(docs, "Price Order N/A\n")
        # Fallback: try to get note from entire div[2]
        try:
            devm['po_note'] = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda d: d.find_element("xpath", "//*[@id='price']/div[2]")
            ).text
        except Exception:
            update_log(docs, "po_note N/A\n")
