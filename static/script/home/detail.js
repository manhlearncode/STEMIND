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
    
    // Enhanced notification handling
    enhanceNotifications();
});
document.addEventListener('DOMContentLoaded', function() {
    // Hide loading overlay after a delay if onload events don't trigger
    setTimeout(hideLoading, 3000);
    
    // Debug video loading
    const video = document.querySelector('video');
    if (video) {
        console.log('Video element found:', video.src);
        
        video.addEventListener('loadstart', () => {
            console.log('Video: Load started');
        });
        
        video.addEventListener('loadedmetadata', () => {
            console.log('Video: Metadata loaded');
        });
        
        video.addEventListener('loadeddata', () => {
            console.log('Video: Data loaded');
            hideLoading();
        });
        
        video.addEventListener('canplay', () => {
            console.log('Video: Can play');
            hideLoading();
        });
        
        video.addEventListener('error', (e) => {
            console.error('Video error:', e);
            console.error('Video error details:', video.error);
            hideLoading();
        });
    }
});

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function showVideoFallback(videoElement) {
    console.error('Video failed to load, showing fallback');
    hideLoading();
    
    // Create fallback content
    const fallbackHTML = `
        <div class="video-fallback">
            <div class="video-placeholder">
                <i class="fas fa-exclamation-triangle fa-3x mb-3" style="color: #dc3545;"></i>
                <h5>Không thể phát video</h5>
                <p class="text-muted mb-3">Video có thể bị lỗi hoặc định dạng không được hỗ trợ</p>
                <a href="${videoElement.querySelector('source').src}" 
                   class="btn btn-primary" 
                   target="_blank">
                    <i class="fas fa-download me-2"></i>Tải xuống video
                </a>
            </div>
        </div>
    `;
    
    // Replace video with fallback
    const videoViewer = videoElement.closest('.video-viewer');
    if (videoViewer) {
        videoViewer.innerHTML = fallbackHTML;
    }
}

function showAdvancedFallback(videoElement) {
    console.error('Advanced video failed to load, showing fallback options');
    hideLoading();
    
    // Hide the video element
    if (videoElement) {
        videoElement.style.display = 'none';
    }
    
    // Show the final fallback
    const container = videoElement.closest('.advanced-video-container');
    if (container) {
        const finalFallback = container.querySelector('.final-fallback');
        if (finalFallback) {
            finalFallback.style.display = 'block';
        }
    }
}

function tryAlternativeViewers(buttonElement) {
    const container = buttonElement.closest('.advanced-video-container');
    if (container) {
        const alternativeViewers = container.querySelector('.alternative-viewers');
        const finalFallback = container.querySelector('.final-fallback');
        
        if (alternativeViewers && finalFallback) {
            // Hide final fallback and show alternative viewers
            finalFallback.style.display = 'none';
            alternativeViewers.style.display = 'block';
            
            // Add back button
            const backButton = document.createElement('button');
            backButton.className = 'btn btn-outline-secondary mb-3';
            backButton.innerHTML = '<i class="fas fa-arrow-left me-2"></i>Quay lại';
            backButton.onclick = function() {
                alternativeViewers.style.display = 'none';
                finalFallback.style.display = 'block';
            };
            alternativeViewers.insertBefore(backButton, alternativeViewers.firstChild);
        }
    }
}

function openInNewTab(url) {
    window.open(url, '_blank');
}

// Add video format detection
function detectVideoFormat(filename) {
    const extension = filename.toLowerCase().split('.').pop();
    const formats = {
        'mp4': { type: 'video/mp4', supported: true },
        'webm': { type: 'video/webm', supported: true },
        'avi': { type: 'video/x-msvideo', supported: false },
        'mov': { type: 'video/quicktime', supported: false },
        'wmv': { type: 'video/x-ms-wmv', supported: false },
        'flv': { type: 'video/x-flv', supported: false },
        'mkv': { type: 'video/x-matroska', supported: false }
    };
    
    return formats[extension] || { type: 'video/mp4', supported: false };
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

// Enhanced notification system
function enhanceNotifications() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach((alert, index) => {
        // Add staggered animation delay
        alert.style.animationDelay = `${index * 0.15}s`;
        
        // Auto-hide after 6 seconds for info messages (trừ điểm)
        if (alert.classList.contains('alert-info')) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.animation = 'slideOutRight 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.remove();
                        }
                    }, 500);
                }
            }, 6000);
        }
        
        // Auto-hide after 8 seconds for success messages (cộng điểm)
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.animation = 'slideOutRight 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.remove();
                        }
                    }, 500);
                }
            }, 8000);
        }
        
        // Enhanced close button with smooth animation
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'slideOutRight 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            });
        }
        
        // Add subtle entrance effect
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%) scale(0.95)';
        
        setTimeout(() => {
            alert.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            alert.style.opacity = '1';
            alert.style.transform = 'translateX(0) scale(1)';
        }, index * 150);
    });
}

// Add slideOutRight animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0) scale(1);
            opacity: 1;
        }
        to {
            transform: translateX(100%) scale(0.95);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);