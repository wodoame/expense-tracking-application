from .views_dependencies import *
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
    
    @staticmethod
    def get_context(request, cachedData:list | None, paginator: dc.DateRangePaginator, page):
        if cachedData is None:
            cachedData = []
        user = request.user
        context = {}
        if page == paginator.get_total_pages(): 
            nextPageNumber = None
        else:
            nextPageNumber = page + 1
        dateRange = paginator.get_page_range(page)
        products = ProductSerializer(user.products.filter(date__date__range=(dateRange[1], dateRange[0])), many=True).data
        records = groupByDate(products)
        cachedData.append({
            'page': page, 
            'nextPageNumber': nextPageNumber, 
            'records': records
        })
        cache.set(f'records-{request.user.username}', cachedData) # store this page in the cache
        context = {
        'records': records, 
        'nextPageNumber':nextPageNumber
        }
        return context

@login_required
class Categories(View):
    def get(self, request):
        context = getCategoriesSkeletonContext()
        return render(request, 'core/pages/categories.html', context)

@login_required
class SeeProducts(View):
    def get(self, request, categoryName):
        user = request.user 
        try: 
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
       