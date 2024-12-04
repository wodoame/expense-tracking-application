from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserCreationForm, UserAuthenticationForm
# Create your views here.
class SignUp(View):
    '''the signup view'''
    
    def get(self, request):
        '''returns the signup page'''
        form = UserCreationForm()
        return render(request, 'auth/pages/signup.html', {'form': form})
    
    def post(self, request):
        '''creates a new user in the db'''
        form = UserCreationForm(data=request.POST)
        if form.is_valid(): 
            user = form.save()  
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'auth/pages/signup.html', {'form': form})
            
            
            
class SignIn(View):
    '''the signin view'''
    
    def get(self, request):
        '''returns the signin page or automatically redirects the user if already logged in'''
        
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = UserAuthenticationForm()
        return render(request, 'auth/pages/signin.html', {'form': form})
    
    def post(self, request):
        '''creates a new user in the db'''
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            
class Logout(View):
    '''logout'''
    
    def get(self, request):
        '''logout a user'''
        logout(request)
        return redirect('signin')