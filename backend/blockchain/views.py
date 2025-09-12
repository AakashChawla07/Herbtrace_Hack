from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import BlockchainTransaction, SmartContract
from .serializers import BlockchainTransactionSerializer, SmartContractSerializer
from .services import blockchain_service
from .tasks import verify_batch_integrity_task
from traceability.models import Batch

class BlockchainTransactionListView(generics.ListAPIView):
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = BlockchainTransaction.objects.all()
        
        # Filter by batch if provided
        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        
        # Filter by transaction type
        tx_type = self.request.query_params.get('type')
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type)
        
        # Filter by status
        tx_status = self.request.query_params.get('status')
        if tx_status:
            queryset = queryset.filter(status=tx_status)
        
        return queryset.order_by('-created_at')

class BlockchainTransactionDetailView(generics.RetrieveAPIView):
    queryset = BlockchainTransaction.objects.all()
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'transaction_hash'

class SmartContractListView(generics.ListAPIView):
    queryset = SmartContract.objects.filter(is_active=True)
    serializer_class = SmartContractSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blockchain_status(request):
    """Get blockchain network status"""
    try:
        status_info = {
            'connected': blockchain_service.is_connected(),
            'latest_block': blockchain_service.w3.eth.block_number if blockchain_service.is_connected() else None,
            'gas_price_gwei': blockchain_service.get_gas_price() / 10**9 if blockchain_service.is_connected() else None,
            'account_address': blockchain_service.account.address if blockchain_service.account else None,
            'contracts_loaded': len(blockchain_service.contracts)
        }
        
        if blockchain_service.account and blockchain_service.is_connected():
            balance_wei = blockchain_service.w3.eth.get_balance(blockchain_service.account.address)
            status_info['account_balance_eth'] = float(balance_wei / 10**18)
        
        return Response(status_info)
        
    except Exception as e:
        return Response(
            {'error': f'Error getting blockchain status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_batch_integrity(request, batch_id):
    """Verify batch integrity against blockchain"""
    try:
        batch = get_object_or_404(Batch, batch_id=batch_id)
        
        # Run verification task asynchronously
        task = verify_batch_integrity_task.delay(batch_id)
        
        return Response({
            'message': 'Batch integrity verification started',
            'task_id': task.id,
            'batch_id': batch_id
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error starting verification: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blockchain_analytics(request):
    """Get blockchain analytics and statistics"""
    try:
        analytics = blockchain_service.get_blockchain_analytics()
        return Response(analytics)
        
    except Exception as e:
        return Response(
            {'error': f'Error getting blockchain analytics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_status(request, tx_hash):
    """Get detailed transaction status"""
    try:
        # Get from database first
        try:
            db_transaction = BlockchainTransaction.objects.get(transaction_hash=tx_hash)
            db_data = BlockchainTransactionSerializer(db_transaction).data
        except BlockchainTransaction.DoesNotExist:
            db_data = None
        
        # Get from blockchain
        blockchain_status = blockchain_service.get_transaction_status(tx_hash)
        
        response_data = {
            'transaction_hash': tx_hash,
            'database_record': db_data,
            'blockchain_status': blockchain_status
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': f'Error getting transaction status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_blockchain_sync(request, batch_id):
    """Force blockchain synchronization for a batch"""
    try:
        batch = get_object_or_404(Batch, batch_id=batch_id)
        
        # Check if already on blockchain
        if batch.blockchain_hash:
            return Response({
                'message': 'Batch already has blockchain hash',
                'blockchain_hash': batch.blockchain_hash
            })
        
        # Record on blockchain
        tx_hash = blockchain_service.record_collection_event(batch)
        
        if tx_hash:
            batch.blockchain_hash = tx_hash
            batch.save(update_fields=['blockchain_hash'])
            
            return Response({
                'message': 'Batch recorded on blockchain successfully',
                'transaction_hash': tx_hash,
                'batch_id': batch_id
            })
        else:
            return Response(
                {'error': 'Failed to record batch on blockchain'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': f'Error forcing blockchain sync: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
