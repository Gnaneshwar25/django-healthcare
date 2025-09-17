import time
from django.utils.deprecation import MiddlewareMixin

class CustomLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, "_start_time", time.time())
        print(f"[{request.method}] {request.path} -> {response.status_code} ({duration:.3f}s)")
        return response
