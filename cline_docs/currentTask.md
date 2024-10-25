# Nhiệm Vụ Hiện Tại

## Mục Tiêu
Chuyển đổi hệ thống từ sử dụng thư viện vnquant sang Alpha Vantage API để lấy dữ liệu chứng khoán, và cải thiện chức năng cũng như hiệu suất của ứng dụng phân tích chứng khoán.

## Bối Cảnh
Chúng ta đã quyết định không sử dụng vnquant và thay vào đó sẽ sử dụng Alpha Vantage API (https://www.alphavantage.co/documentation/) để lấy dữ liệu chứng khoán.

## Các Bước Tiếp Theo

1. Đăng ký và lấy API key từ Alpha Vantage:
   - Truy cập https://www.alphavantage.co/ và đăng ký tài khoản.
   - Lấy API key và lưu trữ an toàn.

2. Cài đặt thư viện requests:
   - Thêm requests vào file requirements.txt.
   - Cài đặt requests trong môi trường phát triển.

3. Cập nhật StockService:
   - Thay thế tất cả các cuộc gọi API từ vnquant bằng các cuộc gọi tới Alpha Vantage API.
   - Cập nhật xử lý dữ liệu để phù hợp với định dạng mới từ Alpha Vantage.
   - Thêm xử lý giới hạn tốc độ API (rate limiting) để tuân thủ giới hạn của Alpha Vantage.

4. Cập nhật scrape_stock_data command:
   - Điều chỉnh logic crawl dữ liệu để sử dụng Alpha Vantage API thay vì vnquant.

5. Kiểm tra và cập nhật các view:
   - Đảm bảo rằng tất cả các view đang sử dụng dữ liệu từ StockService một cách chính xác.

6. Cập nhật unit tests:
   - Cập nhật các test case để phản ánh việc sử dụng Alpha Vantage API.

7. Xử lý lỗi và logging:
   - Cập nhật hệ thống xử lý lỗi để phù hợp với các exception có thể xảy ra khi sử dụng Alpha Vantage API.
   - Đảm bảo logging đầy đủ cho quá trình lấy dữ liệu mới.

8. Cập nhật tài liệu:
   - Cập nhật README.md và các tài liệu liên quan để phản ánh việc sử dụng Alpha Vantage API.

9. Tối ưu hóa hiệu suất:
   - Kiểm tra và tối ưu hóa các truy vấn dữ liệu sử dụng Alpha Vantage API.
   - Cập nhật cơ chế cache để giảm số lượng cuộc gọi API không cần thiết.

10. Kiểm thử tích hợp:
    - Chạy kiểm thử toàn diện để đảm bảo tất cả các chức năng vẫn hoạt động chính xác với dữ liệu mới.

11. Triển khai:
    - Cập nhật môi trường production với các thay đổi mới.
    - Theo dõi hiệu suất và độ ổn định của hệ thống sau khi chuyển đổi.

## Ưu tiên
Ưu tiên cao nhất là đảm bảo tính liên tục của dữ liệu và chức năng của ứng dụng. Tập trung vào việc cập nhật StockService và scrape_stock_data command trước tiên.

## Lưu ý
- Đảm bảo bảo mật API key của Alpha Vantage.
- Tuân thủ các giới hạn tốc độ và điều khoản sử dụng của Alpha Vantage API.
- Cần cẩn thận trong việc xử lý dữ liệu lịch sử đã được lưu trữ từ nguồn cũ.
- Theo dõi chặt chẽ hiệu suất của hệ thống sau khi chuyển đổi để đảm bảo không có sự suy giảm đáng kể.
