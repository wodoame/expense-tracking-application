import api.views as api_views
from django.urls import path

urlpatterns = [
    path('categories/', api_views.Categories.as_view()),
    path('search/', api_views.Search.as_view()),
    path('clear-cache/', api_views.ClearCache.as_view(), name='clear-cache'),
    path('error-logs/', api_views.ErrorLogs.as_view(), name='error-logs'),
    path('status/', api_views.Status.as_view(), name='status'),
    path('weekly-spendings/', api_views.GetWeeklySpendings.as_view(), name='weekly-spendings'),
]