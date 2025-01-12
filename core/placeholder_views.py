from .serializers import CategorySerializerWithMetrics
from .views_dependencies import *
@login_required
class Dashboard(View):
    def get(self, request):
        context = getRecordSkeletonContext()
        context.update(AllExpenditures.get_context(request))
        return render(request, 'core/pages/dashboard.html', context)
    
@login_required    
class AllExpenditures(View):
    def get(self, request):
        context = getRecordSkeletonContext()
        context.update(self.get_context(request))
        return render(request, 'core/pages/allExpenditures.html', context)
    
    @staticmethod
    def get_context(request):
        user = request.user
        products = ProductSerializer(user.products.all(), many=True).data
        categories = CategorySerializer(user.categories.all(), many=True).data
        dates = dc.collectDates(products)
        dates.sort(reverse=True)
        records = []
        
        # group the products by date
        for date in dates: 
            records.append(record(date, request))
        
        # print(cache.get(f'records-{request.user.username}'))
        cache.set(f'records-{request.user.username}', records) # store records in a cache
        context = {
         'records': records, 
         'categories': categories,
        }
        return context

@login_required
class Categories(View):
    def get(self, request):
        user = request.user
        context = getCategoriesSkeletonContext()
        return render(request, 'core/pages/categories.html', context)