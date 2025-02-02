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
    def get_context(request):
        user = request.user
        products = ProductSerializer(user.products.all(), many=True).data
        dates = dc.collectDates(products)
        dates.sort(reverse=True)
        records = []
        
        # group the products by date
        for date in dates: 
            records.append(record(date, request)) # * Possible optimization: reduce database hits (try to use records2 function)
        
        # print(cache.get(f'records-{request.user.username}'))
        cache.set(f'records-{request.user.username}', records) # store records in a cache
        context = {
         'records': records, 
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
       