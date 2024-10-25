# Stock Analysis Platform

## Giới thiệu
Đây là một ứng dụng phân tích cổ phiếu sử dụng Django và yfinance để lấy dữ liệu thị trường chứng khoán Việt Nam.

## Tính năng mới
- Sử dụng yfinance để lấy dữ liệu cổ phiếu thời gian thực
- Hiển thị tổng quan thị trường với các chỉ số chính
- Danh sách cổ phiếu Việt Nam với thông tin chi tiết
- Biểu đồ giá cổ phiếu và dữ liệu lịch sử
- Caching để tối ưu hiệu suất
- Lưu trữ dữ liệu lịch sử trong database
- Sử dụng Celery cho background tasks
- Cập nhật dữ liệu cổ phiếu tự động và định kỳ

## Cài đặt và Sử dụng
1. Clone repository
2. Cài đặt dependencies: `pip install -r requirements.txt`
3. Cài đặt Redis (cần thiết cho Celery)
4. Chạy migrations: `python manage.py migrate`
5. Chạy Celery worker: `celery -A core worker -l info`
6. Chạy Celery beat (cho các task định kỳ): `celery -A core beat -l info`
7. Chạy server: `python manage.py runserver`

## Lưu ý
- Đảm bảo tuân thủ các điều khoản sử dụng của Yahoo Finance khi sử dụng yfinance
- Dữ liệu được cập nhật định kỳ, kiểm tra `update_stock_data` command để biết thêm chi tiết
- Caching được sử dụng để giảm số lượng request đến yfinance và cải thiện hiệu suất

## Đóng góp
Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp cho dự án.

## Giấy phép
[MIT License](LICENSE)
