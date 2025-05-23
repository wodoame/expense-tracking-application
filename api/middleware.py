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
        stack_trace = ''.join(traceback.format_exc())
        # Avoid logging the same error multiple times
        if ErrorLog.objects.filter(stack_trace=stack_trace).exists():
            return None
        
        # Log unhandled exceptions
        ErrorLog.objects.create(
            message=str(exception),
            user=request.user if request.user.is_authenticated else None,
            stack_trace=stack_trace,
            request_path=request.path,
            status_code=500,
            level='ERROR',
            method=request.method,
            get_data=request.GET.dict(),
            post_data=request.POST.dict(),
            ip_address=request.META.get('REMOTE_ADDR'),
            error_type=exception.__class__.__name__,
        )
        return HttpResponseServerError('Internal Server Error')