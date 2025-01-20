import api.views as api_views
from django.urls import path

urlpatterns = [
    path('categories/', api_views.Categories.as_view())
]