from django.urls import path
import core.views as core_views
urlpatterns = [
 path('statSummary/', core_views.StatSummary.as_view()),
 path('records/', core_views.Records.as_view()),
]