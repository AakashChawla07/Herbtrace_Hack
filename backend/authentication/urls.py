from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('api/v1/auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/v1/auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/logout/', views.logout_view, name='logout'),
    
    # User profile
    path('api/v1/auth/profile/', views.UserProfileView.as_view(), name='profile'),
    path('api/v1/auth/verify-email/', views.verify_email, name='verify_email'),
    path('api/v1/auth/stats/', views.user_stats, name='user_stats'),
    
    # Password management
    path('api/v1/auth/change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('api/v1/auth/reset-password/', views.PasswordResetRequestView.as_view(), name='reset_password'),
    path('api/v1/auth/reset-password/confirm/', views.PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    
    # API keys
    path('api/v1/auth/api-keys/', views.APIKeyListCreateView.as_view(), name='api_keys'),
    path('api/v1/auth/api-keys/<int:pk>/', views.APIKeyDetailView.as_view(), name='api_key_detail'),
    
    # Sessions
    path('api/v1/auth/sessions/', views.UserSessionListView.as_view(), name='sessions'),
]
