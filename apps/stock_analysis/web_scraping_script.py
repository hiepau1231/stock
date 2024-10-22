from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
from io import StringIO
from datetime import datetime
from .models import Stock, StockPrice

def scrape_stock_data(symbol):
    chrome_driver_path = 'path/to/chromedriver'  # Cập nhật đường dẫn tới chromedriver

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(f'https://s.cafef.vn/lich-su-giao-dich-{symbol}-1.chn')

        search_box = driver.find_element(By.ID, 'ContentPlaceHolder1_ctl00_acp_inp_disclosure')
        search_box.send_keys(symbol)
        search_box.send_keys(Keys.ENTER)

        time.sleep(0.25)

        all_dataframes = []
        page_count = 0
        max_pages = 5  # Giới hạn số trang để tránh quá tải

        while page_count < max_pages:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'owner-contents-table'})

            if table:
                table_html = str(table)
                df = pd.read_html(StringIO(table_html), header=1)[0]
                df['Ngày'] = pd.to_datetime(df['Ngày'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
                df['Thay đổi'] = df['Thay đổi'].astype(str)
                
                for column in ['Đóng cửa', 'Điều chỉnh', 'Khối lượng', 'Giá trị (tỷ VNĐ)', 'Khối lượng.1', 'Giá trị (tỷ VNĐ).1', 'Mở cửa', 'Cao nhất', 'Thấp nhất']:
                    df[column] = pd.to_numeric(df[column].replace('--', None), errors='coerce')
                
                all_dataframes.append(df)
                print(f"Lấy dữ liệu từ trang {page_count + 1}")

                try:
                    next_button = driver.find_element(By.XPATH, '//div[@onclick="ownerCDL.handleChangePage(ownerCDL.pageIndex + 1)"]')
                    next_button.click()
                    time.sleep(0.1)
                    page_count += 1
                except Exception as e:
                    print(f"Không tìm thấy nút Next hoặc đã đến trang cuối cùng. Lỗi: {e}")
                    break
            else:
                print("Không tìm thấy bảng trên trang.")
                break

        final_df = pd.concat(all_dataframes, ignore_index=True)

        now = datetime.now()
        if now.hour < 15:
            final_df = final_df.drop(0).reset_index(drop=True)
            print("Đã xóa hàng đầu tiên vì thời gian hiện tại trước 15:00")

        stock, created = Stock.objects.get_or_create(symbol=symbol)
        
        for _, row in final_df.iterrows():
            StockPrice.objects.update_or_create(
                stock=stock,
                date=row['Ngày'],
                defaults={
                    'open_price': row['Mở cửa'],
                    'high_price': row['Cao nhất'],
                    'low_price': row['Thấp nhất'],
                    'close_price': row['Đóng cửa'],
                    'volume': row['Khối lượng'],
                }
            )

        print(f"Đã lưu dữ liệu cho {symbol}")

    finally:
        driver.quit()
