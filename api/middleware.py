import jwt
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
import os

# JWT Secret Key (in production, use environment variable)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add user to request if JWT token is valid
        request.user = self.get_user_from_token(request)
        return self.get_response(request)

    def get_user_from_token(self, request):
        """Extract user from JWT token in Authorization header"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id:
                return User.objects.get(id=user_id)
                
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except User.DoesNotExist:
            return None
        
        return None

def jwt_login_required(view_func):
    """Custom decorator for JWT authentication"""
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
