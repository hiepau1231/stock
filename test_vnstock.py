from vnstock import *

try:
    # Test lấy danh sách công ty
    companies = listing_companies()
    print("Danh sách công ty:")
    print(companies.head())

    # Test lấy dữ liệu lịch sử
    historical_data = stock_historical_data("VNM", "2023-01-01", "2023-12-31")
    print("\nDữ liệu lịch sử VNM:")
    print(historical_data.head())

    # Test lấy thông tin thị trường
    market_data = market_top_mover()
    print("\nThông tin thị trường:")
    print(market_data)

except Exception as e:
    print(f"Lỗi: {str(e)}")
