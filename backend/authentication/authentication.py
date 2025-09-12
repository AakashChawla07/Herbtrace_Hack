from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication for API keys
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
            
            # Check if key is expired
            if key_obj.expires_at and key_obj.expires_at < timezone.now():
                raise AuthenticationFailed('API key expired')
            
            # Check IP restrictions
            if key_obj.allowed_ips:
                client_ip = request.META.get('REMOTE_ADDR')
                if client_ip not in key_obj.allowed_ips:
                    raise AuthenticationFailed('IP address not allowed')
            
            # Update usage stats
            key_obj.last_used = timezone.now()
            key_obj.usage_count += 1
            key_obj.save(update_fields=['last_used', 'usage_count'])
            
            return (key_obj.user, key_obj)
            
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
    
    def authenticate_header(self, request):
        return 'X-API-Key'
