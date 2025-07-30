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
// Remove favorite với AJAX
async function removeFavorite(fileId) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài liệu này khỏi danh sách yêu thích?')) {
        return;
    }
    
    try {
        const response = await fetch(`/toggle-favorite/${fileId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success && !data.is_favorited) {
            // Remove item from DOM with animation
            const item = document.getElementById(`favorite-${fileId}`);
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '0';
            item.style.transform = 'translateX(-100px)';
            
            setTimeout(() => {
                item.remove();
                
                // Check if no favorites left
                const remainingItems = document.querySelectorAll('.favorite-item');
                if (remainingItems.length === 0) {
                    location.reload(); // Reload to show empty state
                }
            }, 300);
            
            showNotification('Đã xóa khỏi danh sách yêu thích!', 'success');
        } else {
            showNotification('Có lỗi xảy ra. Vui lòng thử lại.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Không thể kết nối đến server.', 'error');
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// Add slideInRight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);   