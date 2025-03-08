import api.views as api_views
from django.urls import path

urlpatterns = [
    path('categories/', api_views.Categories.as_view()),
    path('search/', api_views.Search.as_view()),
    path('recreate-indexes/', api_views.RecreateIndexes.as_view()),
]