# Stock Analysis Platform

## Giới thiệu
Stock Analysis Platform là một ứng dụng web được thiết kế để cung cấp các công cụ toàn diện để phân tích dữ liệu thị trường chứng khoán. Dự án sử dụng Django cho backend, Node.js cho xử lý dữ liệu thời gian thực, và Argon Dashboard Django template cho giao diện người dùng.

## Yêu cầu hệ thống
- Python 3.8+
- Node.js 14+
- PostgreSQL

## Cài đặt

1. Clone repository:   ```
   git clone https://github.com/your-username/stock-analysis-platform.git
   cd stock-analysis-platform   ```

2. Tạo và kích hoạt môi trường ảo:   ```
   python -m venv venv
   source venv/bin/activate  # Trên Windows sử dụng: venv\Scripts\activate   ```

3. Cài đặt các dependency Python:   ```
   pip install -r requirements.txt   ```

4. Cài đặt các dependency Node.js:   ```
   npm install   ```

5. Cấu hình cơ sở dữ liệu:
   - Tạo một cơ sở dữ liệu PostgreSQL mới
   - Cập nhật thông tin kết nối trong file `stock_analysis_project/settings.py`

6. Thực hiện migrations:   ```
   python manage.py migrate   ```

7. Tạo superuser:   ```
   python manage.py createsuperuser   ```

## Chạy ứng dụng

1. Khởi động Django server:   ```
   python manage.py runserver   ```

2. Trong một terminal khác, khởi động Node.js server cho xử lý real-time:   ```
   node real_time_server.js   ```

3. Truy cập ứng dụng tại `http://localhost:8000`

## Cấu trúc dự án
