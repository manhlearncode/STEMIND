document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const realTimeResults = document.getElementById('realTimeResults');
    const realTimeList = document.getElementById('realTimeList');
    const mainResults = document.getElementById('mainResults');
    
    let searchTimeout;
    let isSearching = false;

    // Real-time search with debounce
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(searchTimeout);
        
        // Hide real-time results if query is empty
        if (!query) {
            realTimeResults.style.display = 'none';
            return;
        }
        
        // Set new timeout for debounce (500ms)
        searchTimeout = setTimeout(() => {
            performRealTimeSearch(query);
        }, 500);
    });

    // Handle form submission
    const searchForm = document.querySelector('.search-form');
    searchForm.addEventListener('submit', function(e) {
        const query = searchInput.value.trim();
        if (!query) {
            e.preventDefault();
            showMessage('Vui lòng nhập từ khóa tìm kiếm', 'warning');
            return;
        }
    });

    // Perform real-time search
    function performRealTimeSearch(query) {
        if (isSearching) return;
        
        isSearching = true;
        showLoading();
        
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                isSearching = false;
                displayRealTimeResults(data.files, query);
            })
            .catch(error => {
                isSearching = false;
                console.error('Search error:', error);
                showMessage('Có lỗi xảy ra khi tìm kiếm', 'error');
            });
    }

    // Display real-time search results
    function displayRealTimeResults(files, query) {
        if (files.length === 0) {
            realTimeResults.style.display = 'none';
            return;
        }

        realTimeList.innerHTML = '';
        
        files.forEach(file => {
            const item = document.createElement('div');
            item.className = 'real-time-item';
            item.innerHTML = `
                <div class="file-thumbnail">
                    <img src="/static/images/default.webp" alt="${file.title}" class="img-fluid" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
                </div>
                <div class="file-info">
                    <div class="file-title">${highlightQuery(file.title, query)}</div>
                    <div class="file-meta">
                        <span class="category-badge">${file.category}</span>
                        <span class="author">bởi ${file.author}</span>
                        <span class="status ${file.status === 'Free' ? 'free' : 'paid'}">${file.status}</span>
                    </div>
                </div>
            `;
            
            // Add click event to navigate to file detail
            item.addEventListener('click', () => {
                window.location.href = file.url;
            });
            
            realTimeList.appendChild(item);
        });
        
        realTimeResults.style.display = 'block';
    }

    // Highlight search query in results
    function highlightQuery(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    // Show loading state
    function showLoading() {
        realTimeList.innerHTML = `
            <div class="text-center py-3">
                <div class="loading"></div>
                <p class="text-muted mt-2">Đang tìm kiếm...</p>
            </div>
        `;
        realTimeResults.style.display = 'block';
    }

    // Show message
    function showMessage(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.search-results .container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Filter functionality
    const filterSelects = document.querySelectorAll('.search-filters select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Auto-submit form when filters change
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Keyboard navigation for real-time results
    let selectedIndex = -1;
    const realTimeItems = [];

    searchInput.addEventListener('keydown', function(e) {
        const items = realTimeList.querySelectorAll('.real-time-item');
        
        if (items.length === 0) return;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelection(items);
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection(items);
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && items[selectedIndex]) {
                    items[selectedIndex].click();
                } else {
                    // Submit form if no item is selected
                    searchForm.submit();
                }
                break;
            case 'Escape':
                realTimeResults.style.display = 'none';
                selectedIndex = -1;
                break;
        }
    });

    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.style.backgroundColor = '#e3f2fd';
                item.style.borderLeft = '3px solid #006056';
            } else {
                item.style.backgroundColor = '';
                item.style.borderLeft = '';
            }
        });
    }

    // Click outside to close real-time results
    document.addEventListener('click', function(e) {
        if (!realTimeResults.contains(e.target) && e.target !== searchInput) {
            realTimeResults.style.display = 'none';
            selectedIndex = -1;
        }
    });

    // Report file function
    window.reportFile = function() {
        if (confirm('Bạn có chắc chắn muốn báo cáo tài liệu này?')) {
            alert('Cảm ơn bạn đã báo cáo. Chúng tôi sẽ xem xét trong thời gian sớm nhất.');
        }
    };

    // Initialize search input focus
    searchInput.focus();
    
    // Add search suggestions
    const suggestions = [
        'Toán học', 'Vật lý', 'Hóa học', 'Sinh học', 
        'Công nghệ', 'Kỹ thuật', 'Bài giảng', 'Thí nghiệm',
        'Giáo án', 'Đề thi', 'Tài liệu', 'STEM'
    ];
    
    let suggestionIndex = 0;
    
    // Auto-complete functionality
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length < 2) return;
        
        const matchingSuggestion = suggestions.find(s => 
            s.toLowerCase().includes(query) && s.toLowerCase() !== query
        );
        
        if (matchingSuggestion) {
            // Show suggestion (you can implement this as a dropdown)
            // For now, we'll just log it
            console.log('Suggestion:', matchingSuggestion);
        }
    });

    // Add search analytics
    function trackSearch(query, results) {
        // You can implement analytics tracking here
        console.log(`Search: "${query}" returned ${results} results`);
    }

    // Enhanced search with filters
    const filterForm = document.querySelector('.search-form');
    const filterInputs = filterForm.querySelectorAll('input, select');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Add visual feedback for active filters
            const activeFilters = Array.from(filterInputs)
                .filter(input => input.value && input.value !== '')
                .length;
            
            if (activeFilters > 0) {
                filterForm.classList.add('has-filters');
            } else {
                filterForm.classList.remove('has-filters');
            }
        });
    });

    // Add search history (localStorage)
    function saveSearchHistory(query) {
        let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        history = history.filter(item => item !== query);
        history.unshift(query);
        history = history.slice(0, 10); // Keep only last 10 searches
        localStorage.setItem('searchHistory', JSON.stringify(history));
    }

    function getSearchHistory() {
        return JSON.parse(localStorage.getItem('searchHistory') || '[]');
    }

    // Show search history on focus
    searchInput.addEventListener('focus', function() {
        const history = getSearchHistory();
        if (history.length > 0 && !this.value) {
            // You can implement a dropdown to show search history
            console.log('Search history:', history);
        }
    });
}); 