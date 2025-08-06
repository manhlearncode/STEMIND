from django import forms
from .models import Post, Comment, UserProfile

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
    class Meta:
        model = UserProfile
        fields = ['lastname', 'firstname', 'age', 'role']
        widgets = {
            'lastname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập họ của bạn'
            }),
            'firstname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên của bạn'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tuổi của bạn',
                'min': '1',
                'max': '120'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'lastname': 'Họ',
            'firstname': 'Tên',
            'age': 'Tuổi',
            'role': 'Vai trò'
        } 