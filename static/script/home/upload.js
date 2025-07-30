document.addEventListener('DOMContentLoaded', function() {
    const dragDropArea = document.getElementById('dragDropArea');
    const fileInput = document.getElementById('fileInput');
    const selectedFile = document.getElementById('selectedFile');
    const progressBar = document.getElementById('progressBar');
    const thumbnailInput = document.querySelector('input[type="file"][accept="image/*"]');
    const thumbnailPreview = document.getElementById('thumbnailPreview');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const fileStatusSelect = document.querySelector('select[id*="file_status"]');
    const priceField = document.getElementById('priceField');

    // Initialize price field visibility
    updatePriceVisibility();

    // Add event listener for file status change
    if (fileStatusSelect) {
        fileStatusSelect.addEventListener('change', updatePriceVisibility);
    }

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, unhighlight, false);
    });

    dragDropArea.addEventListener('drop', handleDrop, false);
    dragDropArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFiles);

    // Thumbnail preview functionality
    if (thumbnailInput) {
        thumbnailInput.addEventListener('change', handleThumbnailPreview);
    }

    // Form submission with validation
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang tải lên...';
            
            // Validate price for paid files
            const statusValue = fileStatusSelect ? fileStatusSelect.value : '0';
            const priceInput = priceField ? priceField.querySelector('input') : null;
            
            if (statusValue === '1' && priceInput) {
                const price = parseInt(priceInput.value) || 0;
                if (price <= 0) {
                    e.preventDefault();
                    alert('Vui lòng nhập giá cho tài liệu có phí.');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Tải lên tài liệu';
                    return;
                }
            }
        });
    }

    function updatePriceVisibility() {
        if (fileStatusSelect && priceField) {
            const selectedValue = fileStatusSelect.value;
            const priceInput = priceField.querySelector('input');
            
            if (selectedValue === '1') { // For sales
                priceField.style.display = 'block';
                if (priceInput) {
                    priceInput.required = true;
                    priceInput.min = '1000';
                }
            } else { // Free
                priceField.style.display = 'none';
                if (priceInput) {
                    priceInput.required = false;
                    priceInput.value = '0';
                }
            }
        }
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dragDropArea.classList.add('drag-over');
    }

    function unhighlight(e) {
        dragDropArea.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles();
    }

    function handleFiles() {
        const files = fileInput.files;
        if (files.length > 0) {
            const file = files[0];
            
            // Validate file size (50MB)
            if (file.size > 50 * 1024 * 1024) {
                alert('Kích thước tệp quá lớn! Vui lòng chọn tệp nhỏ hơn 50MB.');
                fileInput.value = '';
                resetUploadArea();
                return;
            }
            
            // Validate file type
            const allowedTypes = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedTypes.includes(fileExtension)) {
                alert('Định dạng tệp không được hỗ trợ! Vui lòng chọn tệp PDF, Word, PowerPoint, Excel, Text, ZIP hoặc RAR.');
                fileInput.value = '';
                resetUploadArea();
                return;
            }
            
            displaySelectedFile(file);
        }
    }

    function displaySelectedFile(file) {
        const fileName = file.name;
        const fileSize = formatFileSize(file.size);
        
        selectedFile.querySelector('.file-name').textContent = fileName;
        selectedFile.querySelector('.file-size').textContent = fileSize;
        selectedFile.style.display = 'block';
        
        // Update drag drop area
        dragDropArea.querySelector('.upload-content').innerHTML = `
            <i class="fas fa-check-circle upload-icon" style="color: #28a745;"></i>
            <h4 style="color: #28a745;">Tệp đã được chọn!</h4>
            <p class="text-muted">Click để chọn tệp khác</p>
        `;
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function handleThumbnailPreview(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                thumbnailPreview.src = e.target.result;
                thumbnailPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    function resetUploadArea() {
        selectedFile.style.display = 'none';
        dragDropArea.querySelector('.upload-content').innerHTML = `
            <i class="fas fa-cloud-upload-alt upload-icon"></i>
            <h4>Kéo thả tệp vào đây hoặc click để chọn</h4>
            <p class="text-muted">Hỗ trợ: PDF, Word, PowerPoint, Excel, Text, ZIP, RAR</p>
            <p class="text-muted">Kích thước tối đa: 50MB</p>
        `;
    }

    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    });
});

// Global function for price visibility (called from form onchange)
function updatePriceVisibility() {
    const fileStatusSelect = document.querySelector('select[id*="file_status"]');
    const priceField = document.getElementById('priceField');
    
    if (fileStatusSelect && priceField) {
        const selectedValue = fileStatusSelect.value;
        const priceInput = priceField.querySelector('input');
        
        if (selectedValue === '1') { // For sales
            priceField.style.display = 'block';
            if (priceInput) {
                priceInput.required = true;
                priceInput.min = '1000';
            }
        } else { // Free
            priceField.style.display = 'none';
            if (priceInput) {
                priceInput.required = false;
                priceInput.value = '0';
            }
        }
    }
}