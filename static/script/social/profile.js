// Tab switching
document.querySelectorAll('.profile-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Remove active class from all tabs
        document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        this.classList.add('active');
        
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        // Show selected tab content
        const tabName = this.dataset.tab;
        document.getElementById(tabName + '-tab').style.display = 'block';
    });
});

// Follow functionality
document.querySelector('.follow-button')?.addEventListener('click', function() {
    const username = this.dataset.username;
    
    fetch(`/social/follow/${username}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_following) {
            this.textContent = 'Following';
            this.classList.add('following');
        } else {
            this.textContent = 'Follow';
            this.classList.remove('following');
        }
        
        // Update followers count
        document.querySelector('.stat-number').textContent = data.followers_count;
    })
    .catch(error => {
        console.error('Error:', error);
    });
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