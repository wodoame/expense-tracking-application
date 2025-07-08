from django.shortcuts import render
from django.views import View
from .models import Category
from .utils import *
from core.templatetags.custom_filters import dateOnly
"""
    Summary
    --------
    This file contains the views which are loaded when the user enters a URL into the browser.
    They do not contain the actual content of the page, but rather the logic to load the content.
    The logic to load the main content includes page skeletons which trigger HTMX requests.
    The actual content is processed and returned by the views in the core/views.py file.
    These views serve as the layer to check user authentication via the custom @login_required decorator in core/utils.py.
    The views are also used to load the skeletons or placeholders for the pages hence the name placeholder_views.py.
"""
@login_required
class Dashboard(View):
    def get(self, request):
        context = getRecordSkeletonContext()
        return render(request, 'core/pages/dashboard.html', context)
    
@login_required    
class AllExpenditures(View):
    def get(self, request):
        context = getRecordSkeletonContext()
        return render(request, 'core/pages/allExpenditures.html', context)

@login_required
class Categories(View):
    def get(self, request):
        context = getCategoriesSkeletonContext()
        return render(request, 'core/pages/categories.html', context)

@login_required
class SeeProducts(View):
    """ 
        This view is used to load the expenses of a specific category.
        It is used to load the skeleton for the page.
        The actual content is loaded by the Records view in core/views.py.
    """
    def get(self, request, categoryName):
        user = request.user 
        try: 
            if  categoryName != 'None':
                user.categories.get(name=categoryName)
            context = getRecordSkeletonContext() 
            context.update(
                {
                    'pageHeading':categoryName, 
                }
            )
            return render(request, 'core/pages/see-products.html', context)
        except Category.DoesNotExist:
            return render(request, 'auth/pages/404.html')

@login_required
class Week(View):
    """
        This view is used to load the skeleton for the weeks page.
        The actual content is loaded by the Records view in core/views.py.
    """
    def get(self, request, pk):
        context = getRecordSkeletonContext()
        try:
            week_spending = WeeklySpending.objects.get(user=request.user, id=pk)
            context.update(
                {
                    'pageHeading':f'{dateOnly(week_spending.week_start)} - {dateOnly(week_spending.week_end)}',
                    'extra_query_params': f'&week_id={pk}',
                }
            )
            return render(request, 'core/pages/week.html', context)
        except WeeklySpending.DoesNotExist:
            return render(request, 'auth/pages/404.html')
@login_required
class Day(View):
    def get(self, request: HttpRequest, date: str):
        """
            This view is used to load the skeleton for the day page.
            The actual content is loaded by the Records view in core/views.py.
        """
        
        context = getRecordSkeletonContext(card_count=1)
        context.update(
            {
                'pageHeading': dateOnly(date),
                'extra_query_params': f'&date={date}&seeDay=1',
            }
        )
        return render(request, 'core/pages/day.html', context)

class Weeks(View):
    """
        This view is used to load the skeleton for the weeks page.
        The actual content is loaded by the Records view in core/views.py.
    """
    def get(self, request):
        context = getRecordSkeletonContext()
        return render(request, 'core/pages/weeks.html', context)
       