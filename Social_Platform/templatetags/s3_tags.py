from django import template
from django.conf import settings
import boto3

register = template.Library()

@register.filter
def s3_url(image_field, expires_in=3600):
    """
    Template filter để lấy presigned URL cho ảnh từ S3
    Usage: {{ post.image|s3_url }}
    """
    if not image_field or not image_field.name:
        return None
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': image_field.name},
            ExpiresIn=expires_in
        )
    except Exception:
        # Fallback to regular URL if S3 fails
        try:
            return image_field.url
        except:
            return None

@register.simple_tag
def get_s3_url(image_field, expires_in=3600):
    """
    Template tag để lấy presigned URL cho ảnh từ S3
    Usage: {% get_s3_url post.image as image_url %}
    """
    return s3_url(image_field, expires_in)

@register.inclusion_tag('social/image_display.html')
def display_image(image_field, alt_text="Image", css_class="img-fluid"):
    """
    Inclusion tag để hiển thị ảnh với S3 URL
    Usage: {% display_image post.image "Post image" "custom-class" %}
    """
    image_url = s3_url(image_field)
    return {
        'image_url': image_url,
        'alt_text': alt_text,
        'css_class': css_class,
        'has_image': bool(image_url)
    }