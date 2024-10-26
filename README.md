# Stock Analysis Platform

Nền tảng phân tích chứng khoán sử dụng Django và yfinance API.

## TÍNH NĂNG

### Đã hoàn thành
- ✅ Hiển thị dữ liệu thị trường realtime
- ✅ Biểu đồ Candlestick và các chỉ báo kỹ thuật (RSI, MACD, Bollinger Bands)
- ✅ Quản lý danh mục đầu tư
- ✅ Danh sách theo dõi cổ phiếu
- ✅ Giao diện responsive
- ✅ Tối ưu hiệu suất với caching
- ✅ Cập nhật dữ liệu tự động
- ✅ Khuyến nghị đầu tư dựa trên phân tích kỹ thuật
- ✅ Phân tích rủi ro danh mục
- ✅ Xuất báo cáo PDF/Excel
- ✅ Cảnh báo giá

### Đang phát triển
- 🔄 Phân tích ngành
- 🔄 Dự đoán VNINDEX
- 🔄 Phân tích và dự đoán từng mã

## CÀI ĐẶT

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

3. Thu thập static files:
```
python manage.py collectstatic
```

4. Chạy server:
```
python manage.py runserver
```

## CẬP NHẬT DỮ LIỆU

### Phương pháp 1: Sử dụng Management Command
1. Chạy trực tiếp command:
```bash
python manage.py auto_update_data
```

### Phương pháp 2: Sử dụng Windows Task Scheduler
1. Tạo file batch (update_stock_data.bat):
```batch
@echo off
cd /d D:\path\to\your\project
call venv\Scripts\activate
python manage.py auto_update_data
```

2. Cấu hình Task Scheduler để chạy file batch định kỳ

### Phương pháp 3: Sử dụng Celery
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

## KIỂM TRA DỮ LIỆU

Truy cập http://localhost:8000/stock/check-data/ để xem:
- Thống kê tổng quan
- Dữ liệu cổ phiếu gần đây
- Lịch sử giá gần đây
- Thời gian cập nhật cuối

## CẤU TRÚC THƯ MỤC

```
stock/
├── apps/                   # Chứa các ứng dụng Django
├── core/                   # Cấu hình Django
├── cline_docs/            # Tài liệu dự án
└── staticfiles/           # Static files
```

## API

- /api/stock/<symbol>/ - Thông tin cổ phiếu
- /api/stock/<symbol>/indicators/ - Chỉ báo kỹ thuật
- /api/stock/<symbol>/historical/ - Dữ liệu lịch sử
- /api/industry/<id>/ - Phân tích ngành

## CÔNG NGHỆ SỬ DỤNG

- Django 5.0.2
- SQLite
- yfinance API
- Plotly
- Pandas
- Celery (tùy chọn)
- Redis (tùy chọn)

## LƯU Ý

- Dữ liệu được cập nhật tự động mỗi giờ
- Có thể điều chỉnh thời gian cập nhật trong file auto_update_data.py
- Nên sử dụng caching để giảm tải cho server
- Theo dõi log để phát hiện lỗi khi cập nhật dữ liệu

## ĐÓNG GÓP

Mọi đóng góp đều được chào đón. Vui lòng:
1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## LICENSE

MIT License

## LIÊN HỆ

Email: example@email.com
GitHub: github.com/username
