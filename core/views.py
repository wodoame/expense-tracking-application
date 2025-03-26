from .views_dependencies import *

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

class Dashboard(View):
    def get(self, request):
        user = request.user
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        products = ProductSerializer(user.products.filter(date__date__gte=dateYesterday), many=True).data
        today = []
        yesterday = []
        for product in products:
            if dc.datefromisoformat(product.get('date')).date() == dateToday:
                today.append(product)
            else:
                yesterday.append(product)
        todayTotal = dc.get_total(today)
        yesterdayTotal = dc.get_total(yesterday)
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
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
        print(request.POST)
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            form = AddProductForm(self.check_category(request), instance=product)
            cedis = request.POST.get('cedis')
            pesewas = request.POST.get('pesewas')
            price = self.format_price(cedis, pesewas)
            parsedDate = datetime.strptime(request.POST.get('new-date'), '%Y-%m-%d')
            date = dc.datefromisoformat(request.POST.get('date')).date()
            dates = [date]
            if form.is_valid():
                product = form.save(commit=False)
                product.price = price
                product.user = request.user
                if parsedDate.date() != product.date.date():
                    product.date = timezone.make_aware(parsedDate, timezone.get_current_timezone())
                    dates.append(parsedDate.date())
                form.save() 
                messages.success(request, 'Product edited successfully')
                referer = request.META.get('HTTP_REFERER')
                path = urlparse(referer).path
                if re.match(r'^/categories/[^/]+/$', path):
                    segments = path.split('/')
                    categoryName = unquote(list(filter(lambda x: x != '', segments)).pop())
                    products = ProductSerializer(request.user.products.filter(category__name=categoryName, date__date__in=dates), many=True).data
                    items = [record2(date, products) for date in dates] 
                else: 
                    items = [record(date, request) for date in dates]
                context = {
                    'items':items, 
                    'showToast':True,
                    'edited':True
                }
                emitter.emit('products_updated', request)
                indexEventEmitter.emit('product_updated', ProductSerializer(product).data)
                return render(request, 'core/components/paginateExpenditures.html', context) 
            else: 
                errors = form.errors.get_json_data()
                print(errors) 
        except Product.DoesNotExist:
            messages.error(request, 'Product has been deleted')
        return redirect(request.META.get('HTTP_REFERER'))
    
    def handle_add_product(self, request: HttpRequest):
        print(request.POST)
        form = AddProductForm(self.check_category(request))
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = self.format_price(cedis, pesewas)
        parsedDate = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
        dateToday = datetime.today().date()
        if form.is_valid():
            product = form.save(commit=False)
            product.price = price
            product.user = request.user
            if parsedDate.date() != dateToday:
                product.date = timezone.make_aware(parsedDate, timezone.get_current_timezone())
            form.save()
            emitter.emit('products_updated', request)
            indexEventEmitter.emit('product_updated', ProductSerializer(product).data)
            messages.success(request, 'Product added successfully')
        else: 
            errors = form.errors.get_json_data()
            print(errors)
        referer = request.META.get('HTTP_REFERER')
        path = urlparse(referer).path
        print('the path is', path)
        if path == '/all-expenditures/':
            return redirect('/components/records/?page=1&addProduct=1')
        if path == '/dashboard/':
            return redirect('implemented-dashboard')
        if path == '/categories/':
            return redirect('implemented-categories')
        if re.match(r'^/categories/[^/]+/$', path):
           segments = path.split('/')
           categoryName = unquote(list(filter(lambda x: x != '', segments)).pop())
           return redirect(f'/components/records/?addProduct=1?&oneCategory=1&categoryName={categoryName}')
        return render(request, 'core/components/toastWrapper.html', {})
        
    
    def handle_delete_product(self, request):
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            indexEventEmitter.emit('product_updated', ProductSerializer(product).data, method='delete')
            product.delete()
            messages.success(request, 'Product deleted successfully')
            date = dc.datefromisoformat(request.POST.get('date')).date() 
            referer = request.META.get('HTTP_REFERER')
            path = urlparse(referer).path
            if re.match(r'^/categories/[^/]+/$', path):
                segments = path.split('/')
                categoryName = list(filter(lambda x: x != '', segments)).pop()
                products = ProductSerializer(request.user.products.filter(category__name=categoryName, date__date=date), many=True).data
                items = [record2(date, products)] 
            else:
                items = [record(date, request)]
            context = {
                'items':items,
                'showToast':True,
            }
            emitter.emit('products_updated', request)
            if not items[0].get('products'):
                return render(request, 'core/components/toastWrapper/toastWrapper.html', context) # return toastWrapper.html so that the success message will be displayed
            return render(request, 'core/components/paginateExpenditures.html', context) 
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')

class ActivityCalendar(View):
    def get(self, request): 
        response = cache.get(f'activity-calendar-{request.user.username}')
        if response:
            return response
        monthsData = dc.get_activity_in_last_year(request)
        context = {
            'monthsData': monthsData, 
        }
        response = render(request, 'core/components/activityCalendar.html', context)
        cache.set(f'activity-calendar-{request.user.username}', response)
        return response

