// Use global point notification system if available
function showPointNotification(message, type = 'success') {
    if (typeof window.showPointNotification === 'function') {
        return window.showPointNotification(message, type);
    }
    
    // Fallback for older browsers or if global system not loaded
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
    
    // Choose icon based on type
    const icon = type === 'success' ? 'fa-coins' : 'fa-exclamation-triangle';
    
    notification.innerHTML = `
        <i class="fas ${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 4000);
}

// Character counter
document.querySelector('.post-input').addEventListener('input', function() {
    const maxLength = 500;
    const currentLength = this.value.length;
    const remaining = maxLength - currentLength;
    
    document.getElementById('charCount').textContent = remaining;
    document.getElementById('postButton').disabled = currentLength === 0;
    
    if (remaining < 0) {
        document.getElementById('charCount').style.color = '#f91880';
    } else {
        document.getElementById('charCount').style.color = '#536471';
    }
});

// Like functionality
document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const postId = this.dataset.postId;
        const likeCount = this.querySelector('.like-count');
        
        fetch(`/social/like/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            likeCount.textContent = data.like_count;
            if (data.liked) {
                this.classList.add('liked');
                // Show point notification if available
                if (data.point_message) {
                    showPointNotification(data.point_message, 'success');
                }
            } else {
                this.classList.remove('liked');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

// Comment functionality
document.querySelectorAll('.comment-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const postId = this.dataset.postId;
        const commentsSection = document.getElementById(`comments-${postId}`);
        
        if (commentsSection.style.display === 'none') {
            commentsSection.style.display = 'block';
            this.classList.add('commented');
        } else {
            commentsSection.style.display = 'none';
            this.classList.remove('commented');
        }
    });
});

// Comment form submission
document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const postId = this.dataset.postId;
        const input = this.querySelector('.comment-input');
        const content = input.value.trim();
        
        console.log('Submitting comment for post:', postId, 'Content:', content);
        if (!content) return;
        
        // Try using FormData instead of JSON for better compatibility
        const formData = new FormData();
        formData.append('content', content);
        
        fetch(`/social/comment/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: formData
        })
        .then(response => {
            console.log('Comment response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Comment response data:', data);
            if (data.success) {
                // Add new comment to the list
                const commentsList = document.getElementById(`comments-list-${postId}`);
                const newComment = document.createElement('div');
                newComment.className = 'comment-item';
                newComment.innerHTML = `
                    <div class="comment-avatar">
                        ${data.user_avatar}
                    </div>
                    <div class="comment-content">
                        <div class="comment-header">
                            <span class="comment-author">${data.user}</span>
                            <span class="comment-time">Just now</span>
                        </div>
                        <div class="comment-text">${data.content}</div>
                    </div>
                `;
                commentsList.appendChild(newComment);
                
                // Update comment count
                const commentCount = document.querySelector(`[data-post-id="${postId}"].comment-btn .comment-count`);
                commentCount.textContent = parseInt(commentCount.textContent) + 1;
                
                // Clear input
                input.value = '';
                
                // Show point notification if available
                if (data.point_message) {
                    showPointNotification(data.point_message, 'success');
                }
            } else {
                console.error('Error adding comment:', data.error);
                alert('Failed to add comment. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

// Share functionality
function sharePost(postId) {
    if (navigator.share) {
        navigator.share({
            title: 'Check out this post on STEMind',
            text: 'Interesting post from the STEM community',
            url: window.location.origin + `/social/post/${postId}/`
        }).then(() => {
            // Show point notification for sharing
            showPointNotification('+5 points for sharing post!', 'success');
        });
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(window.location.origin + `/social/post/${postId}/`).then(() => {
            alert('Post link copied to clipboard!');
            // Show point notification for sharing
            showPointNotification('+5 points for sharing post!', 'success');
        });
    }
}

// Follow functionality with point notification
document.addEventListener('click', function(e) {
    if (e.target.closest('.follow-btn')) {
        const followBtn = e.target.closest('.follow-btn');
        const username = followBtn.dataset.username;
        
        fetch(`/social/follow/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update follow button state
                if (data.is_following) {
                    followBtn.classList.add('following');
                    followBtn.textContent = 'Following';
                } else {
                    followBtn.classList.remove('following');
                    followBtn.textContent = 'Follow';
                }
                
                // Show point notification if available
                if (data.message && data.message.includes('points')) {
                    const pointMessage = data.message.split('. ').pop(); // Get the point message part
                    showPointNotification(pointMessage, 'success');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

// Image preview
document.getElementById('image').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // You can add image preview functionality here
            console.log('Image selected:', file.name);
        };
        reader.readAsDataURL(file);
    }
});