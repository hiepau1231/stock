# Stock Analysis Platform

Đây là một ứng dụng web phân tích chứng khoán sử dụng Django, Node.js và Argon Dashboard Django template.

## Yêu cầu hệ thống

- Python 3.8+
- Node.js 14+
- pip
- virtualenv (khuyến nghị)

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

5. Tạo file .env trong thư mục gốc và cấu hình các biến môi trường cần thiết:   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3   ```

6. Thực hiện migrations:   ```
   python manage.py makemigrations
   python manage.py migrate   ```

7. Tạo superuser:   ```
   python manage.py createsuperuser   ```

8. Chạy lệnh để crawl dữ liệu chứng khoán:   ```
   python manage.py scrape_stock_data   ```

## Chạy ứng dụng

1. Khởi động Django server:   ```
   python manage.py runserver   ```

2. Mở trình duyệt và truy cập http://localhost:8000

## Cấu trúc dự án

- `manage.py`: Django's command-line utility cho các tác vụ quản trị.
- `core/`: Cài đặt và cấu hình cốt lõi của Django project.
- `apps/`: Chứa tất cả các Django apps.
  - `stock_analysis/`: App chính cho phân tích chứng khoán.
    - `models.py`: Định nghĩa các model dữ liệu.
    - `views.py`: Xử lý logic cho các view.
    - `services/`: Chứa các service classes.
    - `management/commands/`: Chứa các custom management commands.
- `templates/`: Chứa các template HTML.
- `static/`: Chứa các file tĩnh (CSS, JavaScript, images).
- `requirements.txt`: Liệt kê các dependency Python.
- `package.json`: Liệt kê các dependency Node.js.

## Tính năng chính

- Xem tổng quan thị trường
- Tra cứu thông tin cổ phiếu
- Xem biểu đồ giá cổ phiếu
- Phân tích kỹ thuật cơ bản
- Quản lý danh mục đầu tư

## Đóng góp

Nếu bạn muốn đóng góp cho dự án, vui lòng tạo pull request hoặc báo cáo issues trên GitHub.

## Giấy phép

[MIT License](LICENSE)
