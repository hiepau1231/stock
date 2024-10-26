from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .utils.performance import query_debugger, optimize_queryset

import pandas as pd
import json
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime

from .models import Stock, Portfolio, PortfolioItem, WatchList, PriceAlert, Industry, StockPrice
from .services.stock_service import StockService
from .services.report_service import PortfolioReportService
from .services.recommendation_service import RecommendationService
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

stock_service = StockService()

class DashboardView(LoginRequiredMixin, View):
    template_name = 'stock_analysis/dashboard.html'
    
    def get(self, request):
        try:
            stock_service = StockService()
            
            # Lấy tổng quan thị trường
            market_overview = stock_service.get_market_overview()
            
            # Lấy top tăng/giảm
            top_movers = stock_service.get_top_movers(limit=5)
            
            # Lấy tổng quan ngành
            industry_overview = stock_service.get_industry_overview()
            
            # Lấy khuyến nghị
            recommendation_service = RecommendationService()
            recommendations = recommendation_service.get_top_recommendations(limit=3)
            
            context = {
                'market_overview': market_overview,
                'top_gainers': top_movers['top_gainers'] if top_movers else [],
                'top_losers': top_movers['top_losers'] if top_movers else [],
                'industry_overview': industry_overview,
                'recommendations': recommendations,
                'last_update': timezone.now()
            }
            
            return render(request, self.template_name, context)
        except Exception as e:
            logger.error(f"Error in DashboardView: {str(e)}")
            messages.error(request, "An error occurred while loading the dashboard.")
            return render(request, self.template_name, {})

class StockListView(ListView):
    model = Stock
    template_name = 'stock_analysis/stock_list.html'
    context_object_name = 'stocks'

    @method_decorator(cache_page(60 * 15))  # Cache trong 15 phút
    @method_decorator(query_debugger)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Stock.objects.select_related('industry').all().order_by('symbol')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'stock_list'
        context['last_update'] = Stock.objects.order_by('-updated_at').first().updated_at if Stock.objects.exists() else None
        return context

@login_required
def dashboard(request):
    stock_service = StockService()
    top_movers = stock_service.get_top_movers(limit=5)
    
    context = {
        'top_movers': top_movers if top_movers else {'top_gainers': [], 'top_losers': []}
    }
    return render(request, 'stock_analysis/dashboard.html', context)

@login_required
def stock_list(request):
    stocks = optimize_queryset(
        Stock.objects.all(),
        prefetch_related=['historical_data']
    )
    context = {'stocks': stocks}
    return render(request, 'stock_analysis/stock_list.html', context)

@login_required
def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    historical_data = optimize_queryset(
        stock.historical_data.all().order_by('-date')[:30]
    )
    context = {
        'stock': stock,
        'historical_data': historical_data
    }
    return render(request, 'stock_analysis/stock_detail.html', context)

