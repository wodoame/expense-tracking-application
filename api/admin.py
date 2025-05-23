from django.contrib import admin
from .models import ErrorLog

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'user', 'timestamp', 'request_path')
    list_filter = ('level', 'user', 'timestamp')
    search_fields = ('message', 'request_path')