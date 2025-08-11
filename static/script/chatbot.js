// Global variables
let currentSessionId = null;
let isTyping = false;
let sessions = {};

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function() {
    loadSessions();
    initializeChat();
});

// Load sessions from localStorage
function loadSessions() {
    const savedSessions = localStorage.getItem('chatbot_sessions');
    if (savedSessions) {
        sessions = JSON.parse(savedSessions);
    }
    updateChatHistory();
}

// Save sessions to localStorage
function saveSessions() {
    localStorage.setItem('chatbot_sessions', JSON.stringify(sessions));
}

// Initialize chat
function initializeChat() {
    // Check if there's a current session
    const lastSessionId = localStorage.getItem('current_session_id');
    if (lastSessionId && sessions[lastSessionId]) {
        loadSession(lastSessionId);
    } else {
        startNewChat();
    }
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// Handle Enter key
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send message
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    const fileInput = document.getElementById('fileInput');
    const hasFile = fileInput.files.length > 0;
    
    if (!message && !hasFile) return;
    if (isTyping) return;
    
    // Hide welcome message
    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
    
    // Handle file upload
    if (hasFile) {
        uploadFile(message);
    } else {
        // Send text message
        sendTextMessage(message);
    }
    
    // Clear input and file
    input.value = '';
    autoResize(input);
    removeFile();
}

function sendTextMessage(message) {
    // Add user message
    addMessage(message, 'user');
    
    // Update session title if it's the first message
    if (!sessions[currentSessionId] || sessions[currentSessionId].messages.length === 1) {
        const title = message.length > 30 ? message.substring(0, 30) + '...' : message;
        updateSessionTitle(title);
    }
    
    // Show typing indicator
    showTypingIndicator();
    
    // Call chatbot API
    fetch('/chatbot/api/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            message: message,
            session_id: currentSessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        
        if (data.success) {
            addMessage(data.response.text, 'bot');
            currentSessionId = data.response.session_id;
            localStorage.setItem('current_session_id', currentSessionId);
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    });
}

function uploadFile(message) {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    // Add user message with file info
    const fileMessage = message || `Uploaded file: ${file.name}`;
    addMessageWithFile(fileMessage, 'user', file);
    
    // Update session title if it's the first message
    if (!sessions[currentSessionId] || sessions[currentSessionId].messages.length === 1) {
        const title = fileMessage.length > 30 ? fileMessage.substring(0, 30) + '...' : fileMessage;
        updateSessionTitle(title);
    }
    
    // Show typing indicator
    showTypingIndicator();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message', message);
    formData.append('session_id', currentSessionId || '');
    
    // Upload file
    fetch('/chatbot/upload/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        if (data.success) {
            addMessage(data.response.text, 'bot');
            
            // Show content extraction indicator if successful
            if (data.file && data.file.content_extracted) {
                // Find the user message with file attachment
                const messages = document.querySelectorAll('.message.user');
                const lastUserMessage = messages[messages.length - 1];
                if (lastUserMessage) {
                    const fileAttachment = lastUserMessage.querySelector('.file-attachment-info');
                    if (fileAttachment) {
                        const indicator = document.createElement('div');
                        indicator.className = 'content-extracted-indicator';
                        indicator.innerHTML = '<i class="fas fa-check-circle"></i> Nội dung đã được đọc';
                        fileAttachment.appendChild(indicator);
                    }
                }
            }
            
            // Update session ID if new session was created
            if (data.response.session_id) {
                currentSessionId = data.response.session_id;
            }
        } else {
            addMessage(`Lỗi upload file: ${data.error}`, 'bot');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Upload error:', error);
    });
}

// Send suggestion
function sendSuggestion(suggestion) {
    document.getElementById('chatInput').value = suggestion;
    sendMessage();
}

// Add message to chat
function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? 
        '{{ user.username|slice:":1"|upper|default:"U" }}' : 
        '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.innerHTML = formatMessage(text);
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString();
    
    content.appendChild(messageText);
    content.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Save message to session
    saveMessageToSession(text, sender);
}