class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock_analysis/stock_detail.html'
    context_object_name = 'stock'
    slug_field = 'symbol'
    slug_url_kwarg = 'symbol'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock = self.object
        
        historical_data = stock_service.get_stock_historical_data(stock.symbol)
        
        if historical_data:
            latest_data = historical_data[0]
            
            context['latest_date'] = latest_data.get('date', 'N/A')
            context['latest_price'] = latest_data.get('close', 'N/A')
            context['latest_change'] = latest_data.get('change', 'N/A')
            context['latest_volume'] = latest_data.get('volume', 'N/A')
            
            # Tạo dữ liệu cho biểu đồ
            dates = [item['date'] for item in historical_data]
            prices = {
                'open': [item.get('open', 0) for item in historical_data],
                'high': [item.get('high', 0) for item in historical_data],
                'low': [item.get('low', 0) for item in historical_data],
                'close': [item.get('close', 0) for item in historical_data]
            }
            volumes = [item.get('volume', 0) for item in historical_data]

            # Tạo biểu đồ candlestick
            candlestick = go.Candlestick(
                x=dates,
                open=prices['open'],
                high=prices['high'],
                low=prices['low'],
                close=prices['close'],
                name='OHLC'
            )

            # Thêm volume bar
            volume_bar = go.Bar(
                x=dates,
                y=volumes,
                name='Volume',
                yaxis='y2',
                marker={'color': 'rgba(128,128,128,0.5)'}
            )

            # Tạo layout với 2 y-axis
            layout = go.Layout(
                title=f'{stock.symbol} - Biểu đồ giá',
                yaxis=dict(
                    title='Giá',
                    titlefont=dict(color='#1f77b4'),
                    tickfont=dict(color='#1f77b4')
                ),
                yaxis2=dict(
                    title='Khối lượng',
                    titlefont=dict(color='#7f7f7f'),
                    tickfont=dict(color='#7f7f7f'),
                    overlaying='y',
                    side='right'
                ),
                xaxis=dict(
                    rangeslider=dict(visible=False),
                    type='date'
                ),
                showlegend=True,
                height=600
            )

            # Tạo figure và chuyển thành HTML
            fig = go.Figure(data=[candlestick, volume_bar], layout=layout)
            
            # Cập nhật layout thêm
            fig.update_layout(
                template='plotly_white',
                hovermode='x unified',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            plot_div = plot(fig, output_type='div', include_plotlyjs=True)
            context['candlestick_chart'] = plot_div
            
            # Tính toán các chỉ báo kỹ thuật
            try:
                df = pd.DataFrame(historical_data)
                
                # RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # MACD
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                
                # Bollinger Bands
                sma = df['close'].rolling(window=20).mean()
                std = df['close'].rolling(window=20).std()
                bb_upper = sma + (std * 2)
                bb_lower = sma - (std * 2)
                
                context.update({
                    'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 'N/A',
                    'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 'N/A',
                    'signal': float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else 'N/A',
                    'bb_upper': float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else 'N/A',
                    'bb_middle': float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else 'N/A',
                    'bb_lower': float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else 'N/A'
                })
            except Exception as e:
                logger.error(f"Error calculating technical indicators for {stock.symbol}: {str(e)}")
                context.update({
                    'rsi': 'N/A',
                    'macd': 'N/A',
                    'signal': 'N/A',
                    'bb_upper': 'N/A',
                    'bb_middle': 'N/A',
                    'bb_lower': 'N/A'
                })
        else:
            # Nếu không c d liệu
            context.update({
                'latest_date': 'N/A',
                'latest_price': 'N/A',
                'latest_change': 'N/A',
                'latest_volume': 'N/A',
                'candlestick_chart': '',
                'rsi': 'N/A',
                'macd': 'N/A',
                'signal': 'N/A',
                'bb_upper': 'N/A',
                'bb_middle': 'N/A',
                'bb_lower': 'N/A'
            })
        
        return context

class PortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = 'stock_analysis/portfolio_list.html'
    context_object_name = 'portfolios'

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    template_name = 'stock_analysis/portfolio_create.html'
    fields = ['name']
    success_url = reverse_lazy('stock_analysis:portfolio_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = Portfolio
    template_name = 'stock_analysis/portfolio_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.get_object()
        
        # Lấy dữ liệu hiệu suất và rủi ro
        stock_service = StockService()
        performance_data = stock_service.calculate_portfolio_performance(portfolio)
        risk_data = stock_service.calculate_portfolio_risk(portfolio)
        
        context.update({
            'performance_data': performance_data,
            'benchmark_name': 'VN-Index',
            'risk_data': risk_data
        })
        return context

@login_required
def add_portfolio_stock(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        quantity = int(request.POST.get('quantity'))
        purchase_price = float(request.POST.get('purchase_price'))
        purchase_date = request.POST.get('purchase_date')
        
        stock = get_object_or_404(Stock, symbol=symbol)
        PortfolioItem.objects.create(
            portfolio=portfolio,
            stock=stock,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
        messages.success(request, f"{symbol} đã được thêm vào danh mục đầu tư của bạn.")
    return redirect('stock_analysis:portfolio_detail', pk=pk)

@login_required
def remove_portfolio_stock(request, pk, stock_id):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    item = get_object_or_404(PortfolioItem, portfolio=portfolio, stock_id=stock_id)
    item.delete()
    messages.success(request, f"{item.stock.symbol} đã được xóa khỏi danh mục đầu tư của bạn.")
    return redirect('stock_analysis:portfolio_detail', pk=pk)

class WatchListView(LoginRequiredMixin, ListView):
    model = WatchList
    template_name = 'stock_analysis/watchlist.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        watchlist, created = WatchList.objects.get_or_create(user=self.request.user)
        return watchlist.stocks.all()  # Trả về trực tiếp danh sách stocks

@login_required
def add_to_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    watchlist, created = WatchList.objects.get_or_create(user=request.user)
    watchlist.stocks.add(stock)
    messages.success(request, f"{symbol} đã được thêm vo danh sách theo dõi của bạn.")
    return redirect('stock_analysis:watchlist')

@login_required
def remove_from_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    watchlist = get_object_or_404(WatchList, user=request.user)
    watchlist.stocks.remove(stock)
    messages.success(request, f"{symbol} đã được xóa khỏi danh sách theo dõi của bạn.")
    return redirect('stock_analysis:watchlist')

@login_required
def compare_stocks(request):
    if request.method == 'POST':
        symbols = request.POST.getlist('symbols')
        comparison_data = []
        for symbol in symbols:
            data = stock_service.get_stock_data(symbol)
            if data:
                comparison_data.append(data)
        return render(request, 'stock_analysis/compare_stocks.html', {'comparison_data': comparison_data})
    return render(request, 'stock_analysis/compare_stocks.html')

@login_required
def industry_analysis(request):
    industries = Industry.objects.all()
    context = {
        'industries': industries
    }
    return render(request, 'stock_analysis/industry_analysis.html', context)

@login_required
def stock_intraday(request, symbol):
    intraday_data = stock_service.get_stock_intraday(symbol)
    if intraday_data is not None:
        return JsonResponse(intraday_data.to_dict('records'), safe=False)
    else:
        return JsonResponse({'error': 'Unable to fetch intraday data'}, status=400)

@login_required
def get_technical_indicators(request, symbol):
    try:
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return JsonResponse(
                {'error': f'Stock with symbol {symbol} not found'}, 
                status=404
            )
        
        historical_data = stock.historical_data.all().order_by('date')
        if not historical_data.exists():
            return JsonResponse(
                {'error': f'No historical data found for {symbol}'}, 
                status=404
            )
        
        df = pd.DataFrame(list(historical_data.values()))
        
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        exp1 = df['close_price'].ewm(span=12, adjust=False).mean()
        exp2 = df['close_price'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        sma = df['close_price'].rolling(window=20).mean()
        std = df['close_price'].rolling(window=20).std()
        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)
        
        indicators = {
            'rsi': float(rsi.iloc[-1]),
            'macd': float(macd.iloc[-1]),
            'signal': float(signal.iloc[-1]),
            'bb_upper': float(bb_upper.iloc[-1]),
            'bb_middle': float(sma.iloc[-1]),
            'bb_lower': float(bb_lower.iloc[-1])
        }
        
        return JsonResponse(indicators)
    except Exception as e:
        logger.error(f"Error calculating indicators for {symbol}: {str(e)}")
        if isinstance(e, Stock.DoesNotExist):
            return JsonResponse({'error': str(e)}, status=404)
        return JsonResponse({'error': str(e)}, status=400)

class PriceAlertListView(LoginRequiredMixin, ListView):
    model = PriceAlert
    template_name = 'stock_analysis/price_alert_list.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)

@login_required
def add_price_alert(request, symbol):
    if request.method == 'POST':
        try:
            stock = get_object_or_404(Stock, symbol=symbol)
            alert_type = request.POST.get('alert_type')
            price_threshold = float(request.POST.get('price_threshold'))
            
            # Kiểm tra xem đã có cảnh báo tương tự chưa
            existing_alert = PriceAlert.objects.filter(
                user=request.user,
                stock=stock,
                alert_type=alert_type,
                price_threshold=price_threshold,
                is_active=True
            ).exists()
            
            if existing_alert:
                messages.warning(request, f'Đã tồn tại cảnh báo giá tương tự cho {symbol}')
            else:
                PriceAlert.objects.create(
                    user=request.user,
                    stock=stock,
                    alert_type=alert_type,
                    price_threshold=price_threshold
                )
                messages.success(request, f'Đã tạo cảnh báo giá cho {symbol}')
            
            return redirect('stock_analysis:stock_detail', symbol=symbol)
        except Exception as e:
            logger.error(f"Error creating price alert: {str(e)}")
            messages.error(request, 'Có lỗi xảy ra khi tạo cảnh báo giá')
            return redirect('stock_analysis:stock_detail', symbol=symbol)
    
    return redirect('stock_analysis:stock_detail', symbol=symbol)

@login_required
def remove_price_alert(request, alert_id):
    alert = get_object_or_404(PriceAlert, id=alert_id, user=request.user)
    alert.delete()
    messages.success(request, f'Đã xóa cảnh báo giá cho {alert.stock.symbol}')
    return redirect('stock_analysis:price_alert_list')

@login_required
def export_portfolio_pdf(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    items = portfolio.portfolioitem_set.all()
    
    buffer = PortfolioReportService.generate_pdf_report(portfolio, items)
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'portfolio_{portfolio.name}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@login_required
def export_portfolio_excel(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    items = portfolio.portfolioitem_set.all()
    
    buffer = PortfolioReportService.generate_excel_report(portfolio, items)
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'portfolio_{portfolio.name}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

class RecommendationsView(LoginRequiredMixin, View):
    template_name = 'stock_analysis/recommendations.html'
    
    def get(self, request):
        recommendation_service = RecommendationService()
        recommendations = recommendation_service.get_top_recommendations(limit=5)
        
        # Thêm thông tin giá và thay đổi
        stock_service = StockService()
        for rec in recommendations:
            stock_data = stock_service.get_stock_data(rec['symbol'])
            if stock_data is not None:  # Kiểm tra None thay vì dùng if stock_data
                rec['current_price'] = stock_data['price']
                rec['change'] = stock_data['change_percent']
            else:
                rec['current_price'] = 0
                rec['change'] = 0
        
        context = {
            'recommendations': recommendations,
            'last_update': timezone.now()
        }
        
        return render(request, self.template_name, context)

class PortfolioOptimizationView(LoginRequiredMixin, View):
    template_name = 'stock_analysis/portfolio_optimization.html'
    
    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        optimization_service = PortfolioOptimizationService()
        
        optimization_data = optimization_service.get_portfolio_optimization(portfolio)
        
        context = {
            'portfolio': portfolio,
            'optimization_data': optimization_data
        }
        return render(request, self.template_name, context)

@login_required
def get_industry_data(request, industry_id):
    industry = get_object_or_404(Industry, id=industry_id)
    stocks = Stock.objects.filter(stockindustry__industry=industry)
    
    # Tính toán các chỉ số ngành
    overview = {
        'name': industry.name,
        'total_market_cap': sum(stock.market_cap for stock in stocks if stock.market_cap),
        'average_pe': statistics.mean(stock.pe_ratio for stock in stocks if stock.pe_ratio),
        'growth': 5.2  # Thay bằng tính toán thực tế
    }
    
    # Phân loại theo sàn
    stocks_by_exchange = {}
    for stock in stocks:
        if stock.exchange not in stocks_by_exchange:
            stocks_by_exchange[stock.exchange] = []
        stocks_by_exchange[stock.exchange].append({
            'symbol': stock.symbol,
            'name': stock.name,
            'price': stock.current_price,
            'change': stock.percent_change
        })
    
    # Top 3 cổ phiếu tiềm năng
    potential_stocks = list(stocks)
    potential_stocks.sort(key=lambda x: x.market_cap, reverse=True)
    potential_stocks = potential_stocks[:3]
    
    return JsonResponse({
        'overview': overview,
        'stocks': stocks_by_exchange,
        'money_flow': {
            'dates': ['2024-01', '2024-02', '2024-03'],
            'values': [1000000, 1200000, 900000]
        },
        'potential_stocks': [
            {
                'symbol': stock.symbol,
                'name': stock.name,
                'price': stock.current_price,
                'reason': 'Market leader with strong fundamentals'
            }
            for stock in potential_stocks
        ]
    })

@login_required
def check_data(request):
    # Đếm số lượng records
    stock_count = Stock.objects.count()
    price_count = StockPrice.objects.count()
    industry_count = Industry.objects.count()
    
    # Lấy thời gian cập nhật cuối cùng
    last_update = Stock.objects.order_by('-updated_at').first().updated_at if stock_count > 0 else None
    
    # Lấy 10 mã cổ phiếu mới nhất với thông tin chi tiết
    recent_stocks = Stock.objects.select_related('industry').order_by('-updated_at')[:10]
    
    # Lấy 10 giá mới nhất với thông tin chi tiết
    recent_prices = StockPrice.objects.select_related('stock').order_by('-date', '-created_at')[:10]
    
    context = {
        'stock_count': stock_count,
        'price_count': price_count,
        'industry_count': industry_count,
        'last_update': last_update,
        'recent_stocks': recent_stocks,
        'recent_prices': recent_prices
    }
    
    return render(request, 'stock_analysis/check_data.html', context)

@login_required
def refresh_data(request):
    if request.method == 'POST':
        try:
            from django.core.management import call_command
            call_command('auto_update_data')
            messages.success(request, 'Data has been successfully updated!')
        except Exception as e:
            messages.error(request, f'Error updating data: {str(e)}')
    return redirect('stock_analysis:check_data')

