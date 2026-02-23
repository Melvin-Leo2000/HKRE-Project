from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from src.google_services import update_log
from .utils import extract_pdf_url_from_xpath

def sales_brochure(WEBLOAD_TIMEOUT, docs, devm, el_sb, driver, pdf):
    # Extract dates from first two rows
    devm['sb1_date'] = pd.to_datetime(el_sb[0].text[-11:]).strftime('%d %b %Y')

    try:
        devm['sbe_date'] = pd.to_datetime(el_sb[1].text[-11:]).strftime('%d %b %Y')
    except Exception as e:
        print(f"Skipping invalid date for entry: {el_sb[1].text} — {e}")
        devm['sbe_date'] = None

    # Extract middle rows (2 to second-to-last)
    for r in range(2, len(el_sb) - 1):
        devm[f'sb{r - 1}_text'] = el_sb[r].text
        xpath = f"//*[@id='brochure']/div[2]/table/tbody/tr[{r + 1}]/td[1]/div/span/a"
        url = extract_pdf_url_from_xpath(driver, WEBLOAD_TIMEOUT, xpath)
        if url:
            text_key = el_sb[r].text.replace('\n', '').strip()
            pdf[text_key] = url

    # Extract last row
    devm['sbe_text'] = el_sb[-1].text
    xpath = f"//*[@id='brochure']/div[2]/table/tbody/tr[{len(el_sb)}]/td[1]/div/span/a"
    url = extract_pdf_url_from_xpath(driver, WEBLOAD_TIMEOUT, xpath)
    if url:
        text_key = el_sb[-1].text.replace('\n', '').strip()
        pdf[text_key] = url

    # Extract sales brochure notes
    try:
        div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda d: d.find_elements("xpath", "//*[@id='brochure']/div[2]/div")
        )
        note_texts = [elem.text for elem in div_elements if elem.text]
        if note_texts:
            devm['sb_note'] = "\n".join([devm.get('sb_note', "")] + note_texts)
    except Exception:
        try:
            devm['sb_note'] = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda d: d.find_element("xpath", "//*[@id='brochure']/div[2]")
            ).text
        except Exception:
            update_log(docs, "Sales Brochure N/A\n")