# @login_required    
class Records(View):
    def get(self, request): 
        records = []
        data = {}
        nextPageNumber = None
        user = request.user 
        if request.GET.get('oneCategory'):
            categoryName = unquote(request.GET.get('categoryName'))
            print(request.GET)
            if categoryName != 'None':
                products = ProductSerializer(user.products.filter(category__name=categoryName), many=True).data
            else: 
                products = ProductSerializer(user.products.filter(category=None), many=True).data
            records = groupByDate(products)
        else:
            previousData: list[dict] = cache.get(f'records-{request.user.username}') # ! BUG: if user has no product stored in the cache, the data will be None which will cause bug
            numberOfDays = 7
            paginator = dc.DateRangePaginator(user.date_joined.date(), datetime.today().date(), numberOfDays, reverse=True)
            if previousData is None or (previousData is not None and int(request.GET.get('page')) > len(previousData)):
                page = int(request.GET.get('page'))
                data = AllExpenditures.get_context(request, previousData, paginator, page)
                records = data.get('records')
                nextPageNumber = data.get('nextPageNumber')
            else: 
                print('cached upto page', len(previousData))
                html = ''
                for item in previousData:
                    html += render_to_string('core/components/paginateExpenditures.html', {'items': item.get('records')})
                if len(previousData) < paginator.get_total_pages(): # len(previousData) is  the number of pages cached so far
                    nextPageNumber = len(previousData) + 1
                    print(nextPageNumber)
                    extraContext = getRecordSkeletonContext()
                    extraContext.update({'nextPageNumber':nextPageNumber})
                    html += render_to_string('core/components/paginator.html', extraContext)
                if request.GET.get('addProduct'): # if page reloads due to adding a products display a message
                    html += render_to_string('core/components/toastWrapper.html')
                return HttpResponse(html)
    
        context = {
            'items':records, 
            'nextPageNumber':nextPageNumber,
            'seeProductsPage': request.GET.get('addProduct')
            }
        context.update(getRecordSkeletonContext())
        return render(request, 'core/components/paginateExpenditures.html', context)
    
# @login_required
class Settings(View): 
    def get(self, request):
        return render(request, 'core/pages/settings.html')


class Test(View):
    def get(self, request): 
        context = {}
        # cache.clear()
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
                  '/statSummarySkeleton/': render_to_string('core/components/statSummarySkeleton.html'), 
                  '/categories/category-name/': render_to_string('core/placeholders/seeProductsSkeleton.html',getRecordSkeletonContext()),
                  'seeProductsSkeleton': render_to_string('core/placeholders/seeProductsSkeleton2.html',getRecordSkeletonContext()),
                  '/search/': render_to_string('core/components/staticRecordSkeleton2.html', getRecordSkeletonContext()),
                }
            )
        return render(request, 'core/components/blank.html', context)


class Categories(View):
    def get(self, request):
        user = request.user
        categories = CategorySerializerWithMetrics(user.categories.all(), many=True).data
        productsWithNoCategory = ProductPriceSerializer(user.products.filter(category=None), many=True).data
        df = pd.DataFrame(productsWithNoCategory)
        metrics = {
            "product_count": 0, 
            "total_amount_spent": 0
        }
        if not df.empty:
            # NOTE: explicitly convert to the respective data types since the original result from pandas is an object
            metrics['product_count'] = int(df.get('name').count())
            metrics['total_amount_spent'] = float(df.get('price').sum())
        categories.append(
            {
                "name": "None",
                "metrics": metrics
            }
        )
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
            emitter.emit('products_updated', request)
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
            emitter.emit('products_updated', request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return redirect('implemented-categories')
    
    def handle_delete_category(self, request): 
        categoryId = request.POST.get('id')
        try:
            Category.objects.get(id=categoryId).delete()
            messages.success(request, 'Category deleted successfully')
            emitter.emit('products_updated', request) # some products may still be associated with the deleted category so the cache must be cleared
        except Product.DoesNotExist:
            messages.error(request, 'Category already deleted')
        return redirect('implemented-categories')
    
class StatSummary(View):
    def get(self, request):
        stats = None
        user = request.user
        if request.GET.get('type') == 'weekly':
            stats = cache.get(f'weekly-stats-{user.username}')
            if not stats:
                products = getAllProductsFromCache(user)
                stats = Context(WeeklyStats(products, user)).apply()
                cache.set(f'weekly-stats-{user.username}', stats)
        if request.GET.get('type') == 'monthly':
            stats = cache.get(f'monthly-stats-{user.username}')
            if not stats:
                products = getAllProductsFromCache(user)
                stats = Context(MonthlyStats(products, user)).apply()
                cache.set(f'monthly-stats-{user.username}', stats)  
        context = {
            'stats':stats
        }
        return render(request, 'core/components/statSummary.html', context)
class Search(View):
    def get(self, request):
        return render(request, 'core/pages/search-results.html')
        
class SearchResults(View):
    def get(self, request):
        print(request.GET)
        query = request.GET.get('query').strip()
        user = request.user 
        data = APISearch.search_products(query, user)
        context = {
            'results': data.get('results')
        }
        return render(request, 'core/components/searchResults.html', context)
        