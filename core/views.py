from .serializers import CategorySerializerWithMetrics
from .views_dependencies import *

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

@login_required
class Dashboard(View):
    def get(self, request):
        user = request.user
        products = ProductSerializer(user.products.all(), many=True).data
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        statContext = Context(WeeklyStats(products, request.user))
        stats = statContext.apply() 
        today = [product for product in products if dc.datefromisoformat(product.get('date')).date() == dateToday]
        yesterday = [product for product in products if dc.datefromisoformat(product.get('date')).date() == dateYesterday]
        todayTotal = dc.get_total(today)
        yesterdayTotal = dc.get_total(yesterday)
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
            'stats': stats,
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal,
        }
        return render(request, 'core/implementations/dashboard.html', context)
    
    def post(self, request):
        if request.GET.get('edit'): 
            return self.handle_edit_product(request)
        if request.GET.get('delete'):
            return self.handle_delete_product(request)
        return self.handle_add_product(request)
        
    def check_category(self, request):
        categoryId = request.POST.get('category')
        
        if categoryId != '' and int(categoryId) == 0:
            category = Category.objects.create(name=request.POST.get('newCategoryName'), user=request.user)
            postDict = request.POST.dict()
            postDict['category'] = category.id
            return postDict
        return request.POST
    
    def format_price(self, cedis, pesewas):
        if len(pesewas) == 1:
            pesewas = '0' + pesewas
        price = float(cedis + '.' + pesewas)
        return price 
    
        
    def handle_edit_product(self, request):
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            form = AddProductForm(self.check_category(request), instance=product)
            cedis = request.POST.get('cedis')
            pesewas = request.POST.get('pesewas')
            price = self.format_price(cedis, pesewas)
            if form.is_valid():
                product = form.save(commit=False)
                product.price = price
                product.user = request.user
                form.save() 
                messages.success(request, 'Product edited successfully')
                date = dc.datefromisoformat(request.POST.get('date')).date() 
                items = [record(date, request)]
                context = {
                    'items':items
                }
                Records.invalidate_cache(request)
                return render(request, 'core/components/paginateExpenditures.html', context) 
            else: 
                errors = form.errors.get_json_data()
                print(errors) 
        except Product.DoesNotExist:
            messages.error(request, 'Product has been deleted')
        return redirect(request.META.get('HTTP_REFERER'))
    
    def handle_add_product(self, request: HttpRequest):
        form = AddProductForm(self.check_category(request))
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = self.format_price(cedis, pesewas)
        if form.is_valid():
            product = form.save(commit=False)
            product.price = price
            product.user = request.user
            form.save()
            Records.invalidate_cache(request) # remove records from cache
            messages.success(request, 'Product added successfully')
        else: 
            errors = form.errors.get_json_data()
            print(errors)
        referer = request.META.get('HTTP_REFERER')
        path = urlparse(referer).path
        if path == '/all-expenditures/':
            return redirect('/components/records/')
        if path == '/dashboard/':
            return redirect('implemented-dashboard')
        if path == '/categories/':
            return redirect('implemented-categories')
        return redirect(referer)
        
    
    def handle_delete_product(self, request):
        productId = request.POST.get('id')
        try:
            Product.objects.get(id=productId).delete()
            messages.success(request, 'Product deleted successfully')
            date = dc.datefromisoformat(request.POST.get('date')).date() 
            items = [record(date, request)]
            context = {
                'items':items
            }
            Records.invalidate_cache(request) 
            if not items[0].get('products'):
                return render(request, 'core/components/toastWrapper/toastWrapper.html', context) # return toastWrapper.html so that the success message will be displayed
            return render(request, 'core/components/paginateExpenditures.html', context) 
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')
# @login_required    
class ActivityCalendar(View):
    def get(self, request): 
        monthsData = dc.get_activity_in_last_year(request)
        context = {
            'monthsData': monthsData, 
        }
        return render(request, 'core/components/activityCalendar.html', context)

# @login_required    
class Records(View):
    def get(self, request): 
        records = cache.get(f'records-{request.user.username}')
        if not records:
            records = AllExpenditures.get_context(request).get('records')
            cache.set(f'records-{request.user.username}', records)
             
        pageNumber = request.GET.get('page')
        if not pageNumber:
            pageNumber = 1
        paginator = Paginator(records, 7)
        page = paginator.page(pageNumber)
        nextPageNumber = None
        if page.has_next(): 
            nextPageNumber = page.next_page_number()
        items = page.object_list
        context = {
            'items':items, 
            'nextPageNumber':nextPageNumber,
            }
        context.update(getRecordSkeletonContext())
        return render(request, 'core/components/paginateExpenditures.html', context)
    @staticmethod
    def invalidate_cache(request):
        cache.delete(f'records-{request.user.username}')
    
# @login_required
class Settings(View): 
    def get(self, request):
        return render(request, 'core/pages/settings.html')

# @login_required
class Test(View):
    def get(self, request): 
        context = {'row_count': range(5)}
        return render(request, 'core/pages/test.html', context)
    
    def post(self, request): 
       pass


class Routes(View): 
    def get(self, request): 
        context = {}
        if request.GET.get('all'):
            return JsonResponse(
                {
                  '/dashboard/': render_to_string('core/placeholders/dashboardSkeleton.html', getRecordSkeletonContext()),
                  '/all-expenditures/': render_to_string('core/placeholders/allExpendituresSkeleton.html', getRecordSkeletonContext()),
                  '/categories/': render_to_string('core/placeholders/categoriesPageSkeleton.html', getCategoriesSkeletonContext()),
                  '/statSummarySkeleton/': render_to_string('core/components/statSummarySkeleton.html')
                }
            )
        return render(request, 'core/components/blank.html', context)


class Categories(View):
    def get(self, request):
        user = request.user
        categories = CategorySerializerWithMetrics(user.categories.all(), many=True).data
        categories.sort(key=lambda x:x['metrics']['total_amount_spent'], reverse=True)
        context = {
            'categories': categories
        }
        return render(request, 'core/implementations/categories.html', context)
    
    def post(self, request):
        if request.GET.get('edit'):
            return self.handle_edit_category(request)
        if request.GET.get('delete'):
            return self.handle_delete_category(request)
        return self.handle_add_category(request)
       
    def handle_add_category(self, request): 
        user = request.user
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = user
            category.save()
            messages.success(request, 'Category added successfully')
            Records.invalidate_cache(request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return redirect('implemented-categories')
    
    def handle_edit_category(self, request): 
        categoryId = request.POST.get('id')
        category = Category.objects.get(id=categoryId)
        form = AddCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            messages.success(request, 'Category edited successfully')
            Records.invalidate_cache(request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return redirect('implemented-categories')
    
    def handle_delete_category(self, request): 
        categoryId = request.POST.get('id')
        try:
            Category.objects.get(id=categoryId).delete()
            messages.success(request, 'Category deleted successfully')
            Records.invalidate_cache(request) # some products may still be associated with the deleted category so the cache must be cleared
        except Product.DoesNotExist:
            messages.error(request, 'Category already deleted')
        return redirect('implemented-categories')
    
class StatSummary(View):
    def get(self, request):
        stats = None
        user = request.user
        products = ProductSerializer(user.products.all(), many=True).data
        if request.GET.get('type') == 'weekly':
            stats = Context(WeeklyStats(products, request.user)).apply()
        if request.GET.get('type') == 'monthly':
            stats = Context(MonthlyStats(products, request.user)).apply() 
        context = {
            'stats':stats
        }
        return render(request, 'core/components/statSummary.html', context)
        
        