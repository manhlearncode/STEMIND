from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, UserProfile, CustomUser

class CustomUserCreationForm(UserCreationForm):
    lastname = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ của bạn'
        }),
        label='Họ'
    )
    
    firstname = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên của bạn'
        }),
        label='Tên'
    )
    
    age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tuổi của bạn',
            'min': '1',
            'max': '120'
        }),
        label='Tuổi'
    )
    
    address = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ công tác của bạn'
        }),
        label='Địa chỉ công tác'
    )
    
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Vai trò'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'lastname', 'firstname', 'age', 'address', 'role', 'password1', 'password2']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'post-input',
                'placeholder': 'What\'s happening in STEM world?',
                'rows': 4,
                'maxlength': 500
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'content': '',
            'image': ''
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'comment-input',
                'placeholder': 'Write a comment...',
                'rows': 2,
                'maxlength': 300
            })
        }
        labels = {
            'content': ''
        }

class UserProfileForm(forms.ModelForm):
    """Form cho UserProfile - chỉ chứa bio và avatar (tùy chọn)"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Giới thiệu về bản thân... (tùy chọn)',
                'rows': 3,
                'maxlength': 200
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'bio': 'Giới thiệu (tùy chọn)',
            'avatar': 'Ảnh đại diện (tùy chọn)'
        }
        help_texts = {
            'bio': 'Bạn có thể bỏ qua trường này',
            'avatar': 'Bạn có thể bỏ qua trường này'
        } 