from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from io import StringIO
from datetime import datetime
import psycopg2
import sys
import io

# Thiết lập encoding cho stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cấu hình đường dẫn đến ChromeDriver
chrome_driver_path = 'C:/Users/Mr Duong/chromedriver-win64/chromedriver.exe'

# Khởi tạo tùy chọn cho Chrome (bao gồm cả chế độ headless)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Bật chế độ headless
chrome_options.add_argument("--disable-dev-shm-usage")  # Tùy chọn để tối ưu khi chạy headless

# Khởi tạo Service và WebDriver với tùy chọn headless

# Khởi tạo Service và WebDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Cấu hình kết nối PostgreSQL
conn = psycopg2.connect(
    dbname='stock_web', 
    user='postgres', 
    password='09062023', 
    host='localhost', 
    port='5432'
)
cur = conn.cursor()
ticker = 'VNINDEX'
try:
    
    driver.get(f'https://s.cafef.vn/lich-su-giao-dich-{ticker}-1.chn')

    search_box = driver.find_element(By.ID, 'ContentPlaceHolder1_ctl00_acp_inp_disclosure')
    search_box.send_keys(ticker)
    search_box.send_keys(Keys.ENTER)

    time.sleep(0.25)

    all_dataframes = []
    page_count = 0
    max_pages = 100

    while page_count < max_pages:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'id': 'owner-contents-table'})

        if table:
            table_html = str(table)
            df = pd.read_html(StringIO(table_html), header=1)[0]
            df['Ngày'] = pd.to_datetime(df['Ngày'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
            # Giữ nguyên định dạng của cột 'Thay đổi'
            df['Thay đổi'] = df['Thay đổi'].astype(str)
            
            # Xử lý dữ liệu không hợp lệ
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

    for index, row in final_df.iterrows():
        ticker = ticker
        sql = f"""
        INSERT INTO {ticker} (ngay, dong_cua, dieu_chinh, thay_doi, khoi_luong, gia_tri, khoi_luong1, gia_tri1, mo_cua, cao_nhat, thap_nhat)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            row['Ngày'], row['Đóng cửa'], row['Điều chỉnh'], row['Thay đổi'], row['Khối lượng'], row['Giá trị (tỷ VNĐ)'],
            row['Khối lượng.1'], row['Giá trị (tỷ VNĐ).1'], row['Mở cửa'], row['Cao nhất'], row['Thấp nhất']
        ))

    conn.commit()
    print("Đã lưu dữ liệu vào PostgreSQL và đóng kết nối")

finally:
    cur.close()
    conn.close()
    driver.quit()
