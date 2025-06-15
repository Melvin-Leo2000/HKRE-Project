from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from devm_versions import update_log

def sales_brochure(WEBLOAD_TIMEOUT, docs, devm, el_sb, driver, pdf):
    devm['sb1_date'] = pd.to_datetime(el_sb[0].text[-11:]).strftime('%d %b %Y')
    devm['sbe_date'] = pd.to_datetime(el_sb[1].text[-11:]).strftime('%d %b %Y')

    for r in range(2, len(el_sb) - 1):
        devm[f'sb{r - 1}_text'] = el_sb[r].text

        url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda driver: driver.find_element(
                "xpath", f"//*[@id='brochure']/div[2]/table/tbody/tr[{r + 1}]/td[1]/div/span/a"
            )
        ).get_attribute("href")

        # Getting the pdf size 
        filename = f"{url.split('/')[-1][:-4]}.PDF"
        
        # saving the name and url in the pdf dictionary
        pdf[filename] = url
        

    devm['sbe_text'] = el_sb[-1].text
    url = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
        lambda driver: driver.find_element(
            "xpath", f"//*[@id='brochure']/div[2]/table/tbody/tr[{len(el_sb)}]/td[1]/div/span/a"
        )
    ).get_attribute("href")

    filename = f"{url.split('/')[-1][:-4]}.PDF"
    pdf[filename] = url


    # Sales Brochure
    try:

        div_elements = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
            lambda driver: driver.find_elements("xpath", "//*[@id='brochure']/div[2]/div")
        )
        devm['sb_note'] = "\n".join([devm.get('sb_note', "")] + [elem.text for elem in div_elements if elem.text])
    except Exception:
        update_log(docs, "sb_note N/A\n")

        try:
            devm['sb_note'] = WebDriverWait(driver, WEBLOAD_TIMEOUT).until(
                lambda driver: driver.find_element("xpath", "//*[@id='brochure']/div[2]")
            ).text
        except Exception:
            update_log(docs, "Sales Brochure N/A\n")

