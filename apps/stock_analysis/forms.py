from django import forms

class UpdateDataForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Xác nhận cập nhật dữ liệu")
