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
        
        if (!content) return;
        
        fetch(`/social/comment/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add new comment to the list
                const commentsList = document.getElementById(`comments-list-${postId}`);
                const newComment = document.createElement('div');
                newComment.className = 'comment-item';
                newComment.innerHTML = `
                    <div class="comment-avatar">
                        {{ user.username|slice:":1"|upper }}
                    </div>
                    <div class="comment-content">
                        <div class="comment-header">
                            <span class="comment-author">{{ user.get_full_name|default:user.username }}</span>
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
        });
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(window.location.origin + `/social/post/${postId}/`).then(() => {
            alert('Post link copied to clipboard!');
        });
    }
}

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