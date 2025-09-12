from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import BlockchainTransaction
from .services import blockchain_service
from traceability.models import Batch, ProcessingEvent, QualityTest

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def record_batch_on_blockchain(self, batch_id):
    """Async task to record batch on blockchain"""
    try:
        batch = Batch.objects.get(batch_id=batch_id)
        tx_hash = blockchain_service.record_collection_event(batch)
        
        if tx_hash:
            batch.blockchain_hash = tx_hash
            batch.save(update_fields=['blockchain_hash'])
            logger.info(f"Batch {batch_id} recorded on blockchain: {tx_hash}")
        else:
            raise Exception("Failed to record batch on blockchain")
            
    except Exception as e:
        logger.error(f"Error recording batch {batch_id} on blockchain: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries reached for batch {batch_id}")

@shared_task(bind=True, max_retries=3)
def record_processing_on_blockchain(self, processing_event_id):
    """Async task to record processing event on blockchain"""
    try:
        processing_event = ProcessingEvent.objects.get(id=processing_event_id)
        tx_hash = blockchain_service.record_processing_event(processing_event)
        
        if tx_hash:
            processing_event.blockchain_hash = tx_hash
            processing_event.save(update_fields=['blockchain_hash'])
            logger.info(f"Processing event {processing_event_id} recorded on blockchain: {tx_hash}")
        else:
            raise Exception("Failed to record processing event on blockchain")
            
    except Exception as e:
        logger.error(f"Error recording processing event {processing_event_id} on blockchain: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries reached for processing event {processing_event_id}")

@shared_task(bind=True, max_retries=3)
def record_quality_test_on_blockchain(self, quality_test_id):
    """Async task to record quality test on blockchain"""
    try:
        quality_test = QualityTest.objects.get(id=quality_test_id)
        tx_hash = blockchain_service.record_quality_test(quality_test)
        
        if tx_hash:
            logger.info(f"Quality test {quality_test_id} recorded on blockchain: {tx_hash}")
        else:
            raise Exception("Failed to record quality test on blockchain")
            
    except Exception as e:
        logger.error(f"Error recording quality test {quality_test_id} on blockchain: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries reached for quality test {quality_test_id}")

@shared_task
def update_transaction_statuses():
    """Update pending blockchain transaction statuses"""
    pending_transactions = BlockchainTransaction.objects.filter(
        status='PENDING',
        created_at__gte=timezone.now() - timedelta(hours=24)  # Only check recent transactions
    )
    
    updated_count = 0
    for tx in pending_transactions:
        try:
            status_info = blockchain_service.get_transaction_status(tx.transaction_hash)
            
            if status_info['status'] != 'PENDING':
                tx.status = status_info['status']
                tx.block_number = status_info.get('block_number')
                tx.gas_used = status_info.get('gas_used')
                tx.transaction_fee = status_info.get('transaction_fee')
                
                if status_info['status'] == 'CONFIRMED':
                    tx.confirmed_at = timezone.now()
                    
                    # Update related model
                    if tx.transaction_type == 'COLLECTION':
                        Batch.objects.filter(batch_id=tx.batch_id).update(is_blockchain_verified=True)
                    elif tx.transaction_type == 'PROCESSING':
                        ProcessingEvent.objects.filter(
                            batch__batch_id=tx.batch_id,
                            blockchain_hash=tx.transaction_hash
                        ).update(is_blockchain_verified=True)
                
                tx.save()
                updated_count += 1
                
        except Exception as e:
            logger.error(f"Error updating transaction {tx.transaction_hash}: {e}")
    
    logger.info(f"Updated {updated_count} blockchain transaction statuses")
    return updated_count

@shared_task
def verify_batch_integrity_task(batch_id):
    """Async task to verify batch integrity against blockchain"""
    try:
        batch = Batch.objects.get(batch_id=batch_id)
        verification_result = blockchain_service.verify_batch_integrity(batch)
        
        if verification_result['verified']:
            logger.info(f"Batch {batch_id} integrity verified successfully")
        else:
            logger.warning(f"Batch {batch_id} integrity verification failed: {verification_result.get('error', 'Unknown error')}")
        
        return verification_result
        
    except Exception as e:
        logger.error(f"Error verifying batch {batch_id} integrity: {e}")
        return {'verified': False, 'error': str(e)}

@shared_task
def cleanup_old_transactions():
    """Clean up old failed transactions"""
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = BlockchainTransaction.objects.filter(
        status='FAILED',
        created_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old failed transactions")
    return deleted_count
