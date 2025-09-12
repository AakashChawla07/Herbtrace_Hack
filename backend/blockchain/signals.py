from django.db.models.signals import post_save
from django.dispatch import receiver
from traceability.models import Batch, ProcessingEvent, QualityTest
from .tasks import record_batch_on_blockchain, record_processing_on_blockchain, record_quality_test_on_blockchain

@receiver(post_save, sender=Batch)
def batch_created_handler(sender, instance, created, **kwargs):
    """Automatically record new batches on blockchain"""
    if created and not instance.blockchain_hash:
        # Delay blockchain recording to allow transaction to complete
        record_batch_on_blockchain.apply_async(
            args=[instance.batch_id],
            countdown=5  # Wait 5 seconds
        )

@receiver(post_save, sender=ProcessingEvent)
def processing_event_created_handler(sender, instance, created, **kwargs):
    """Automatically record processing events on blockchain"""
    if created and not instance.blockchain_hash:
        record_processing_on_blockchain.apply_async(
            args=[instance.id],
            countdown=5
        )

@receiver(post_save, sender=QualityTest)
def quality_test_created_handler(sender, instance, created, **kwargs):
    """Automatically record quality tests on blockchain"""
    if created:
        record_quality_test_on_blockchain.apply_async(
            args=[instance.id],
            countdown=5
        )
