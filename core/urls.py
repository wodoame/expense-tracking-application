from django.urls import path
import core.views as core_views
urlpatterns = [
 path('dashboard/', core_views.Dashboard.as_view(), name='implemented-dashboard'),
 path('categories/', core_views.Categories.as_view(), name='implemented-categories')
]