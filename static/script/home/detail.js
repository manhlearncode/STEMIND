// Add CSRF token for AJAX requests
document.addEventListener('DOMContentLoaded', function() {
    // Create CSRF token element if it doesn't exist
    if (!document.querySelector('[name=csrfmiddlewaretoken]')) {
        const csrfToken = document.createElement('input');
        csrfToken.type = 'hidden';
        csrfToken.name = 'csrfmiddlewaretoken';
        csrfToken.value = '{{ csrf_token }}';
        document.body.appendChild(csrfToken);
    }
});
document.addEventListener('DOMContentLoaded', function() {
    // Hide loading overlay after a delay if onload events don't trigger
    setTimeout(hideLoading, 3000);
});

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function shareFile() {
    if (navigator.share) {
        navigator.share({
            title: '{{ file.title }}',
            text: '{{ file.file_description|truncatechars:100 }}',
            url: window.location.href
        });
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Đã sao chép liên kết vào clipboard!');
        });
    }
}

function reportFile() {
    if (confirm('Bạn có chắc chắn muốn báo cáo tài liệu này?')) {
        alert('Cảm ơn bạn đã báo cáo. Chúng tôi sẽ xem xét trong thời gian sớm nhất.');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // cookie = "csrftoken=abc123"
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleFavorite() {
    const fileId = document.getElementById('favoriteBtn').getAttribute('data-file-id');
    const btn = document.getElementById('favoriteBtn');
    const icon = document.getElementById('favoriteIcon');
    const text = document.getElementById('favoriteText');
    
    fetch(`/toggle-favorite/${fileId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.is_favorited) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                text.textContent = 'Bỏ yêu thích';
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-danger');
            } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
                text.textContent = 'Thêm vào yêu thích';
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-danger');
            }
            
            // Show success message
            const toast = document.createElement('div');
            toast.className = 'alert alert-success position-fixed';
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
            toast.textContent = data.message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra. Vui lòng thử lại.');
    });
}

// Track file views (could be enhanced with analytics)
if (typeof gtag !== 'undefined') {
    gtag('event', 'file_view', {
        'file_title': '{{ file.title }}',
        'file_author': '{{ file.author.username }}'
    });
}