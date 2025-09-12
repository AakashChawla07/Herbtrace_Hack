import pytest
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.cache import cache
from tests.factories import BatchFactory, UserFactory
import time

@pytest.mark.django_db
class TestPerformance:
    
    def test_batch_list_performance(self, authenticated_client):
        """Test batch list endpoint performance with large dataset"""
        # Create 100 batches
        BatchFactory.create_batch(100)
        
        from django.urls import reverse
        url = reverse('batch-list')
        
        start_time = time.time()
        response = authenticated_client.get(url)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 2.0  # Should complete within 2 seconds
    
    def test_batch_stats_caching(self, authenticated_client):
        """Test that batch stats are properly cached"""
        BatchFactory.create_batch(50)
        
        from django.urls import reverse
        url = reverse('batch-stats')
        
        # First request
        start_time = time.time()
        response1 = authenticated_client.get(url)
        first_request_time = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = authenticated_client.get(url)
        second_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        # Second request should be significantly faster due to caching
        assert second_request_time < first_request_time * 0.5
    
    def test_database_query_optimization(self, authenticated_client):
        """Test that database queries are optimized"""
        BatchFactory.create_batch(10)
        
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            from django.urls import reverse
            url = reverse('batch-list')
            
            # Reset query count
            connection.queries_log.clear()
            
            response = authenticated_client.get(url)
            
            # Should use select_related/prefetch_related to minimize queries
            query_count = len(connection.queries)
            assert query_count < 10  # Should be efficient with joins
            assert response.status_code == 200
