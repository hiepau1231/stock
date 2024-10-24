import requests
# xóa 2 dòng này nếu không cần async
# import asyncio
# import nest_asyncio
from requests.exceptions import RequestException
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
from .models import Stock, StockPrice, StockIndex, HistoricalData
import logging
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from django.utils import timezone
from time import sleep

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_driver():
    """
    Khởi tạo và trả về Chrome WebDriver
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Sử dụng ChromeDriverManager để tự động tải và quản lý chromedriver
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error initializing Chrome WebDriver: {str(e)}")
        return None

def scrape_index_data():
    """
    Scrape dữ liệu chỉ số từ TCBS, SSI, VNDIRECT và chỉ số ngành
    """
    logger.info("Starting index scraping...")
    driver = get_chrome_driver()
    if not driver:
        return False

    try:
        # 1. Scrape chỉ số từ TCBS
        driver.get("https://tcbs.com.vn/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "market-index"))
        )

        # Dictionary ánh xạ class index với tên chỉ số
        index_mapping = {
            "vnindex": "VN-Index",
            "hnxindex": "HNX-Index",
            "upcomindex": "UPCOM-Index"
        }

        # Scrape chỉ số cơ bản
        for index_class, index_name in index_mapping.items():
            try:
                index_element = driver.find_element(By.CLASS_NAME, index_class)
                value = float(index_element.find_element(
                    By.CLASS_NAME, "index-point").text.replace(',', ''))
                change_text = index_element.find_element(
                    By.CLASS_NAME, "index-change").text.strip('%')
                change = float(change_text)

                StockIndex.objects.update_or_create(
                    name=index_name,
                    defaults={
                        'value': value,
                        'change': change,
                        'last_updated': timezone.now()
                    }
                )
                logger.info(f"Updated {index_name}: value={value}, change={change}%")

            except Exception as e:
                logger.error(f"Error updating {index_name}: {str(e)}")
                continue

        # 2. Scrape chỉ số VN30 và HNX30 từ SSI
        driver.get("https://iboard.ssi.com.vn/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "index-list"))
        )

        additional_indices = {
            "vn30": "VN30",
            "hnx30": "HNX30"
        }

        for index_class, index_name in additional_indices.items():
            try:
                index_element = driver.find_element(By.CLASS_NAME, index_class)
                value_element = index_element.find_element(By.CLASS_NAME, "index-value")
                value = float(value_element.text.replace(',', ''))
                change_element = index_element.find_element(By.CLASS_NAME, "index-change")
                change = float(change_element.text.strip('%'))

                StockIndex.objects.update_or_create(
                    name=index_name,
                    defaults={
                        'value': value,
                        'change': change,
                        'last_updated': timezone.now()
                    }
                )
                logger.info(f"Updated {index_name}: value={value}, change={change}%")

            except Exception as e:
                logger.error(f"Error updating {index_name}: {str(e)}")
                continue

        # 3. Scrape VNMid và VNSmall từ VNDIRECT
        driver.get("https://dstock.vndirect.com.vn/thi-truong-chung-khoan/chi-so")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "market-index-item"))
        )

        vnmid_small_indices = {
            "vnmid": "VNMID",
            "vnsml": "VNSMALL"
        }

        for index_class, index_name in vnmid_small_indices.items():
            try:
                index_element = driver.find_element(By.CLASS_NAME, index_class)
                value = float(index_element.find_element(
                    By.CLASS_NAME, "current-value").text.replace(',', ''))
                change_element = index_element.find_element(By.CLASS_NAME, "change-value")
                change = float(change_element.text.strip('%'))

                StockIndex.objects.update_or_create(
                    name=index_name,
                    defaults={
                        'value': value,
                        'change': change,
                        'last_updated': timezone.now()
                    }
                )
                logger.info(f"Updated {index_name}: value={value}, change={change}%")

            except NoSuchElementException:
                logger.error(f"Could not find elements for {index_name}")
                continue
            except ValueError as e:
                logger.error(f"Error parsing values for {index_name}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error updating {index_name}: {str(e)}")
                continue

        # 4. Scrape chỉ số ngành từ TCBS
        driver.get("https://tcbs.com.vn/vi_VN/industry")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "industry-index"))
        )

        # Dictionary cho các chỉ số ngành chính
        industry_indices = {
            "bank": "Ngân hàng",
            "securities": "Chứng khoán",
            "real-estate": "Bất động sản",
            "oil-gas": "Dầu khí",
            "steel": "Thép",
            "retail": "Bán lẻ",
            "insurance": "Bảo hiểm",
            "technology": "Công nghệ",
            "construction": "Xây dựng",
            "logistics": "Logistics"
        }

        for index_class, index_name in industry_indices.items():
            try:
                # Tìm phần tử chứa thông tin chỉ số ngành
                industry_element = driver.find_element(By.CLASS_NAME, f"industry-{index_class}")
                
                # Lấy giá trị chỉ số
                value = float(industry_element.find_element(
                    By.CLASS_NAME, "industry-value").text.replace(',', ''))
                
                # Lấy phần trăm thay đổi
                change_element = industry_element.find_element(By.CLASS_NAME, "industry-change")
                change = float(change_element.text.strip('%'))

                # Cập nhật hoặc tạo mới trong database
                StockIndex.objects.update_or_create(
                    name=f"IDX-{index_name}",  # Thêm tiền tố để phân biệt với chỉ số thông thường
                    defaults={
                        'value': value,
                        'change': change,
                        'last_updated': timezone.now()
                    }
                )
                logger.info(f"Updated industry index {index_name}: value={value}, change={change}%")

            except NoSuchElementException:
                logger.error(f"Could not find elements for industry {index_name}")
                continue
            except ValueError as e:
                logger.error(f"Error parsing values for industry {index_name}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error updating industry {index_name}: {str(e)}")
                continue

        # 5. Scrape thêm thông tin chi tiết cho mỗi ngành
        for index_class, index_name in industry_indices.items():
            try:
                # Click vào ngành để xem chi tiết
                industry_element = driver.find_element(By.CLASS_NAME, f"industry-{index_class}")
                industry_element.click()
                
                # Chờ dữ liệu chi tiết được load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "industry-detail"))
                )

                # Lấy thông tin về vốn hóa và P/E ngành
                market_cap = float(driver.find_element(
                    By.CLASS_NAME, "market-cap").text.replace(',', ''))
                pe_ratio = float(driver.find_element(
                    By.CLASS_NAME, "pe-ratio").text)

                # Lưu thông tin bổ sung vào database
                StockIndex.objects.update_or_create(
                    name=f"IDX-{index_name}-PE",
                    defaults={
                        'value': pe_ratio,
                        'change': 0,  # PE không có % thay đổi
                        'last_updated': timezone.now()
                    }
                )

                logger.info(f"Updated detailed info for {index_name}: PE={pe_ratio}")

            except Exception as e:
                logger.error(f"Error updating detailed info for industry {index_name}: {str(e)}")
                continue

        logger.info("All index and industry data updated successfully")
        return True

    except Exception as e:
        logger.error(f"Error scraping index and industry data: {str(e)}")
        return False
    finally:
        driver.quit()

def scrape_stock_data(symbol):
    """
    Scrape dữ liệu chi tiết của một mã cổ phiếu từ TCBS
    """
    logger.info(f"Starting to scrape data for {symbol}")
    driver = get_chrome_driver()
    if not driver:
        return False

    try:
        # Truy cập trang chi tiết cổ phiếu trên TCBS
        url = f'https://tcinvest.tcbs.com.vn/tc-price/tc-analysis/{symbol}'
        driver.get(url)
        logger.info(f"Accessing URL: {url}")

        # Chờ cho bảng dữ liệu được load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stock-price-info"))
        )

        # Lấy thông tin giá hiện tại
        try:
            price_info = driver.find_element(By.CLASS_NAME, "stock-price-info")
            current_price = float(price_info.find_element(
                By.CLASS_NAME, "current-price").text.replace(',', ''))
            
            # Lấy thông tin khối lượng giao dịch
            volume = int(price_info.find_element(
                By.CLASS_NAME, "volume").text.replace(',', ''))
            
            # Lấy giá cao nhất, thấp nhất trong ngày
            price_range = price_info.find_elements(By.CLASS_NAME, "price-range")
            high_price = float(price_range[0].text.replace(',', ''))
            low_price = float(price_range[1].text.replace(',', ''))
            
            # Lấy giá mở cửa
            open_price = float(price_info.find_element(
                By.CLASS_NAME, "open-price").text.replace(',', ''))

            # Lưu dữ liệu vào database
            stock = Stock.objects.get(symbol=symbol)
            today = timezone.now().date()

            StockPrice.objects.update_or_create(
                stock=stock,
                date=today,
                defaults={
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'close_price': current_price,
                    'volume': volume
                }
            )

            # Lấy dữ liệu lịch sử
            driver.find_element(By.ID, "historical-data-tab").click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "historical-data-table"))
            )

            # Parse bảng dữ liệu lịch sử
            table = driver.find_element(By.CLASS_NAME, "historical-data-table")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Bỏ qua header

            for row in rows[:30]:  # Lấy 30 ngày gần nhất
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    date_str = cols[0].text
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    
                    HistoricalData.objects.update_or_create(
                        stock=stock,
                        date=date,
                        defaults={
                            'open_price': float(cols[1].text.replace(',', '')),
                            'high_price': float(cols[2].text.replace(',', '')),
                            'low_price': float(cols[3].text.replace(',', '')),
                            'close_price': float(cols[4].text.replace(',', '')),
                            'volume': int(cols[5].text.replace(',', ''))
                        }
                    )

            logger.info(f"Successfully updated data for {symbol}")
            return True

        except NoSuchElementException as e:
            logger.error(f"Could not find element for {symbol}: {str(e)}")
            return False
        except ValueError as e:
            logger.error(f"Error parsing values for {symbol}: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"Error scraping data for {symbol}: {str(e)}")
        return False
    finally:
        driver.quit()

def run_scraping():
    """
    Chạy toàn bộ quá trình scraping
    """
    logger.info("Starting full scraping process...")
    try:
        # Cập nhật chỉ số
        if not scrape_index_data():
            logger.error("Failed to update index data")
            return False

        # Cập nhật dữ liệu cổ phiếu
        stocks = Stock.objects.all()
        for stock in stocks:
            if not scrape_stock_data(stock.symbol):
                logger.warning(f"Failed to update data for {stock.symbol}")
                continue
            time.sleep(1)  # Tránh request quá nhanh

        logger.info("Full scraping process completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error in run_scraping: {str(e)}")
        return False
