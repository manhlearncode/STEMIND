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
                // Remove post from liked posts page
                const postItem = document.getElementById(`post-${postId}`);
                if (postItem) {
                    postItem.style.transition = 'all 0.3s ease';
                    postItem.style.opacity = '0';
                    postItem.style.transform = 'translateX(-100px)';
                    
                    setTimeout(() => {
                        postItem.remove();
                        
                        // Check if no posts left
                        const remainingPosts = document.querySelectorAll('.post-item');
                        if (remainingPosts.length === 0) {
                            location.reload(); // Reload to show empty state
                        }
                    }, 300);
                }
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