// Format message
function formatMessage(text) {
    // Convert URLs to links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: inherit; text-decoration: underline;">$1</a>');
    
    // Convert code blocks
    text = text.replace(/```([\s\S]*?)```/g, '<pre style="background: #f4f4f4; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; overflow-x: auto;"><code>$1</code></pre>');
    
    // Convert inline code
    text = text.replace(/`([^`]+)`/g, '<code style="background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px;">$1</code>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Show typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    isTyping = true;
    
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    content.appendChild(typingIndicator);
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Session management
function startNewChat() {
    currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    
    // Create new session
    sessions[currentSessionId] = {
        id: currentSessionId,
        title: 'New Chat',
        messages: [],
        createdAt: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
    };
    
    // Clear chat
    document.getElementById('chatTitle').textContent = 'New Chat';
    document.getElementById('chatMessages').innerHTML = `
        <div class="welcome-container" id="welcomeMessage">
            <div class="welcome-icon">
                <i class="fas fa-robot"></i>
            </div>
            <h1 class="welcome-title">How can I help you today?</h1>
            <p class="welcome-subtitle">
                I'm your AI assistant. I can help you with questions, provide information, 
                and assist with various tasks. Feel free to ask me anything!
            </p>
            
            <div class="suggestion-grid">
                <div class="suggestion-card" onclick="sendSuggestion('Tell me about STEM education')">
                    <div class="suggestion-title">STEM Education</div>
                    <div class="suggestion-text">Learn about Science, Technology, Engineering, and Mathematics education</div>
                </div>
                <div class="suggestion-card" onclick="sendSuggestion('Help me with a coding problem')">
                    <div class="suggestion-title">Coding Help</div>
                    <div class="suggestion-text">Get assistance with programming and development questions</div>
                </div>
                <div class="suggestion-card" onclick="sendSuggestion('Explain a scientific concept')">
                    <div class="suggestion-title">Science Concepts</div>
                    <div class="suggestion-text">Understand complex scientific theories and principles</div>
                </div>
                <div class="suggestion-card" onclick="sendSuggestion('Create a lesson plan')">
                    <div class="suggestion-title">Lesson Planning</div>
                    <div class="suggestion-text">Design educational activities and curriculum</div>
                </div>
            </div>
        </div>
    `;
    
    // Save and update
    localStorage.setItem('current_session_id', currentSessionId);
    saveSessions();
    updateChatHistory();
}

function saveMessageToSession(message, sender) {
    if (!currentSessionId || !sessions[currentSessionId]) return;
    
    const messageObj = {
        text: message,
        sender: sender,
        timestamp: new Date().toISOString()
    };
    
    sessions[currentSessionId].messages.push(messageObj);
    sessions[currentSessionId].lastUpdated = new Date().toISOString();
    
    saveSessions();
}

function updateSessionTitle(title) {
    if (!currentSessionId || !sessions[currentSessionId]) return;
    
    sessions[currentSessionId].title = title;
    document.getElementById('chatTitle').textContent = title;
    
    saveSessions();
    updateChatHistory();
}

function loadSession(sessionId) {
    if (!sessions[sessionId]) return;
    
    currentSessionId = sessionId;
    const session = sessions[sessionId];
    
    // Update UI
    document.getElementById('chatTitle').textContent = session.title;
    document.getElementById('chatMessages').innerHTML = '';
    
    // Load messages
    if (session.messages.length === 0) {
        document.getElementById('welcomeMessage').style.display = 'block';
    } else {
        session.messages.forEach(msg => {
            addMessageToUI(msg.text, msg.sender, msg.timestamp);
        });
    }
    
    // Save current session
    localStorage.setItem('current_session_id', currentSessionId);
    updateChatHistory();
}

            function addMessageToUI(text, sender, timestamp) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? 
            '{{ user.username|slice:":1"|upper|default:"U" }}' : 
            '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = formatMessage(text);
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date(timestamp).toLocaleTimeString();
        
        content.appendChild(messageText);
        content.appendChild(time);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addMessageWithFile(text, sender, file) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? 
            '{{ user.username|slice:":1"|upper|default:"U" }}' : 
            '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        // File attachment display
        if (file) {
            const fileAttachment = document.createElement('div');
            fileAttachment.className = 'message-file-attachment';
            fileAttachment.innerHTML = `
                <div class="file-attachment-content">
                    <i class="fas fa-file file-attachment-icon"></i>
                    <div class="file-attachment-info">
                        <div class="file-attachment-name">${file.name}</div>
                        <div class="file-attachment-size">${formatBytes(file.size)}</div>
                    </div>
                </div>
            `;
            content.appendChild(fileAttachment);
        }
        
        if (text) {
            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.innerHTML = formatMessage(text);
            content.appendChild(messageText);
        }
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString();
        
        content.appendChild(time);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save message to session
        saveMessageToSession(text || `Uploaded file: ${file.name}`, sender);
    }

function updateChatHistory() {
    const historyContainer = document.getElementById('chatHistory');
    historyContainer.innerHTML = '';
    
    // Sort sessions by last updated
    const sortedSessions = Object.values(sessions)
        .sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
    
    sortedSessions.forEach(session => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        if (session.id === currentSessionId) {
            chatItem.classList.add('active');
        }
        
        chatItem.onclick = () => loadSession(session.id);
        
        const icon = document.createElement('div');
        icon.className = 'chat-item-icon';
        icon.innerHTML = '<i class="fas fa-comment"></i>';
        
        const title = document.createElement('div');
        title.className = 'chat-item-title';
        title.textContent = session.title;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-item-delete';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteSession(session.id);
        };
        
        chatItem.appendChild(icon);
        chatItem.appendChild(title);
        chatItem.appendChild(deleteBtn);
        historyContainer.appendChild(chatItem);
    });
}

function deleteSession(sessionId) {
    if (confirm('Are you sure you want to delete this chat?')) {
        delete sessions[sessionId];
        
        if (sessionId === currentSessionId) {
            startNewChat();
        }
        
        saveSessions();
        updateChatHistory();
    }
}

// Utility functions
function clearChat() {
    if (confirm('Are you sure you want to clear this chat?')) {
        if (currentSessionId && sessions[currentSessionId]) {
            sessions[currentSessionId].messages = [];
            sessions[currentSessionId].title = 'New Chat';
            sessions[currentSessionId].lastUpdated = new Date().toISOString();
            
            document.getElementById('chatTitle').textContent = 'New Chat';
            document.getElementById('chatMessages').innerHTML = `
                <div class="welcome-container" id="welcomeMessage">
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h1 class="welcome-title">How can I help you today?</h1>
                    <p class="welcome-subtitle">
                        I'm your AI assistant. I can help you with questions, provide information, 
                        and assist with various tasks. Feel free to ask me anything!
                    </p>
                    
                    <div class="suggestion-grid">
                        <div class="suggestion-card" onclick="sendSuggestion('Tell me about STEM education')">
                            <div class="suggestion-title">STEM Education</div>
                            <div class="suggestion-text">Learn about Science, Technology, Engineering, and Mathematics education</div>
                        </div>
                        <div class="suggestion-card" onclick="sendSuggestion('Help me with a coding problem')">
                            <div class="suggestion-title">Coding Help</div>
                            <div class="suggestion-text">Get assistance with programming and development questions</div>
                        </div>
                        <div class="suggestion-card" onclick="sendSuggestion('Explain a scientific concept')">
                            <div class="suggestion-title">Science Concepts</div>
                            <div class="suggestion-text">Understand complex scientific theories and principles</div>
                        </div>
                        <div class="suggestion-card" onclick="sendSuggestion('Create a lesson plan')">
                            <div class="suggestion-title">Lesson Planning</div>
                            <div class="suggestion-text">Design educational activities and curriculum</div>
                        </div>
                    </div>
                </div>
            `;
            
            saveSessions();
            updateChatHistory();
        }
    }
}

// TEMPORARILY DISABLED - Export functionality
// function exportChat() {
//     if (!currentSessionId || !sessions[currentSessionId] || sessions[currentSessionId].messages.length === 0) {
//         alert('No messages to export');
//         return;
//     }
//     
//     const session = sessions[currentSessionId];
//     const exportData = {
//         title: session.title,
//         createdAt: session.createdAt,
//         lastUpdated: session.lastUpdated,
//         messages: session.messages
//     };
//     
//     const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = `chat_${session.title.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.json`;
//     a.click();
//     URL.revokeObjectURL(url);
// }

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
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

// File upload handling
function openFileDialog() {
    document.getElementById('fileInput').click();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const filePreview = document.getElementById('filePreview');
        filePreview.style.display = 'flex';
        filePreview.querySelector('.file-name').textContent = file.name;
        filePreview.querySelector('.file-size').textContent = formatBytes(file.size);
    }
}

function removeFile() {
    document.getElementById('fileInput').value = ''; // Clear the file input
    document.getElementById('filePreview').style.display = 'none';
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    
    if (window.innerWidth <= 768 && 
        !sidebar.contains(event.target) && 
        !sidebarToggle.contains(event.target) &&
        sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
    }
});