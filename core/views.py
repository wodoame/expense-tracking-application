from .views_dependencies import * 
class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

@login_required
class Dashboard(View):
    def get(self, request):
        # asyncio.run(asyncio.sleep(3))
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
            'totalSpentThisWeek': stats[0],
            'totalSpentLastWeek': stats[1],
            'highestWeeklySpending': stats[2],
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal,
        }
        return render(request, 'core/routes/fakeDashboard.html', context)
    
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
    
        
    def handle_edit_product(self, request):
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            form = AddProductForm(self.check_category(request), instance=product)
            cedis = request.POST.get('cedis')
            pesewas = request.POST.get('pesewas')
            price = float(cedis + '.' + pesewas)
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
        price = float(cedis + '.' + pesewas)
        if form.is_valid():
            product = form.save(commit=False)
            product.price = price
            product.user = request.user
            form.save()
            messages.success(request, 'Product added successfully')
        else: 
            errors = form.errors.get_json_data()
            print(errors)
        return redirect(request.META.get('HTTP_REFERER'))
    
    def handle_delete_product(self, request):
        print(request.POST)
        productId = request.POST.get('id')
        try:
            Product.objects.get(id=productId).delete()
            messages.success(request, 'Product deleted successfully')
            date = dc.datefromisoformat(request.POST.get('date')).date() 
            items = [record(date, request)]
            context = {
                'items':items
            }
            if not items[0].get('products'):
                return render(request, 'core/components/toastWrapper/toastWrapper.html', context) # return toastWrapper.html so that the success message will be displayed
            return render(request, 'core/components/paginateExpenditures.html', context) 
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return redirect(request.META.get('HTTP_REFERER'))
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
    def post(self, request):
        # I'm sending the data through the request instead of calling the database again
        # will be replaced with a caching system
        records = json.loads(request.POST.get('records'))
        pageNumber = request.GET.get('page')
        paginator = Paginator(records, 4)
        page = paginator.page(pageNumber)
        nextPageNumber = None
        if page.has_next(): 
            nextPageNumber = page.next_page_number()
        items = page.object_list
        context = {
            'items':items, 
            'nextPageNumber':nextPageNumber,
            'row_count': range(5),
            'card_count': range(5)
            }
        return render(request, 'core/components/paginateExpenditures.html', context)
    
# @login_required
class Settings(View): 
    def get(self, request):
        return render(request, 'core/pages/settings.html')
# @login_required
class CategoriesPage(View): 
    def get(self, request):
        user = request.user
        categories = CategorySerializer(user.categories.all(), many=True).data
        productsWithNoCategory = Product.objects.filter(category=None)
        context = {
            'categories': categories + [{'name': 'Uncategorized', 'product_count': productsWithNoCategory.count()}], 
        }
        return render(request, 'core/pages/categories.html', context)
    

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
                  '/all-expenditures/': render_to_string('core/placeholders/allExpendituresSkeleton.html', getRecordSkeletonContext())
                }
            )
        return render(request, 'core/components/blank.html', context)
        
    
        