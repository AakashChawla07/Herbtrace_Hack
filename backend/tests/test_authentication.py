import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:
    
    def test_user_registration(self, api_client):
        """Test user registration endpoint"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'COLLECTOR',
            'phone_number': '+1234567890'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
    
    def test_user_login(self, api_client, user_factory):
        """Test user login endpoint"""
        user = user_factory(username='testuser', password='testpass123')
        
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_user_profile(self, authenticated_client):
        """Test user profile endpoint"""
        url = reverse('profile')
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_client.user.username
    
    def test_password_change(self, authenticated_client):
        """Test password change endpoint"""
        url = reverse('change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password was changed
        authenticated_client.user.refresh_from_db()
        assert authenticated_client.user.check_password('newpass123')
    
    def test_api_key_creation(self, authenticated_client):
        """Test API key creation"""
        url = reverse('api_keys')
        data = {
            'name': 'Test API Key',
            'rate_limit_per_hour': 1000
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'key' in response.data
        assert response.data['name'] == 'Test API Key'
    
    def test_unauthorized_access(self, api_client):
        """Test that unauthorized requests are rejected"""
        url = reverse('profile')
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
