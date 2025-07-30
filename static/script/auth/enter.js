document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Enhanced form validation
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username');
        const password = document.getElementById('password');
        let isValid = true;
        
        // Reset validation
        [username, password].forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
        
        // Validate username
        if (!username.value.trim()) {
            username.classList.add('is-invalid');
            isValid = false;
        } else {
            username.classList.add('is-valid');
        }
        
        // Validate password
        if (!password.value) {
            password.classList.add('is-invalid');
            isValid = false;
        } else {
            password.classList.add('is-valid');
        }
        
        if (isValid) {
            // Show loading state
            submitBtn.classList.add('btn-loading');
            submitBtn.innerHTML = '<span><i class="fas fa-sign-in-alt me-2"></i>Đăng nhập</span>';
            
            // Submit form after short delay for UX
            setTimeout(() => {
                form.submit();
            }, 500);
        } else {
            // Shake animation for invalid form
            form.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => {
                form.style.animation = '';
            }, 500);
        }
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.value.trim()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
    
    // Remember me functionality
    const rememberMe = document.getElementById('rememberMe');
    const username = document.getElementById('username');
    
    // Load saved username
    if (localStorage.getItem('remembered_username')) {
        username.value = localStorage.getItem('remembered_username');
        rememberMe.checked = true;
    }
    
    // Save username on form submit
    form.addEventListener('submit', function() {
        if (rememberMe.checked) {
            localStorage.setItem('remembered_username', username.value);
        } else {
            localStorage.removeItem('remembered_username');
        }
    });
});

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(inputId + 'ToggleIcon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Social login placeholder functions
function socialLogin(provider) {
    // Placeholder for social login implementation
    alert(`Đăng nhập với ${provider} sẽ được triển khai sớm!`);
}

// Shake animation CSS
const shakeCSS = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}
`;

// Add shake animation to page
const style = document.createElement('style');
style.textContent = shakeCSS;
document.head.appendChild(style);