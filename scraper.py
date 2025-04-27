"""
This script scrapes company data from a provider website and saves it in raw JSON format.
"""

import os
import re
import time
import logging

import json
from random import randint

import pandas as pd

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COMPANY_INFO_WEBSITE_URL = os.environ.get("COMPANY_INFO_WEBSITE_URL", None)

LOGGER = logging.getLogger(__name__)


def close_ad_popup(driver: webdriver.Chrome):
    try:
        WebDriverWait(driver=driver, timeout=5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close"))
        ).click()
    except Exception as e:
        LOGGER.error(e)


def close_cookie_popup(driver: webdriver.Chrome):
    try:
        WebDriverWait(driver=driver, timeout=5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
    except Exception as e:
        LOGGER.error(e)


def get_company_details(company_id: str):
    driver = webdriver.Chrome()
    driver.get(url=COMPANY_INFO_WEBSITE_URL)

    close_cookie_popup(driver)
    close_ad_popup(driver)

    elem = driver.find_element("id", "search-input")
    elem.click()
    elem.send_keys(company_id)
    elem.send_keys(Keys.ENTER)

    links = driver.find_elements(By.TAG_NAME, "a")
    company_link = None
    for link in links:
        href = link.get_attribute("href")
        if href and re.search(r"/\d{7}$", href):
            company_link = href

    if company_link:
        driver.get(company_link)

        close_cookie_popup(driver)
        close_ad_popup(driver)

        script = driver.find_element(By.ID, "__NEXT_DATA__")
        next_data_json = script.get_attribute("innerHTML")

        next_data = json.loads(next_data_json)
        output_path = os.path.join("data", "scraped_raw_jsons", f"{company_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(next_data, f, ensure_ascii=False, indent=2)
    else:
        LOGGER.warning(f"Company link not found for {company_id}")

    driver.close()
    driver.quit()


def main():
    if not COMPANY_INFO_WEBSITE_URL:
        raise ValueError("COMPANY_INFO_URL environment variable is not set.")

    company_list_path = os.path.join(
        "data", "startup100", "startup100_company_details.csv"
    )
    company_list_df = pd.read_csv(
        filepath_or_buffer=company_list_path, low_memory=False
    )
    company_list_df = company_list_df[
        company_list_df["business_id"].notna()
    ].reset_index(drop=True)

    for index, row in company_list_df.iterrows():
        company_id = row["business_id"]
        get_company_details(company_id=company_id)
        time.sleep(randint(1, 3))


if __name__ == "__main__":
    main()
