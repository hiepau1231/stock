# Stock Analysis Platform







## Giới thiệu



Stock Analysis Platform là một ứng dụng web được thiết kế để cung cấp các công cụ toàn diện để phân tích dữ liệu thị trường chứng khoán. Dự án sử dụng Django cho backend và Argon Dashboard Django template cho giao diện người dùng.







## Yêu cầu hệ thống



- Python 3.8+



- pip (Python package manager)



- Git







## Cài đặt và Chạy Dự án







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







5. Chạy server:   ```



   python manage.py runserver   ```







## Chức năng mới: Cập nhật dữ liệu chỉ số thị trường

- Truy cập trang dashboard
- Nhấn nút "Cập nhật dữ liệu chỉ số" để mở form cập nhật
- Xác nhận và gửi form để lấy dữ liệu mới nhất
- Dữ liệu sẽ được hiển thị trên dashboard sau khi cập nhật







## Quản lý dữ liệu qua Admin Interface







1. Tạo superuser:   ```



   python manage.py createsuperuser   ```







2. Truy cập `/admin` và đăng nhập với tài khoản superuser







3. Quản lý dữ liệu Stock, StockPrice, và StockIndex







## Lưu ý

- Đảm bảo cài đặt tất cả các dependency mới bằng cách chạy `pip install -r requirements.txt`
- Chạy migrations nếu có bất kỳ thay đổi nào trong models: `python manage.py makemigrations` và `python manage.py migrate`
- Kiểm tra log để debug các vấn đề liên quan đến web scraping







## Chức năng mới

1. Biểu đồ chỉ số thị trường:
   - Dashboard hiện hiển thị biểu đồ so sánh các chỉ số VN-Index, HNX-Index và UPCOM-Index.

2. Tìm kiếm cổ phiếu:
   - Người dùng có thể tìm kiếm cổ phiếu theo mã hoặc tên công ty trên trang danh sách cổ phiếu.







## Cài đặt thêm

Để sử dụng biểu đồ, cần cài đặt thêm thư viện plotly:

## Tính năng mới

1. Phân trang danh sách cổ phiếu:
   - Hiển thị 20 cổ phiếu mỗi trang để cải thiện hiệu suất và trải nghiệm người dùng.

2. Xuất dữ liệu cổ phiếu:
   - Người dùng có thể xuất danh sách cổ phiếu ra file CSV.

3. Caching:
   - Sử dụng caching để cải thiện hiệu suất trang dashboard và danh sách cổ phiếu.

4. So sánh cổ phiếu:
   - Người dùng có thể so sánh tối đa 3 cổ phiếu cùng lúc.
   - So sánh các chỉ số quan trọng như giá hiện tại, thay đổi giá, khối lượng giao dịch, v.v.

5. Cải thiện hiệu suất:
   - Tối ưu hóa truy vấn database để tăng tốc độ tải trang.
   - Sử dụng caching để giảm tải cho server và cải thiện thời gian phản hồi.

## Cài đặt thêm

Không cần cài đặt thêm thư viện cho các tính năng mới.

<!-- Existing content -->
