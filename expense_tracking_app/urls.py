"""
URL configuration for expense_tracking_app project.

The `urlpatterns` list implementations URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import core.views as core_views
import authentication.views as auth_views
import core.placeholder_views as placeholder_views

handler404 = 'authentication.views.not_found_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/callback/', auth_views.AuthCallback.as_view(), name='auth-callback'),
    path('api/', include('api.urls')),
    path('implementations/', include('core.urls')),
    path('components/', include('core.component_urls')),
    # path('__debug__/', include('debug_toolbar.urls')),
    path('', include("django_components.urls")),
    path('', core_views.RedirectView.as_view()),
    path('dashboard/', placeholder_views.Dashboard.as_view(), name='dashboard'),
    path('weeks/<int:pk>/', placeholder_views.Week.as_view(), name='get-a-week'),
    path('months/<int:pk>/', placeholder_views.Month.as_view(), name='get-a-month'),
    path('weeks/', placeholder_views.Weeks.as_view(), name='weeks'),
    path('days/<str:date>/', placeholder_views.Day.as_view(), name='get-a-day'),
    path('all-expenditures/', placeholder_views.AllExpenditures.as_view(), name='all-expenditures'),
    path('categories/', placeholder_views.Categories.as_view(), name='categories'),
    path('categories/<str:categoryName>/', placeholder_views.SeeProducts.as_view(), name='see-products'),
    path('components/activityCalendar/', core_views.ActivityCalendar.as_view()),
    path('settings/', core_views.Settings.as_view()),
    path('search/', core_views.Search.as_view()),
    path('signup/', auth_views.SignUp.as_view(), name='signup'),
    path('signin/', auth_views.SignIn.as_view(), name='signin'),
    path('logout/', auth_views.Logout.as_view(), name='logout'),
    path('test/', core_views.Test.as_view()),
    path('routes/', core_views.Routes.as_view()),
]
