from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserCreationForm, UserAuthenticationForm
from django.contrib import messages 
from rest_framework import status
import json
from .schemas import UserModel
from .models import User

# Create your views here.
class SignUp(View):
    '''the signup view'''
    
    def get(self, request):
        '''returns the signup page'''
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = UserCreationForm()
        return render(request, 'auth/pages/signup.html', {'form': form})
    
    def post(self, request):
        '''creates a new user in the db'''
        form = UserCreationForm(data=request.POST)
        if form.is_valid(): 
            user = form.save()  
            login(request, user)
            messages.success(request,'Welcome to Xpense')
            return redirect('dashboard')
        else:
            print(form.errors.get_json_data())
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)  
            return render(request, 'auth/pages/signup.html', {'form': form})
            
            
            
class SignIn(View):
    '''the signin view'''
    
    def get(self, request):
        '''returns the signin page or automatically redirects the user if already logged in'''
        
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = UserAuthenticationForm()
        return render(request, 'auth/pages/signin.html', {'form': form}, status=status.HTTP_401_UNAUTHORIZED)
    
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
            else:
                messages.error(request, 'User not found, sign up')
        for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)        
        return render(request, 'auth/pages/signin.html', {'form': form})

            
class Logout(View):
    '''logout'''
    
    def get(self, request):
        '''logout a user'''
        logout(request)
        return redirect('signin')
    
def not_found_404(request, exception):
    '''404 page'''
    return render(request, 'auth/pages/404.html', {}, status=404)

class AuthCallback(View):
    '''Handles the OAuth callback from the authentication provider'''
    
    def get(self, request):
        '''Process the callback and redirect to the dashboard or signin page'''
        return render(request, 'auth/pages/callback.html')

    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        action = request.GET.get('action') # signup or singin
        if data:
            user = UserModel(**data.get('user'))
            if user.app_metadata.provider == 'google':
                return self.authenticate_with_google(request, user, action)
        messages.error(request, 'Authentication failed.')
        return JsonResponse({'message': 'error', 'redirect': '/signin/'}, status=status.HTTP_401_UNAUTHORIZED)

    def authenticate_with_google(self, request: HttpRequest, user: UserModel, action:str):
        '''Authenticate the user with Google and redirect to the dashboard'''
        if action == 'signin':
            django_user = User.objects.filter(email=user.email).first()
            if django_user:
                django_user.profile_picture = user.user_metadata.picture or None
                django_user.save()
                login(request, django_user)
                messages.success(request, 'Welcome back!')
                return JsonResponse({'message': 'success', 'redirect': '/dashboard/'})
            else:
                return self.authenticate_with_google(request, user, 'signup')

        if action == 'signup':
            django_user = User.objects.filter(email=user.email).first() # already existing user may attempt to signup again
            created = False
            if not django_user:
                django_user = self.create_user_from_google(user)
                created = True
            login(request, django_user)
            messages.success(request, 'Welcome to Xpense!')
            return JsonResponse({'message': 'success', 'redirect': '/dashboard/'}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        messages.error(request, 'Authentication failed.')
        return JsonResponse({'message': 'error', 'redirect': '/signin/'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def create_user_from_google(self, user: UserModel):
        '''Create a new user from Google data'''
        django_user = User.objects.create(
            username=user.email.split('@')[0] + '_google',
            email=user.email,
            profile_picture=user.user_metadata.picture or None,
            first_name=user.user_metadata.full_name or '',
            last_name='',
        )
        django_user.set_unusable_password()
        django_user.save()  # Save the user after setting unusable password
        return django_user