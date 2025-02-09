from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as logout_handler
from django.views.decorators.http import require_http_methods
from .models import CustomUser
import re

# Validation functions
def is_valid_password(password):
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password) is not None

def is_valid_email(email):
    regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def is_valid_username(username):
    regex = r'^[a-zA-Z0-9_]{4,32}$'
    return re.match(regex, username) is not None

# Helper function to authenticate with username or email
def get_authenticated_user(username_or_email, password):
    user = None
    if is_valid_email(username_or_email):
        try:
            user = CustomUser.objects.get(email=username_or_email)
            username_or_email = user.username  # Convert email to username for authentication
        except CustomUser.DoesNotExist:
            return None

    return authenticate(username=username_or_email, password=password)

# Helper function to validate registration input
def validate_registration_data(username, email, match_email, password, match_password, birth_date, gender, bio):
    if not all([username, email, match_email, password, match_password, birth_date, gender, bio]):
        return "All fields are required"

    if not is_valid_username(username):
        return "Invalid username format"

    if not is_valid_email(email):
        return "Invalid email format"

    if email != match_email:
        return "Emails do not match"

    if not is_valid_password(password):
        return "Weak password"

    if password != match_password:
        return "Passwords do not match"

    if gender not in ['M', 'F', 'O']:
        return "Invalid gender selection"

    if len(bio) > 500:
        return "Bio cannot exceed 500 characters"

    if CustomUser.objects.filter(username=username).exists():
        return "Username already exists"

    if CustomUser.objects.filter(email=email).exists():
        return "Email already registered"

    return None  # No errors

# Login view
@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated:
        return redirect('project:home')

    if request.method == 'GET':
        return render(request, 'account/login.html')

    username_or_email = request.POST.get('username') or request.POST.get('email')
    password = request.POST.get('password')

    if not username_or_email or not password:
        return render(request, 'account/login.html', {'error': 'Both fields are required'})

    user = get_authenticated_user(username_or_email, password)
    
    if user is None:
        return render(request, 'account/login.html', {'error': 'Invalid credentials'})

    auth_login(request, user)
    return redirect('project:home')

# Logout view
@require_http_methods(["GET"])
def logout(request):
    logout_handler(request)
    return redirect('project:home')

# Register view
@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('project:home')

    if request.method == 'GET':
        return render(request, 'account/register.html')

    username = request.POST.get('username')
    email = request.POST.get('email')
    match_email = request.POST.get('matchEmail')
    password = request.POST.get('password')
    match_password = request.POST.get('matchpassword')
    birth_date = request.POST.get('birth_date')
    gender = request.POST.get('gender')
    bio = request.POST.get('bio')

    error_message = validate_registration_data(username, email, match_email, password, match_password, birth_date, gender, bio)
    if error_message:
        return render(request, 'account/register.html', {'error': error_message})

    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        birth_date=birth_date,
        gender=gender,
        bio=bio
    )

    auth_login(request, user)
    return redirect('project:home')

# Update user view
@require_http_methods(["GET", "POST"])
def update_user(request):
    if not request.user.is_authenticated:
        return redirect('account:login')

    if request.method == 'GET':
        return render(request, 'account/update.html')

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    birth_date = request.POST.get('birth_date')
    gender = request.POST.get('gender')
    bio = request.POST.get('bio')
    profile_picture = request.FILES.get('profile_picture')

    error_message = validate_update_data(username, email, password, birth_date, gender, bio)
    if error_message:
        return render(request, 'account/update.html', {'error': error_message})

    user = request.user
    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.set_password(password)
    if birth_date:
        user.birth_date = birth_date
    if gender:
        user.gender = gender
    if bio:
        user.bio = bio
    if profile_picture:
        user.profile_picture = profile_picture

    user.save()
    return redirect('project:home')

# Helper function to validate update input
def validate_update_data(username, email, password, birth_date, gender, bio):
    if username and not is_valid_username(username):
        return "Invalid username format"

    if email and not is_valid_email(email):
        return "Invalid email format"

    if password and not is_valid_password(password):
        return "Weak password"

    if gender and gender not in ['M', 'F', 'O']:
        return "Invalid gender selection"

    if bio and len(bio) > 500:
        return "Bio cannot exceed 500 characters"

    return None  # No errors
