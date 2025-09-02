from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from .models import Example
from .middleware import jwt_login_required
import json
import jwt
from datetime import datetime, timedelta
import os

# JWT Secret Key (in production, use environment variable)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

def generate_jwt_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def hello(request):
    return JsonResponse({"message": "Hello from Django + Supabase"})

def list_examples(request):
    examples = list(Example.objects.values())
    return JsonResponse(examples, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """User registration endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validation
        if not all([username, email, password]):
            return JsonResponse({
                'status': 'error',
                'message': 'Username, email, and password are required'
            }, status=400)
        
        if len(password) < 8:
            return JsonResponse({
                'status': 'error',
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Username already exists'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Email already registered'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """User login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return JsonResponse({
                'status': 'error',
                'message': 'Username and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Generate JWT token
            token = generate_jwt_token(user)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'token': token
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """User logout endpoint"""
    try:
        logout(request)
        return JsonResponse({
            'status': 'success',
            'message': 'Logout successful'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def social_login(request):
    """Social login endpoint (Google, Facebook, etc.)"""
    try:
        data = json.loads(request.body)
        provider = data.get('provider')  # 'google', 'facebook', etc.
        social_id = data.get('social_id')
        email = data.get('email')
        name = data.get('name')
        
        if not all([provider, social_id, email]):
            return JsonResponse({
                'status': 'error',
                'message': 'Provider, social_id, and email are required'
            }, status=400)
        
        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user for social login
            username = f"{provider}_{social_id}"
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name or '',
                password=User.objects.make_random_password()
            )
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Social login successful',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'provider': provider,
                'token': token
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            'status': 'error',
            'message': 'User with this email already exists'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@jwt_login_required
def profile(request):
    """Get user profile (requires authentication)"""
    return JsonResponse({
        'status': 'success',
        'data': {
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined.isoformat()
        }
    })

def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        "status": "healthy",
        "service": "Django Backend",
        "timestamp": datetime.now().isoformat()
    })
