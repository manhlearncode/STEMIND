from django.contrib import messages

def add_point_notification(request, message, message_type='success'):
    """
    Add point notification to session that will be displayed on the next page load
    """
    if not hasattr(request, 'session'):
        return
    
    # Store in session for next page load
    if 'point_notifications' not in request.session:
        request.session['point_notifications'] = []
    
    request.session['point_notifications'].append({
        'message': message,
        'type': message_type
    })
    request.session.modified = True

def get_and_clear_point_notifications(request):
    """
    Get point notifications from session and clear them
    """
    if not hasattr(request, 'session'):
        return []
    
    notifications = request.session.get('point_notifications', [])
    if notifications:
        request.session['point_notifications'] = []
        request.session.modified = True
    
    return notifications
