from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import CustomUser
import re

# Regular Expressions for Validation
EMAIL_REGEX = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
USERNAME_REGEX = r'^[a-zA-Z0-9_]{4,32}$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

def is_valid(value, pattern):
    return bool(re.match(pattern, value))

def validate_user_data(**kwargs):
    validations = {
        'username': (USERNAME_REGEX, "Invalid username format"),
        'email': (EMAIL_REGEX, "Invalid email format"),
        'password': (PASSWORD_REGEX, "Weak password"),
        'bio': (lambda x: len(x) <= 500, "Bio cannot exceed 500 characters"),
        'gender': (lambda x: x in ['M', 'F', 'O'], "Invalid gender selection")
    }
    for field, (check, error) in validations.items():
        if field in kwargs and kwargs[field]:
            if isinstance(check, str) and not is_valid(kwargs[field], check):
                return error
            elif callable(check) and not check(kwargs[field]):
                return error
    
    if kwargs.get('profile_picture'):
        try:
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])(kwargs['profile_picture'].name)
        except ValidationError:
            return "Invalid file type. Only JPG, JPEG, PNG, GIF allowed."
    return None

def authenticate_user(identifier, password):
    user = CustomUser.objects.filter(email=identifier).first() or CustomUser.objects.filter(username=identifier).first()
    return authenticate(username=user.username, password=password) if user else None

@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        identifier, password = request.POST.get('username_or_email'), request.POST.get('password')
        if not identifier or not password:
            return render(request, 'account/login.html', {'error': 'Both fields are required'})
        
        user = authenticate_user(identifier, password)
        if not user:
            return render(request, 'account/login.html', {'error': 'Invalid credentials'})
        
        auth_login(request, user)
        return redirect('home')
    
    return render(request, 'account/login.html')

@require_http_methods(["GET"])
def logout(request):
    auth_logout(request)
    return redirect('home')

@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        data = {key: request.POST.get(key) for key in ['username', 'email', 'confirm_email', 'password', 'confirm_password', 'birth_date', 'gender', 'bio']}
        data['profile_picture'] = request.FILES.get('profile_picture')
        
        if data['email'] != data['confirm_email']:
            return render(request, 'account/register.html', {'error': "Emails do not match"})
        if data['password'] != data['confirm_password']:
            return render(request, 'account/register.html', {'error': "Passwords do not match"})
        
        error = validate_user_data(**data)
        if error:
            return render(request, 'account/register.html', {'error': error})
        
        user = CustomUser.objects.create_user(**{k: v for k, v in data.items() if k != 'confirm_email'})
        auth_login(request, user)
        return redirect('home')
    
    return render(request, 'account/register.html')

@login_required
@require_http_methods(["GET", "POST"])
def update_user(request):
    if request.method == 'GET':
        return render(request, 'account/update.html')
    
    user, updated_data = request.user, {k: request.POST.get(k) for k in ['username', 'email', 'password', 'birth_date', 'gender', 'bio']}
    updated_data['profile_picture'] = request.FILES.get('profile_picture')
    
    error = validate_user_data(**updated_data)
    if error:
        return render(request, 'account/update.html', {'error': error})
    
    for field, value in updated_data.items():
        if value:
            setattr(user, field, value if field != 'password' else user.set_password(value))
    
    user.save()
    return redirect('home')

@csrf_exempt
@require_http_methods(["POST"])
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    return JsonResponse({'message': 'User deactivated successfully!'}, status=200)

@login_required
@require_http_methods(["GET"])
def get_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return JsonResponse({field: getattr(user, field) for field in ['id', 'username', 'email', 'gender', 'birth_date', 'bio', 'date_joined', 'last_login']})

@require_http_methods(["GET"])
def get_users(request):
    return render(request, 'account/user_list.html', {'users': CustomUser.objects.values()})

@login_required
def get_this_user(request):
    return JsonResponse({field: getattr(request.user, field) for field in ['id', 'username', 'email', 'gender', 'birth_date', 'bio', 'date_joined', 'last_login']})



@require_http_methods(["GET", "POST"])
def filter_users(request):
    filters = {f"{key}__icontains": request.GET[key] for key in ['email', 'username', 'gender'] if request.GET.get(key)}
    users = CustomUser.objects.filter(**filters).values()
    return JsonResponse(list(users), safe=False) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'account/search_results.html', {'users': users})