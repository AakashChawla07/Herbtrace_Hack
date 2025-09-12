import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    """API client for testing"""
    return APIClient()

@pytest.fixture
def user_factory():
    """Factory for creating test users"""
    def create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'COLLECTOR',
            'is_verified': True
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(password=password, **defaults)
        return user
    return create_user

@pytest.fixture
def authenticated_client(api_client, user_factory):
    """API client with authenticated user"""
    user = user_factory()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    return api_client

@pytest.fixture
def admin_client(api_client, user_factory):
    """API client with admin user"""
    user = user_factory(user_type='ADMIN', is_staff=True, is_superuser=True)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    return api_client

@pytest.fixture
def sample_location():
    """Sample GPS location"""
    return Point(77.5946, 12.9716, srid=4326)  # Bangalore coordinates
