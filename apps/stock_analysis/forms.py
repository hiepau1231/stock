from django import forms
from .models import Stock, Portfolio, PortfolioItem

class UpdateDataForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label='Xác nhận cập nhật dữ liệu',
        help_text='Tick vào đây để xác nhận việc cập nhật dữ liệu'
    )

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']
        labels = {
            'name': 'Tên danh mục'
        }

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['stock', 'quantity', 'purchase_price', 'purchase_date']
        labels = {
            'stock': 'Mã cổ phiếu',
            'quantity': 'Số lượng',
            'purchase_price': 'Giá mua',
            'purchase_date': 'Ngày mua'
        }
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'})
        }

class StockSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã cổ phiếu hoặc tên công ty...'
        })
    )
    sector = forms.ChoiceField(
        required=False,
        label='Ngành',
        choices=[('', 'Tất cả ngành')],  # Choices sẽ được cập nhật động
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cập nhật choices cho sector từ database
        sectors = Stock.objects.values_list('sector', flat=True).distinct()
        self.fields['sector'].choices += [(sector, sector) for sector in sectors if sector]

class CompareStocksForm(forms.Form):
    stock1 = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        label='Cổ phiếu 1',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock2 = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        label='Cổ phiếu 2',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock3 = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        required=False,
        label='Cổ phiếu 3 (tùy chọn)',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
