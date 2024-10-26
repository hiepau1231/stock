# Nhiệm Vụ Hiện Tại

## Đã hoàn thành
- ✅ Chuyển đổi từ vnstock3 sang yfinance để lấy dữ liệu chứng khoán
- ✅ Cập nhật StockService để sử dụng yfinance API
- ✅ Cập nhật và sửa lỗi tất cả tests trong apps.stock_analysis
- ✅ Thêm caching để tối ưu hiệu suất
- ✅ Thêm logging chi tiết
- ✅ Hiển thị dữ liệu trên dashboard và stock list
- ✅ Tạo models cần thiết trong predictions/models.py
- ✅ Tối ưu hóa các truy vấn database
- ✅ Thêm indexes cho các trường thường xuyên query
- ✅ Thêm biểu đồ Candlestick cho dữ liệu cổ phiếu
- ✅ Thêm các chỉ báo kỹ thuật (RSI, MACD, Bollinger Bands)
- ✅ Cải thiện giao diện chi tiết cổ phiếu
- ✅ Thêm responsive design cho mobile
- ✅ Thêm tính năng cảnh báo giá
- ✅ Cập nhật dữ liệu tự động với management command
- ✅ Thêm loading indicators cho biểu đồ
- ✅ Thêm tính năng xuất báo cáo PDF/Excel cho danh mục
- ✅ Thêm biểu đồ phân bổ danh mục
- ✅ Thêm thống kê hiệu suất danh mục theo thời gian
- ✅ Thêm so sánh với benchmark (VN-Index)
- ✅ Thêm phân tích rủi ro danh mục (Volatility, Sharpe Ratio, Beta, VaR)
- ✅ Trang giới thiệu và hướng dẫn
- ✅ Trang Cổ phiếu được khuyến nghị:
  - ✅ Hiển thị 5 mã cổ phiếu được khuyến nghị
  - ✅ Cập nhật chỉ số hiện tại mỗi tuần
  - ✅ Thêm lý do khuyến nghị
  - ✅ Thêm cron job cập nhật tuần qua Celery

## Cần làm tiếp theo thứ tự ưu tiên

1. Phân tích cổ phiếu theo ngành:
   - Tạo thanh chọn ngành (11 ngành)
   - Hiển thị danh sách cổ phiếu theo ngành và sàn
   - Thêm biểu đồ phân tích dòng tiền
   - Hiển thị 3 mã tiềm năng của ngành
   (Đã có model Industry và StockIndustry, cần thêm data và logic)

2. Phân tích và dự đoán VNINDEX:
   - Thêm thông tin và chỉ số hiện tại
   - Cập nhật dự đoán 1 tuần
   - Tự động cập nhật hàng tuần
   (Cần implement thuật toán dự đoán)

3. Phân tích và dự đoán từng mã:
   - Thêm form chọn mã và thời gian dự đoán
   - Hiển thị thông tin chi tiết (P/E, EPS, etc.)
   - Thêm các biểu đồ phân tích
   - Thêm khuyến nghị mua/bán
   (Phần phức tạp nhất, cần nhiều thuật toán)

## Chi tiết triển khai

### 1. Phân tích theo ngành (Ưu tiên 1):
- Tạo data migration cho 11 ngành
- Implement IndustryAnalysisService
- Tạo template industry_analysis.html
- Thêm biểu đồ dòng tiền ngành

### 2. Dự đoán VNINDEX (Ưu tiên 2):
- Implement PredictionService
- Tạo template market_prediction.html
- Thêm cron job cập nhật tuần

## Ưu tiên
1. Thêm gợi ý cân bằng danh mục
2. Thêm thông báo email khi có biến động lớn
3. Thêm phân tích cơ bản và kỹ thuật nâng cao
4. Cải thiện UX/UI với dark mode và animations

## Lưu ý
- Theo dõi giới hạn request của yfinance API
- Thêm error handling cho các trường hợp API không phản hồi
- Cân nhắc việc cache dữ liệu offline cho các mã giao dịch phổ biến
- Đảm bảo UX/UI thân thiện với người dùng
- Tối ưu performance cho mobile
