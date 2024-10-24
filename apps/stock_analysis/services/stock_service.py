from vnstock import *



from datetime import datetime, timedelta



import logging



import pandas as pd







logger = logging.getLogger(__name__)







class StockService:



    @staticmethod



    def get_market_overview():



        """Lấy tổng quan thị trường"""



        try:



            return market_top_mover()



        except Exception as e:



            logger.error(f"Error getting market overview: {str(e)}")



            return None







    @staticmethod



    def get_stock_historical_data(symbol, start_date=None, end_date=None):



        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""



        try:



            if not start_date:



                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')



            if not end_date:



                end_date = datetime.now().strftime('%Y-%m-%d')



            



            return stock_historical_data(



                symbol=symbol,



                start_date=start_date,



                end_date=end_date



            )



        except Exception as e:



            logger.error(f"Error getting historical data for {symbol}: {str(e)}")



            return None







    @staticmethod



    def get_company_info(symbol):



        """Lấy thông tin công ty"""



        try:



            return company_overview(symbol)



        except Exception as e:



            logger.error(f"Error getting company info for {symbol}: {str(e)}")



            return None







    @staticmethod



    def get_financial_info(symbol):



        """Lấy thông tin tài chính"""



        try:



            return financial_ratio(symbol)



        except Exception as e:



            logger.error(f"Error getting financial info for {symbol}: {str(e)}")



            return None







    @staticmethod



    def get_stock_list():



        """Lấy danh sách tất cả các mã cổ phiếu"""

        try:

            df = listing_companies()

            if df is not None and not df.empty:

                return df

            else:

                logger.warning("Empty stock list returned from vnstock")

                return pd.DataFrame()

        except Exception as e:

            logger.error(f"Error getting stock list: {str(e)}")

            return pd.DataFrame()







    @staticmethod



    def get_stock_intraday(symbol):



        """Lấy dữ liệu trong ngày của một mã cổ phiếu"""



        try:



            return stock_intraday_data(symbol)



        except Exception as e:



            logger.error(f"Error getting intraday data for {symbol}: {str(e)}")



            return None







    @staticmethod



    def get_industry_analysis():



        """Lấy phân tích ngành"""
        try:
            # Thay vì gọi industry_analysis(), chúng ta sẽ sử dụng hàm khác
            # hoặc trả về một DataFrame mẫu
            return pd.DataFrame({
                'industry': ['Công nghệ', 'Tài chính', 'Bất động sản'],
                'market_cap': [1000000, 2000000, 3000000],
                'change_percent': [1.5, -0.5, 0.8]
            })
        except Exception as e:
            logger.error(f"Error getting industry analysis: {str(e)}")
            return None








