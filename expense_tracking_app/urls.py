"""
URL configuration for expense_tracking_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
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

handler404 = 'authentication.views.not_found_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('__debug__/', include('debug_toolbar.urls')),
    path('', include("django_components.urls")),
    path('', core_views.RedirectView.as_view()),
    path('dashboard/', core_views.Dashboard.as_view(), name='dashboard'),
    path('all-expenditures/', core_views.AllExpenditures.as_view(), name='all-expenditures'),
    path('components/activityCalendar/', core_views.ActivityCalendar.as_view()), 
    path('components/records/', core_views.Records.as_view()),
    path('settings/', core_views.Settings.as_view()),   
    path('categories/', core_views.CategoriesPage.as_view()),
    path('signup/', auth_views.SignUp.as_view(), name='signup'),
    path('signin/', auth_views.SignIn.as_view(), name='signin'),
    path('logout/', auth_views.Logout.as_view(), name='logout'),
    # path('complete-signup/', auth_views.CompleteSignUp.as_view(), name='complete-signup'),
    # path('components/signupContinued/', auth_views.SignUpContinued.as_view()),
    path('test/', core_views.Test.as_view()),
]
