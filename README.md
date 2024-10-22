# Stock Analysis Platform

## Giới thiệu
Stock Analysis Platform là một ứng dụng web được thiết kế để cung cấp các công cụ toàn diện để phân tích dữ liệu thị trường chứng khoán. Dự án sử dụng Django cho backend và Argon Dashboard Django template cho giao diện người dùng.

## Yêu cầu hệ thống
- Python 3.8+
- pip (Python package manager)
- Git

## Cài đặt

1. Clone repository:   ```
   git clone https://github.com/your-username/stock-analysis-platform.git
   cd stock-analysis-platform   ```

2. Tạo và kích hoạt môi trường ảo:   ```
   python -m venv venv
   source venv/bin/activate  # Trên Windows sử dụng: venv\Scripts\activate   ```

3. Cài đặt các dependency:   ```
   pip install -r requirements.txt   ```

4. Thực hiện migrations:   ```
   python manage.py makemigrations
   python manage.py migrate   ```

5. Tạo superuser:   ```
   python manage.py createsuperuser   ```

## Chạy ứng dụng

1. Khởi động Django server:   ```
   python manage.py runserver   ```

2. Truy cập ứng dụng tại `http://127.0.0.1:8000`

## Sử dụng ứng dụng

1. Đăng nhập với tài khoản superuser đã tạo.

2. Truy cập trang Stock Analysis từ sidebar để xem danh sách cổ phiếu.

3. Nhấp vào "View Details" để xem chi tiết về một cổ phiếu cụ thể.

4. Sử dụng trang Stock Dashboard để có cái nhìn tổng quan về phân tích cổ phiếu.

## Cập nhật dữ liệu cổ phiếu

Để cập nhật dữ liệu cổ phiếu từ web, sử dụng lệnh sau:
