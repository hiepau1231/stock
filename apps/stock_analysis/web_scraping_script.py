from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options 

from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time

import pandas as pd

from io import StringIO

from datetime import datetime

from .models import Stock, StockPrice

import logging
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





def scrape_stock_data(symbol):

    chrome_driver_path = 'path/to/chromedriver'  # Cập nhật đường dẫn tới chromedriver



    chrome_options = Options()

    chrome_options.add_argument("--headless")

    chrome_options.add_argument("--disable-gpu")

    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--disable-dev-shm-usage")



    service = Service(executable_path=chrome_driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)



    try:

        url = f'https://s.cafef.vn/Lich-su-giao-dich-{symbol}-1.chn'
        driver.get(url)
        logger.info(f"Accessing URL: {url}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentMainData"))
        )

        all_dataframes = []
        page_count = 0
        max_pages = 5  # Giới hạn số trang để tránh quá tải



        while page_count < max_pages:

            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find('table', {'id': 'GirdTable2'})



            if table:

                table_html = str(table)

                df = pd.read_html(StringIO(table_html))[0]

                df.columns = ['Ngày', 'Giá đóng cửa', 'Thay đổi', 'Khối lượng', 'Giá mở cửa', 'Giá cao nhất', 'Giá thấp nhất']

                df['Ngày'] = pd.to_datetime(df['Ngày'], format='%d/%m/%Y')

                all_dataframes.append(df)

                logger.info(f"Data scraped from page {page_count + 1}")



                next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging') and contains(text(), '>')]")
                if 'disabled' in next_button.get_attribute('class'):
                    break
                next_button.click()
                time.sleep(1)
                page_count += 1

            else:

                logger.warning("Table not found on the page.")

                break



        if all_dataframes:

            final_df = pd.concat(all_dataframes, ignore_index=True)

            stock, created = Stock.objects.get_or_create(symbol=symbol)
            
            for _, row in final_df.iterrows():
                StockPrice.objects.update_or_create(
                    stock=stock,
                    date=row['Ngày'],
                    defaults={
                        'open_price': row['Giá mở cửa'],
                        'high_price': row['Giá cao nhất'],
                        'low_price': row['Giá thấp nhất'],
                        'close_price': row['Giá đóng cửa'],
                        'volume': row['Khối lượng'],
                    }
                )
            logger.info(f"Data saved for {symbol}")

        else:

            logger.warning(f"No data scraped for {symbol}")



    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Error scraping data for {symbol}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {symbol}: {str(e)}")
    finally:
        driver.quit()



