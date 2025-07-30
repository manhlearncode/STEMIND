from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import File


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for Bootstrap styling
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'category', 'file_description', 'file_urls', 'file_thumbnail', 'file_status', 'file_price']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề tài liệu...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mô tả chi tiết về tài liệu...'
            }),
            'file_urls': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.zip,.rar'
            }),
            'file_thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'file_status': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updatePriceVisibility()'
            }),
            'file_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '1000'
            })
        }
        labels = {
            'title': 'Tiêu đề tài liệu',
            'category': 'Danh mục',
            'file_description': 'Mô tả',
            'file_urls': 'Tệp tài liệu',
            'file_thumbnail': 'Ảnh thumbnail (tùy chọn)',
            'file_status': 'Trạng thái',
            'file_price': 'Giá (VNĐ)'
        }
        help_texts = {
            'title': 'Tên tài liệu phải là duy nhất',
            'file_urls': 'Chọn file PDF, Word, PowerPoint, Excel, Text, ZIP hoặc RAR (tối đa 50MB)',
            'file_thumbnail': 'Tải ảnh đại diện cho tài liệu (tối đa 5MB)',
            'file_price': 'Nhập giá bằng VNĐ (0 = miễn phí)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cập nhật choices cho file_status theo model
        self.fields['file_status'].choices = [(0, 'Free'), (1, 'For sales')]

    def clean_file_urls(self):
        file = self.cleaned_data.get('file_urls')
        
        if file and hasattr(file, 'size'):
            # Kiểm tra kích thước file (50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('Kích thước file không được vượt quá 50MB.')
            
            # Kiểm tra định dạng file
            allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Định dạng file không được hỗ trợ. Vui lòng chọn file PDF, Word, PowerPoint, Excel, Text, ZIP hoặc RAR.')
        elif not file:
            raise forms.ValidationError('Vui lòng chọn tệp để tải lên.')
            
        return file

    def clean_file_thumbnail(self):
        thumbnail = self.cleaned_data.get('file_thumbnail')
        
        if thumbnail and hasattr(thumbnail, 'size'):
            # Kiểm tra kích thước ảnh (5MB)
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Kích thước ảnh không được vượt quá 5MB.')
            
            # Kiểm tra định dạng ảnh
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = thumbnail.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Định dạng ảnh không được hỗ trợ. Vui lòng chọn file JPG, PNG, GIF hoặc WEBP.')
                
        return thumbnail

    def clean_file_price(self):
        price = self.cleaned_data.get('file_price')
        status = self.cleaned_data.get('file_status')
        
        # Kiểm tra giá khi status = For sales
        if status == 1 and (price is None or price <= 0):
            raise forms.ValidationError('Vui lòng nhập giá cho tài liệu có phí.')
        
        if price is not None and price < 0:
            raise forms.ValidationError('Giá không được âm.')
            
        return price or 0

    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        # Kiểm tra trùng lặp title (trừ chính nó nếu đang edit)
        if File.objects.filter(title=title).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Tiêu đề này đã tồn tại. Vui lòng chọn tiêu đề khác.')
            
        return title 