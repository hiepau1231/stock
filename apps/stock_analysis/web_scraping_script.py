import requests  # Thêm dòng này vào đầu file

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





def scrape_index_data():
    """Scrape data for HNX and UPCOM indices"""
    try:
        # URL cho trang chính của CafeF
        url = "https://s.cafef.vn/bao-cao-vi-mo-thi-truong.chn"
        
        logger.info(f"Sending request to {url}")
        soup = get_soup(url)
        
        indices_data = {
            'HNXINDEX': {'name': 'HNX Index', 'selector': '#HNX-Index .box-price span'},
            'UPCOM': {'name': 'UPCOM Index', 'selector': '#UPCOM-Index .box-price span'}
        }
        
        success = False
        for index_code, data in indices_data.items():
            try:
                # Tìm phần tử chứa giá
                price_element = soup.select_one(data['selector'])
                if price_element:
                    price_text = price_element.text.strip()
                    # Chuyển đổi chuỗi giá thành số
                    price = float(price_text.replace(',', ''))
                    
                    # Tìm phần tử chứa thay đổi giá
                    change_element = soup.select_one(f"{data['selector']}:nth-child(2)")
                    change = 0
                    if change_element:
                        change_text = change_element.text.strip()
                        try:
                            change = float(change_text.replace('+', '').replace(',', ''))
                        except ValueError:
                            logger.warning(f"Could not parse change value for {index_code}")
                    
                    stock, created = Stock.objects.get_or_create(
                        symbol=index_code,
                        defaults={'name': data['name']}
                    )
                    
                    # Tạo bản ghi giá mới
                    StockPrice.objects.create(
                        stock=stock,
                        date=datetime.now().date(),
                        open_price=price - change,
                        close_price=price,
                        high_price=max(price, price - change),
                        low_price=min(price, price - change),
                        volume=0
                    )
                    
                    logger.info(f"Successfully saved data for {index_code}: Price={price}, Change={change}")
                    success = True
                else:
                    logger.warning(f"Price element not found for {index_code}")
            except Exception as e:
                logger.error(f"Error processing {index_code}: {str(e)}")
                continue
        
        return success
    
    except Exception as e:
        logger.error(f"Error in scrape_index_data: {str(e)}")
        return False

def get_soup(url, retries=3, delay=1):
    """Get BeautifulSoup object with retry logic"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

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
