from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import User, APIKey, UserSession, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    APIKeySerializer, UserSessionSerializer
)
from .permissions import IsOwnerOrAdmin

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # TODO: Send verification email
        
        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Create user session
            user = User.objects.get(username=request.data.get('username'))
            
            # Get location if provided
            location = None
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            if lat and lng:
                location = Point(float(lng), float(lat), srid=4326)
            
            UserSession.objects.create(
                user=user,
                session_key=secrets.token_hex(20),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_info=request.data.get('device_info', {}),
                location=location
            )
            
            # Update last active
            user.last_active = timezone.now()
            user.save(update_fields=['last_active'])
        
        return response

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Create reset token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # TODO: Send password reset email
        
        return Response({
            'message': 'Password reset email sent successfully',
            'token': reset_token.token  # Remove this in production
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                used_at__isnull=True,
                expires_at__gt=timezone.now()
            )
            
            # Reset password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.used_at = timezone.now()
            reset_token.save()
            
            return Response({'message': 'Password reset successfully'})
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )

class APIKeyListCreateView(generics.ListCreateAPIView):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

class UserSessionListView(generics.ListAPIView):
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user and deactivate session"""
    # Deactivate current session
    session_key = request.data.get('session_key')
    if session_key:
        UserSession.objects.filter(
            user=request.user,
            session_key=session_key,
            is_active=True
        ).update(is_active=False, logout_time=timezone.now())
    
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request):
    """Verify user email with token"""
    token = request.data.get('token')
    user = request.user
    
    if user.verification_token == token:
        user.is_verified = True
        user.verification_token = ''
        user.save()
        return Response({'message': 'Email verified successfully'})
    
    return Response(
        {'error': 'Invalid verification token'},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user activity statistics"""
    user = request.user
    
    # Session stats
    sessions = UserSession.objects.filter(user=user)
    active_sessions = sessions.filter(is_active=True).count()
    total_sessions = sessions.count()
    
    # API key stats
    api_keys = APIKey.objects.filter(user=user)
    active_api_keys = api_keys.filter(is_active=True).count()
    total_api_usage = sum(key.usage_count for key in api_keys)
    
    stats = {
        'user_info': {
            'username': user.username,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'member_since': user.created_at,
            'last_active': user.last_active
        },
        'session_stats': {
            'active_sessions': active_sessions,
            'total_sessions': total_sessions,
            'last_login': sessions.first().login_time if sessions.exists() else None
        },
        'api_stats': {
            'active_api_keys': active_api_keys,
            'total_api_keys': api_keys.count(),
            'total_api_usage': total_api_usage
        }
    }
    
    return Response(stats)
