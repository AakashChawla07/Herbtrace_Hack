import pytest
from django.test import TransactionTestCase
from django.db import transaction
from tests.factories import BatchFactory, ProcessingEventFactory, QualityTestFactory
from blockchain.tasks import record_batch_on_blockchain

@pytest.mark.django_db
class TestIntegration:
    
    def test_complete_batch_lifecycle(self, authenticated_client):
        """Test complete batch lifecycle from creation to verification"""
        # Create batch
        batch = BatchFactory()
        
        # Add processing event
        processing_event = ProcessingEventFactory(batch=batch)
        
        # Add quality test
        quality_test = QualityTestFactory(batch=batch)
        
        # Verify batch can be retrieved with all related data
        from django.urls import reverse
        url = reverse('batch-detail', kwargs={'pk': batch.batch_id})
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data['processing_events']) == 1
        assert len(response.data['quality_tests']) == 1
        assert 'supply_chain_timeline' in response.data
        assert len(response.data['supply_chain_timeline']) >= 3  # Collection + Processing + Quality Test
    
    def test_batch_sustainability_scoring(self, authenticated_client):
        """Test sustainability score calculation"""
        batch = BatchFactory(
            harvesting_method='HAND_PICKED',
            quality_grade='A+',
            soil_health_score=9,
            regeneration_time_months=12
        )
        
        from django.urls import reverse
        url = reverse('batch-detail', kwargs={'pk': batch.batch_id})
        response = authenticated_client.get(url)
        
        sustainability_score = response.data['sustainability_score']
        assert sustainability_score > 70  # Should be high score for good practices
    
    def test_qr_code_generation(self, authenticated_client):
        """Test QR code generation for batches"""
        batch = BatchFactory()
        
        from django.urls import reverse
        url = reverse('batch-detail', kwargs={'pk': batch.batch_id})
        response = authenticated_client.get(url)
        
        assert 'qr_code' in response.data
        assert response.data['qr_code']  # Should contain base64 encoded QR code
    
    def test_geospatial_queries(self, authenticated_client):
        """Test geospatial functionality"""
        # Create batches at different locations
        BatchFactory(collection_location__x=77.5946, collection_location__y=12.9716)  # Bangalore
        BatchFactory(collection_location__x=72.8777, collection_location__y=19.0760)  # Mumbai
        
        from django.urls import reverse
        url = reverse('batch-nearby-collections')
        
        # Search near Bangalore
        response = authenticated_client.get(url, {
            'lat': 12.9716,
            'lng': 77.5946,
            'radius': 50  # 50km radius
        })
        
        assert response.status_code == 200
        # Should find the Bangalore batch but not Mumbai
        assert len(response.data['results']) >= 1
