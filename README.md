# Stock Analysis Platform

Một nền tảng phân tích chứng khoán được xây dựng bằng Django, sử dụng Fireant API để lấy dữ liệu thị trường chứng khoán Việt Nam.

## Tính năng

- 📊 Hiển thị dữ liệu thị trường realtime
- 📈 Biểu đồ giá và các chỉ báo kỹ thuật
- 📱 Giao diện responsive với Argon Dashboard
- 🔍 Tìm kiếm và lọc cổ phiếu
- 📋 Quản lý danh mục đầu tư
- 🔔 Theo dõi và cảnh báo giá
- 📊 Phân tích cơ bản và kỹ thuật
- 🤖 Dự đoán giá sử dụng Machine Learning

## Yêu cầu hệ thống

- Python 3.9+
- Django 4.2.9
- SQLite3
- Node.js (cho việc build assets)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/stock-analysis.git
cd stock-analysis
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Tạo database và chạy migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Tải dữ liệu ban đầu:
```bash
python manage.py load_initial_data
```

6. Chạy development server:
```bash
python manage.py runserver
```

Truy cập http://127.0.0.1:8000/ để xem ứng dụng.

## Cấu trúc dự án

```
stock_analysis_project/
├── manage.py
├── core/                   # Cấu hình Django chính
├── apps/
│   ├── stock_analysis/    # App phân tích chứng khoán
│   ├── predictions/       # App dự đoán giá
│   └── authentication/    # App xác thực người dùng
├── templates/             # Templates HTML
├── static/               # Static files (CSS, JS, images)
└── cline_docs/           # Documentation
```

## API và Data Sources

- Fireant API: Dữ liệu thị trường realtime
- yfinance: Dữ liệu lịch sử
- BeautifulSoup4: Web scraping khi cần thiết

## Tính năng đang phát triển

1. Biểu đồ và chỉ báo kỹ thuật:
   - Candlestick charts
   - RSI, MACD, Bollinger Bands
   - Volume analysis

2. Quản lý danh mục:
   - Theo dõi lợi nhuận/lỗ
   - Cảnh báo giá
   - Báo cáo hiệu suất
   - Xuất báo cáo PDF/Excel

3. Machine Learning:
   - Dự đoán giá
   - Phân tích sentiment
   - Gợi ý cổ phiếu

## Đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Liên hệ

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/stock-analysis](https://github.com/yourusername/stock-analysis)

## Acknowledgments

- [Argon Dashboard Django](https://www.creative-tim.com/product/argon-dashboard-django)
- [Fireant API](https://docs.fireant.vn)
- [yfinance](https://github.com/ranaroussi/yfinance)
