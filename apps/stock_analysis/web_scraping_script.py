import requests  # Thêm dòng này vào đầu file
from requests.exceptions import RequestException  # Thêm dòng này

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

from .models import Stock, StockPrice, StockIndex

import logging
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from django.utils import timezone
from time import sleep

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





def scrape_index_data():
    """Fetch data for VN-Index, HNX-Index, and UPCOM-Index"""
    try:
        data = get_index_data()
        if not data or 'data' not in data:
            logger.warning("No index data received from API")
            return False
        
        success = False
        for index in data['data']:
            try:
                name = index['code']
                price = float(index['price'])
                change = float(index['change'])
                
                stock_index, created = StockIndex.objects.update_or_create(
                    name=name,
                    defaults={
                        'value': price,
                        'change': change,
                        'last_updated': timezone.now()
                    }
                )
                
                logger.info(f"Successfully saved data for {name}: Price={price}, Change={change}")
                success = True
            except Exception as e:
                logger.error(f"Error processing index {name}: {str(e)}")
                continue
        
        if not success:
            logger.warning("No index data was successfully processed")
        
        return success
    
    except Exception as e:
        logger.error(f"Unexpected error in scrape_index_data: {str(e)}")
        return False

def get_index_data():
    url = "https://finfo-api.vndirect.com.vn/v4/change_prices?q=code:VNINDEX,HNX,UPCOM"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error fetching index data: {str(e)}")
        return None

def scrape_stock_data(symbol):
    """Scrape data for individual stocks"""
    try:
        url = f"https://s.cafef.vn/Lich-su-giao-dich-{symbol}-1.chn"
        soup = get_soup(url)
        
        # Tìm bảng dữ liệu
        table = soup.find('table', {'id': 'GirdTable2'})
        if table:
            # Xử lý dữ liệu từ bảng
            rows = table.find_all('tr')[1:]  # Bỏ qua hàng tiêu đề
            
            if rows:
                stock, created = Stock.objects.get_or_create(symbol=symbol)
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 7:
                        try:
                            date_str = cols[0].text.strip()
                            date = datetime.strptime(date_str, '%d/%m/%Y').date()
                            
                            StockPrice.objects.update_or_create(
                                stock=stock,
                                date=date,
                                defaults={
                                    'close_price': float(cols[1].text.replace(',', '')),
                                    'open_price': float(cols[4].text.replace(',', '')),
                                    'high_price': float(cols[5].text.replace(',', '')),
                                    'low_price': float(cols[6].text.replace(',', '')),
                                    'volume': int(cols[3].text.replace(',', ''))
                                }
                            )
                        except (ValueError, IndexError) as e:
                            logger.error(f"Error parsing row data: {str(e)}")
                            continue
                
                logger.info(f"Successfully scraped and saved data for {symbol}")
                return True
            
        logger.warning(f"No data found for {symbol}")
        return False
        
    except Exception as e:
        logger.error(f"Error scraping stock {symbol}: {str(e)}")
        return False

def scrape_stock_data():
    url = "https://finance.vietstock.vn/"  # Cập nhật URL chính xác
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Tìm và trích xuất dữ liệu cho VN-Index
            vn_index = soup.find('div', {'id': 'price-box-1'})
            if vn_index:
                vn_index_value = vn_index.find('span', class_='price').text.strip()
                vn_index_change = vn_index.find('span', class_='change').text.strip()
                
                # Cập nhật hoặc tạo mới đối tượng StockIndex
                stock_index, created = StockIndex.objects.update_or_create(
                    name="VN-Index",
                    defaults={
                        'value': float(vn_index_value.replace(',', '')),
                        'change': float(vn_index_change.replace(',', '')),
                        'last_updated': timezone.now()
                    }
                )
                logger.info(f"{'Created' if created else 'Updated'} VN-Index: {vn_index_value}")

            # Tương tự cho HNX-Index và UPCOM-Index
            # ...

            return True  # Scraping thành công
        except RequestException as e:
            logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Scraping failed.")
                return False
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return False
