from django import template
from django.conf import settings
import boto3

register = template.Library()

@register.filter
def s3_url(image_field, expires_in=3600):
    """
    Template filter để lấy URL cho ảnh từ local storage
    Usage: {{ post.image|s3_url }}
    """
    if not image_field or not image_field.name:
        return None
    
    try:
        return image_field.url
    except:
        return None

@register.simple_tag
def get_s3_url(image_field, expires_in=3600):
    """
    Template tag để lấy URL cho ảnh từ local storage
    Usage: {% get_s3_url post.image as image_url %}
    """
    return s3_url(image_field, expires_in)

@register.inclusion_tag('social/image_display.html')
def display_image(image_field, alt_text="Image", css_class="img-fluid"):
    """
    Inclusion tag để hiển thị ảnh với local URL
    Usage: {% display_image post.image "Post image" "custom-class" %}
    """
    image_url = s3_url(image_field)
    return {
        'image_url': image_url,
        'alt_text': alt_text,
        'css_class': css_class,
        'has_image': bool(image_url)
    }