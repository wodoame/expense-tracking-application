import traceback
from django.http import HttpResponseServerError
from .models import ErrorLog

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Log unhandled exceptions
        ErrorLog.objects.create(
            message=str(exception),
            user=request.user if request.user.is_authenticated else None,
            stack_trace=''.join(traceback.format_exc()),
            request_path=request.path,
            status_code=500,
            level='ERROR',
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return HttpResponseServerError('Internal Server Error')