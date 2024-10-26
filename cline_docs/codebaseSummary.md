# Tổng quan Codebase

## Cấu trúc chính
Dự án được tổ chức thành các module chính:
- `apps/`: Chứa các ứng dụng Django
- `core/`: Cấu hình Django
- `cline_docs/`: Tài liệu dự án
- `staticfiles/`: Static files

## Các thành phần chính

### 1. Stock Analysis Module
Đường dẫn: `apps/stock_analysis/`
- **Models**: Định nghĩa cấu trúc dữ liệu cho cổ phiếu, danh mục, giao dịch
- **Services**: Xử lý logic nghiệp vụ (stock, portfolio, optimization)
- **Views**: Xử lý request và render templates
- **Templates**: Giao diện người dùng

### 2. Services
Đường dẫn: `apps/stock_analysis/services/`
- `stock_service.py`: Xử lý dữ liệu cổ phiếu từ yfinance
- `portfolio_service.py`: Quản lý danh mục đầu tư
- `portfolio_optimization_service.py`: Tối ưu hóa danh mục
- `portfolio_report_service.py`: Xuất báo cáo
- `portfolio_analysis_service.py`: Phân tích danh mục
- `alert_service.py`: Quản lý cảnh báo
- `recommendation_service.py`: Đề xuất cổ phiếu

### 3. Data Flow
1. Dữ liệu cổ phiếu:
   - Lấy từ yfinance API
   - Cache để tối ưu hiệu suất
   - Cập nhật tự động qua auto_update_data

2. Danh mục đầu tư:
   - CRUD operations qua Portfolio model
   - Tính toán hiệu suất realtime
   - Xuất báo cáo PDF/Excel

3. Phân tích và Dự đoán:
   - Phân tích kỹ thuật
   - Tối ưu hóa danh mục
   - Đề xuất cổ phiếu

## Dependencies chính
- Django 5.0.2: Framework chính
- yfinance: Lấy dữ liệu chứng khoán
- Plotly: Vẽ biểu đồ
- Pandas: Xử lý dữ liệu
- Celery (optional): Task scheduling
- Redis (optional): Caching

## Recent Changes
1. Chuyển từ vnstock3 sang yfinance API
2. Thêm quản lý danh mục đầu tư
3. Thêm tối ưu hóa danh mục
4. Thêm xuất báo cáo PDF/Excel
5. Cải thiện hiệu suất với caching

## Performance Considerations
- Sử dụng cache cho dữ liệu thường xuyên truy cập
- Bulk create/update cho thao tác database
- Lazy loading cho templates
- Tối ưu query database

## Security
- Authentication required cho các chức năng quan trọng
- CSRF protection
- Rate limiting cho API calls
- Secure data transmission

## Known Issues
- Giới hạn request của yfinance API
- Độ trễ khi cập nhật dữ liệu realtime
- Cache invalidation khi dữ liệu thay đổi

## Future Improvements
1. Implement Celery cho task scheduling
2. Thêm websocket cho dữ liệu realtime
3. Cải thiện thuật toán dự đoán
4. Thêm social features
5. Mobile app integration
