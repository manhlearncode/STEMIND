// Global Point Notification System
class PointNotificationManager {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 3;
    }

    // Show point notification
    show(message, type = 'success', duration = 4000) {
        // Remove old notifications if we have too many
        if (this.notifications.length >= this.maxNotifications) {
            this.removeOldest();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `point-notification ${type} alert alert-dismissible fade show`;
        
        // Choose icon based on type
        const icon = this.getIconForType(type);
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            ${message}
            <button type="button" class="btn-close" onclick="pointNotificationManager.remove(this.parentElement)"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Store reference
        this.notifications.push({
            element: notification,
            timestamp: Date.now()
        });
        
        // Auto remove after duration
        setTimeout(() => {
            this.remove(notification);
        }, duration);
        
        return notification;
    }

    // Remove specific notification
    remove(notification) {
        if (notification && notification.parentElement) {
            notification.classList.add('removing');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
                // Remove from our array
                this.notifications = this.notifications.filter(n => n.element !== notification);
            }, 300);
        }
    }

    // Remove oldest notification
    removeOldest() {
        if (this.notifications.length > 0) {
            const oldest = this.notifications.shift();
            this.remove(oldest.element);
        }
    }

    // Get icon for notification type
    getIconForType(type) {
        switch (type) {
            case 'success':
                return 'fa-coins';
            case 'warning':
                return 'fa-exclamation-triangle';
            case 'danger':
                return 'fa-times-circle';
            default:
                return 'fa-info-circle';
        }
    }

    // Clear all notifications
    clearAll() {
        this.notifications.forEach(notification => {
            this.remove(notification.element);
        });
        this.notifications = [];
    }
}

// Global instance
window.pointNotificationManager = new PointNotificationManager();

// Global function for easy access
window.showPointNotification = function(message, type = 'success', duration = 4000) {
    return window.pointNotificationManager.show(message, type, duration);
};

// Listen for point notification events
document.addEventListener('DOMContentLoaded', function() {
    // Check for point messages in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const pointMessage = urlParams.get('point_message');
    const pointType = urlParams.get('point_type') || 'success';
    
    if (pointMessage) {
        showPointNotification(pointMessage, pointType);
        // Clean up URL
        urlParams.delete('point_message');
        urlParams.delete('point_type');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState({}, '', newUrl);
    }
});

// Listen for custom point notification events
document.addEventListener('pointNotification', function(e) {
    const { message, type, duration } = e.detail;
    showPointNotification(message, type, duration);
});
