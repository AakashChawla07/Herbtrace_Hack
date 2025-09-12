import pytest
from unittest.mock import Mock, patch
from django.urls import reverse
from rest_framework import status
from tests.factories import BatchFactory, BlockchainTransactionFactory

@pytest.mark.django_db
class TestBlockchainAPI:
    
    def test_blockchain_status(self, authenticated_client):
        """Test blockchain status endpoint"""
        url = reverse('blockchain_status')
        
        with patch('blockchain.services.blockchain_service.is_connected', return_value=True):
            with patch('blockchain.services.blockchain_service.w3.eth.block_number', 12345):
                response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'connected' in response.data
        assert 'latest_block' in response.data
    
    def test_blockchain_transactions_list(self, authenticated_client):
        """Test blockchain transactions listing"""
        BlockchainTransactionFactory.create_batch(3)
        
        url = reverse('blockchain_transactions')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
    
    def test_verify_batch_integrity(self, authenticated_client):
        """Test batch integrity verification"""
        batch = BatchFactory()
        
        url = reverse('verify_batch_integrity', kwargs={'batch_id': batch.batch_id})
        
        with patch('blockchain.tasks.verify_batch_integrity_task.delay') as mock_task:
            mock_task.return_value.id = 'test-task-id'
            response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'task_id' in response.data
        mock_task.assert_called_once_with(batch.batch_id)
    
    def test_force_blockchain_sync(self, authenticated_client):
        """Test force blockchain sync"""
        batch = BatchFactory(blockchain_hash='')
        
        url = reverse('force_blockchain_sync', kwargs={'batch_id': batch.batch_id})
        
        with patch('blockchain.services.blockchain_service.record_collection_event') as mock_record:
            mock_record.return_value = '0x123456789'
            response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'transaction_hash' in response.data
        
        batch.refresh_from_db()
        assert batch.blockchain_hash == '0x123456789'
    
    def test_blockchain_analytics(self, authenticated_client):
        """Test blockchain analytics endpoint"""
        url = reverse('blockchain_analytics')
        
        with patch('blockchain.services.blockchain_service.get_blockchain_analytics') as mock_analytics:
            mock_analytics.return_value = {
                'network_info': {'latest_block': 12345},
                'transaction_stats': {'total_transactions': 10},
                'cost_analytics': {'total_fees_eth': 0.1}
            }
            response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'network_info' in response.data
        assert 'transaction_stats' in response.data
