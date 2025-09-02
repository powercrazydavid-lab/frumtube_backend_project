from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello),
    path('examples/', views.list_examples),
    path('auth/signup/', views.signup),
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/social/', views.social_login),
    path('auth/profile/', views.profile),
    path('health/', views.health_check),
]
