# Stock Analysis Platform

Nền tảng phân tích chứng khoán sử dụng Django

## Tính năng

### Đã hoàn thành
- Hiển thị dữ liệu thị trường realtime
- Biểu đồ Candlestick và các chỉ báo kỹ thuật (RSI, MACD, Bollinger Bands)
- Quản lý danh mục đầu tư cơ bản
- Danh sách theo dõi cổ phiếu
- Giao diện responsive
- Tối ưu hiệu suất với caching
- Cập nhật dữ liệu tự động

## Cài đặt

1. Clone repository và cài đặt môi trường:
```
git clone <repository-url>
cd stock-analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Cấu hình database:
```
python manage.py migrate
python manage.py createsuperuser
```

3. Chạy server:
```
python manage.py runserver
```

## Cập nhật dữ liệu tự động

### Phương pháp 1: Sử dụng Management Command
1. Chạy trực tiếp command:
```bash
python manage.py auto_update_data
```
Command này sẽ tự động cập nhật dữ liệu mỗi giờ và tự động khởi động lại nếu có lỗi.

### Phương pháp 2: Sử dụng Windows Task Scheduler
1. Tạo file batch (update_stock_data.bat):
```batch
@echo off
cd /d D:\path\to\your\project
call venv\Scripts\activate
python manage.py auto_update_data
```

2. Cấu hình Task Scheduler:
- Mở Windows Task Scheduler
- Tạo Task mới
- Trigger: Daily hoặc At startup
- Action: Start program -> Chọn file update_stock_data.bat

### Phương pháp 3: Sử dụng Celery (Nâng cao)
1. Cài đặt Redis và Celery:
```bash
pip install celery redis
```

2. Chạy Celery worker:
```bash
celery -A core worker -l info
```

3. Chạy Celery beat:
```bash
celery -A core beat -l info
```

## Cấu trúc thư mục

```
stock-analysis/
├── apps/
│   └── stock_analysis/     # Ứng dụng chính
├── core/                   # Cấu hình Django
├── templates/             # Giao diện
└── cline_docs/           # Tài liệu
```

## API

- /api/stock/<symbol>/ - Thông tin cổ phiếu
- /api/stock/<symbol>/indicators/ - Chỉ báo kỹ thuật
- /api/stock/<symbol>/historical/ - Dữ liệu lịch sử

## Công nghệ sử dụng

- Django 5.0.2
- PostgreSQL
- yfinance API
- Plotly
- Pandas
- Celery (tùy chọn)
- Redis (tùy chọn)

## Lưu ý

- Dữ liệu được cập nhật tự động mỗi giờ
- Có thể điều chỉnh thời gian cập nhật trong file auto_update_data.py
- Nên sử dụng caching để giảm tải cho server
- Theo dõi log để phát hiện lỗi khi cập nhật dữ liệu

## Liên hệ

Email: example@email.com
GitHub: github.com/username

## License

MIT License
