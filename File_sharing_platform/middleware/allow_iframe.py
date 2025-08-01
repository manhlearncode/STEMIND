# main_app/middleware/allow_iframe.py

class AllowIframeForMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/media/'):
            response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response
