from selenium.webdriver.support.ui import WebDriverWait

from src.google_services import update_log
from .utils import extract_pdf_url_from_xpath

def register_of_transactions(WEBLOAD_TIMEOUT, docs, devm, driver, pdf):
    try:
        rt_rows = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda d: d.find_elements("xpath", "//*[@id='transaction']/div[2]/table/tbody/tr")
        )
    except Exception:
        rt_rows = []

    if rt_rows:
        # Remaining rows (skip first): rt1_text, rt2_text, ... with PDF links
        for r, element in enumerate(rt_rows[1:], start=2):
            devm[f'rt{r - 1}_text'] = element.text

            xpath = f"//*[@id='transaction']/div[2]/table/tbody/tr[{r}]/td[1]/div/span/a"
            url = extract_pdf_url_from_xpath(driver, WEBLOAD_TIMEOUT, xpath)
            if url:
                text_key = element.text.replace('\n', '').strip()
                pdf[text_key] = url

        # Extract notes from div elements
        try:
            div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda d: d.find_elements("xpath", "//*[@id='transaction']/div[2]/div")
            )
            note_texts = [elem.text for elem in div_elements if elem.text]
            if note_texts:
                devm['rt_note'] = "\n".join([devm.get('rt_note', "")] + note_texts)
        except Exception:
            update_log(docs, "rt_note N/A\n")

        # First row: Date and Time of Update → rt_date (insert after rt_text in sheet: ... rt1_text, rt2_text, rt_note, rt_date, po...)
        devm['rt_date'] = rt_rows[0].text.replace('\n', '').strip() if rt_rows[0].text else ''
    else:
        update_log(docs, "RT N/A\n")
