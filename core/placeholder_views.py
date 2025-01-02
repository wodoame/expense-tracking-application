from .views_dependencies import *
@login_required
class Dashboard(View):
    def get(self, request):
        user = request.user
        categories = CategorySerializer(user.categories.all(), many=True).data
        context = {'categories': categories}
        return render(request, 'core/placeholders/dashboard.html', context)
    
@login_required    
class AllExpenditures(View):
    def get(self, request):
        user = request.user
        categories = CategorySerializer(user.categories.all(), many=True).data
        context = {'categories': categories}
        return render(request, 'core/placeholders/allExpenditures.html', context)