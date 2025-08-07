// Test function to debug follow
function testFollow(username) {
    console.log('Test follow function called with username:', username);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    console.log('CSRF token found:', csrfToken);
    alert(`Testing follow for ${username}. Check console for details.`);
}

// Message notification function
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.toast-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `toast-message toast-${type}`;
    messageDiv.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile page loaded');
    console.log('Follow button found:', document.querySelector('#followBtn'));
    
    // Simple tab switching with event delegation
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('nav-btn') || e.target.closest('.nav-btn')) {
            const button = e.target.classList.contains('nav-btn') ? e.target : e.target.closest('.nav-btn');
            const tabName = button.dataset.tab;
            
            console.log('Tab clicked:', tabName);
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Hide all tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Show selected tab content
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.classList.add('active');
                console.log('Successfully switched to tab:', tabName);
            } else {
                console.error('Tab element not found:', tabName + '-tab');
            }
        }
    });

    // Follow functionality
    const followBtn = document.querySelector('#followBtn');
    console.log('Setting up follow button:', followBtn);
    
    if (followBtn) {
        console.log('Follow button found, adding click listener...');
        
        followBtn.onclick = function(e) {
            alert('Button clicked! Testing...');
            console.log('Follow button clicked via onclick');
            
            e.preventDefault();
            const username = this.dataset.username;
            const button = this;
            
            console.log('Username:', username);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            console.log('CSRF token element:', csrfToken);
            
            if (!csrfToken) {
                console.error('CSRF token not found');
                alert('CSRF token not found. Please refresh the page.');
                return;
            }
            
            // Disable button during request
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            console.log('Sending follow request to:', `/social/follow/${username}/`);
            
            fetch(`/social/follow/${username}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken.value,
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                
                if (data.success) {
                    // Update button text and style
                    if (data.is_following) {
                        button.innerHTML = '<i class="fas fa-user-minus"></i> Bỏ theo dõi';
                        button.classList.add('following');
                        button.classList.remove('btn-primary');
                        button.classList.add('btn-secondary');
                    } else {
                        button.innerHTML = '<i class="fas fa-user-plus"></i> Theo dõi';
                        button.classList.remove('following');
                        button.classList.remove('btn-secondary');
                        button.classList.add('btn-primary');
                    }
                    
                    // Update followers count
                    const followersCountElement = document.querySelector('.stat-link .stat-number');
                    console.log('Followers count element:', followersCountElement);
                    
                    if (followersCountElement) {
                        followersCountElement.textContent = data.followers_count;
                    }
                    
                    alert(data.message);
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
            })
            .catch(error => {
                console.error('Follow error:', error);
                button.innerHTML = originalText;
                alert('An error occurred: ' + error.message);
            })
            .finally(() => {
                button.disabled = false;
            });
        };
    } else {
        console.log('Follow button not found on this page');
    }

    // Like functionality
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const likeCount = this.querySelector('span');
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfToken) {
                console.error('CSRF token not found');
                return;
            }
            
            fetch(`/social/like/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken.value,
                }
            })
            .then(response => response.json())
            .then(data => {
                likeCount.textContent = data.like_count;
                const icon = this.querySelector('i');
                if (data.liked) {
                    icon.classList.add('liked');
                } else {
                    icon.classList.remove('liked');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});