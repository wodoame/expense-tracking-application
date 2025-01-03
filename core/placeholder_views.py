from .views_dependencies import *
@login_required
class Dashboard(View):
    def get(self, request):
        context = AllExpenditures.get_context(request)
        return render(request, 'core/placeholders/dashboard.html', context)
    
@login_required    
class AllExpenditures(View):
    def get(self, request):
        return render(request, 'core/placeholders/allExpenditures.html', self.get_context(request))
    
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
        
        context = {
         'records': records, 
         'categories': categories,
        }
        return context