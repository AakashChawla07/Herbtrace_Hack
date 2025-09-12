import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import BatchFactory, HerbSpeciesFactory, CollectorFactory

@pytest.mark.django_db
class TestTraceabilityAPI:
    
    def test_create_batch(self, authenticated_client):
        """Test batch creation"""
        species = HerbSpeciesFactory()
        collector = CollectorFactory()
        
        url = reverse('batch-list')
        data = {
            'species': species.id,
            'collector': collector.id,
            'collection_date': '2024-01-15T10:00:00Z',
            'collection_location': {
                'type': 'Point',
                'coordinates': [77.5946, 12.9716]
            },
            'quantity_kg': '25.500',
            'quality_grade': 'A',
            'harvesting_method': 'HAND_PICKED'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'batch_id' in response.data
    
    def test_batch_list(self, authenticated_client):
        """Test batch listing"""
        BatchFactory.create_batch(3)
        
        url = reverse('batch-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
    
    def test_batch_detail(self, authenticated_client):
        """Test batch detail view"""
        batch = BatchFactory()
        
        url = reverse('batch-detail', kwargs={'pk': batch.batch_id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['batch_id'] == batch.batch_id
        assert 'qr_code' in response.data
        assert 'sustainability_score' in response.data
    
    def test_batch_verification_public(self, api_client):
        """Test public batch verification"""
        batch = BatchFactory()
        
        url = reverse('batch-verify', kwargs={'pk': batch.batch_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['batch_id'] == batch.batch_id
    
    def test_batch_stats(self, authenticated_client):
        """Test batch statistics"""
        BatchFactory.create_batch(5)
        
        url = reverse('batch-stats')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_batches' in response.data
        assert 'species_distribution' in response.data
        assert 'sustainability_metrics' in response.data
    
    def test_nearby_collections(self, authenticated_client):
        """Test nearby collections search"""
        BatchFactory.create_batch(3)
        
        url = reverse('batch-nearby-collections')
        params = {
            'lat': 12.9716,
            'lng': 77.5946,
            'radius': 100
        }
        
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_200_OK
    
    def test_herb_species_crud(self, authenticated_client):
        """Test herb species CRUD operations"""
        # Create
        url = reverse('herbspecies-list')
        data = {
            'name': 'Test Herb',
            'scientific_name': 'Testus herbicus',
            'sanskrit_name': 'Test Aushadhi',
            'medicinal_properties': {'anti_inflammatory': True}
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        species_id = response.data['id']
        
        # Read
        detail_url = reverse('herbspecies-detail', kwargs={'pk': species_id})
        response = authenticated_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Herb'
        
        # Update
        data['name'] = 'Updated Herb'
        response = authenticated_client.put(detail_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Herb'
        
        # Delete
        response = authenticated_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
